import sys
import re
import os
import requests
import json
from env import *
from pathlib import Path
import shutil
import platform

if "VIRTUAL_ENV" in os.environ:
    HOME_DIR = Path(os.environ["VIRTUAL_ENV"])
else:
    HOME_DIR = Path.home()
SOLC_PARSER_DIR = HOME_DIR.joinpath(".solc-parser")
SOLC_BINARIES_DIR = SOLC_PARSER_DIR.joinpath("bin")
SOLC_SYMLINK = SOLC_BINARIES_DIR / "solc"


class Version:
    """Semantic version implementation following npm semver rules"""
    
    def __init__(self, major, minor, patch, prerelease=None, build=None):
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        self.prerelease = prerelease
        self.build = build
    
    @classmethod
    def parse(cls, version_string):
        """Parse version string into Version object"""
        # Remove build metadata for parsing
        if '+' in version_string:
            version_string, build = version_string.split('+', 1)
        else:
            build = None
            
        # Handle prerelease
        if '-' in version_string:
            version_part, prerelease = version_string.split('-', 1)
        else:
            version_part = version_string
            prerelease = None
            
        # Parse version numbers
        parts = version_part.split('.')
        if len(parts) < 3:
            parts.extend(['0'] * (3 - len(parts)))
        
        major, minor, patch = parts[:3]
        return cls(major, minor, patch, prerelease, build)
    
    def __str__(self):
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            result += f"-{self.prerelease}"
        if self.build:
            result += f"+{self.build}"
        return result
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            other = Version.parse(str(other))
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.prerelease == other.prerelease)
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            other = Version.parse(str(other))
        
        # Compare major.minor.patch
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        
        # Handle prerelease comparison
        if self.prerelease is None and other.prerelease is not None:
            return False  # No prerelease > prerelease
        if self.prerelease is not None and other.prerelease is None:
            return True   # prerelease < no prerelease
        if self.prerelease == other.prerelease:
            return False
        
        # Compare prerelease parts
        return self._compare_prerelease(self.prerelease, other.prerelease)
    
    def _compare_prerelease(self, pre1, pre2):
        """Compare prerelease strings"""
        parts1 = pre1.split('.') if pre1 else []
        parts2 = pre2.split('.') if pre2 else []
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else None
            p2 = parts2[i] if i < len(parts2) else None
            
            if p1 is None:
                return True   # shorter prerelease < longer
            if p2 is None:
                return False  # longer prerelease > shorter
            
            # Try to compare as numbers first
            try:
                num1, num2 = int(p1), int(p2)
                if num1 != num2:
                    return num1 < num2
            except ValueError:
                # Compare as strings
                if p1 != p2:
                    return p1 < p2
        
        return False
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other


class VersionRange:
    """Version range implementation following npm semver rules"""
    
    def __init__(self, ranges):
        self.ranges = ranges  # List of comparators
    
    @classmethod
    def parse(cls, range_string):
        """Parse version range string"""
        # Handle logical OR (||)
        if '||' in range_string:
            or_ranges = [r.strip() for r in range_string.split('||')]
            return cls._parse_or_ranges(or_ranges)
        
        # Handle hyphen ranges (1.2.3 - 2.3.4)
        if ' - ' in range_string:
            return cls._parse_hyphen_range(range_string)
        
        # Handle caret ranges (^1.2.3)
        if range_string.startswith('^'):
            return cls._parse_caret_range(range_string)
        
        # Handle tilde ranges (~1.2.3)
        if range_string.startswith('~'):
            return cls._parse_tilde_range(range_string)
        
        # Handle x-ranges (1.2.x, 1.x, *, 0.8.*)
        if 'x' in range_string.lower() or '*' in range_string:
            return cls._parse_x_range(range_string)
        
        # Handle simple comparators
        return cls._parse_simple_range(range_string)
    
    @classmethod
    def _parse_or_ranges(cls, or_ranges):
        """Parse logical OR ranges"""
        ranges = []
        for range_str in or_ranges:
            if range_str.strip():
                ranges.extend(cls.parse(range_str.strip()).ranges)
        return cls(ranges)
    
    @classmethod
    def _parse_hyphen_range(cls, range_string):
        """Parse hyphen range (1.2.3 - 2.3.4)"""
        start, end = range_string.split(' - ', 1)
        start_ver = Version.parse(start.strip())
        end_ver = Version.parse(end.strip())
        
        ranges = [
            {'operator': '>=', 'version': start_ver},
            {'operator': '<=', 'version': end_ver}
        ]
        return cls(ranges)
    
    @classmethod
    def _parse_caret_range(cls, range_string):
        """Parse caret range (^1.2.3)"""
        version_str = range_string[1:].strip()
        version = Version.parse(version_str)
        
        if version.major == 0:
            if version.minor == 0:
                # ^0.0.x := >=0.0.x <0.1.0
                ranges = [
                    {'operator': '>=', 'version': version},
                    {'operator': '<', 'version': Version(0, 1, 0)}
                ]
            else:
                # ^0.x.x := >=0.x.x <0.(x+1).0
                ranges = [
                    {'operator': '>=', 'version': version},
                    {'operator': '<', 'version': Version(0, version.minor + 1, 0)}
                ]
        else:
            # ^x.x.x := >=x.x.x <(x+1).0.0
            ranges = [
                {'operator': '>=', 'version': version},
                {'operator': '<', 'version': Version(version.major + 1, 0, 0)}
            ]
        
        return cls(ranges)
    
    @classmethod
    def _parse_tilde_range(cls, range_string):
        """Parse tilde range (~1.2.3)"""
        version_str = range_string[1:].strip()
        version = Version.parse(version_str)
        
        if version.major == 0:
            if version.minor == 0:
                # ~0.0.x := >=0.0.x <0.0.(x+1)
                ranges = [
                    {'operator': '>=', 'version': version},
                    {'operator': '<', 'version': Version(0, 0, version.patch + 1)}
                ]
            else:
                # ~0.x.x := >=0.x.x <0.(x+1).0
                ranges = [
                    {'operator': '>=', 'version': version},
                    {'operator': '<', 'version': Version(0, version.minor + 1, 0)}
                ]
        else:
            # ~x.x.x := >=x.x.x <x.(x+1).0
            ranges = [
                {'operator': '>=', 'version': version},
                {'operator': '<', 'version': Version(version.major, version.minor + 1, 0)}
            ]
        
        return cls(ranges)
    
    @classmethod
    def _parse_x_range(cls, range_string):
        """Parse x-range (1.2.x, 1.x, *, 0.8.*)"""
        if range_string == '*' or range_string == 'x' or range_string == 'X':
            return cls([])  # Accepts all versions
        
        parts = range_string.split('.')
        if len(parts) < 3:
            parts.extend(['x'] * (3 - len(parts)))
        
        major, minor, patch = parts
        
        if major == 'x' or major == 'X':
            return cls([])  # Accepts all versions
        
        if minor == 'x' or minor == 'X' or minor == '*':
            # 1.x or 1.* := >=1.0.0 <2.0.0
            ranges = [
                {'operator': '>=', 'version': Version(int(major), 0, 0)},
                {'operator': '<', 'version': Version(int(major) + 1, 0, 0)}
            ]
        elif patch == 'x' or patch == 'X' or patch == '*':
            # 1.2.x or 1.2.* := >=1.2.0 <1.3.0
            ranges = [
                {'operator': '>=', 'version': Version(int(major), int(minor), 0)},
                {'operator': '<', 'version': Version(int(major), int(minor) + 1, 0)}
            ]
        else:
            # Exact version
            ranges = [{'operator': '=', 'version': Version.parse(range_string)}]
        
        return cls(ranges)
    
    @classmethod
    def _parse_simple_range(cls, range_string):
        """Parse simple comparator range"""
        # Match operator and version
        pattern = r'^(>=|<=|>|<|=)?\s*(.+)$'
        match = re.match(pattern, range_string.strip())
        
        if not match:
            return cls([])
        
        operator, version_str = match.groups()
        operator = operator or '='  # Default to exact match
        version = Version.parse(version_str.strip())
        
        ranges = [{'operator': operator, 'version': version}]
        return cls(ranges)
    
    def satisfies(self, version):
        """Check if version satisfies this range"""
        if not self.ranges:
            return True  # Empty range accepts all versions
        
        if not isinstance(version, Version):
            version = Version.parse(str(version))
        
        for range_comp in self.ranges:
            operator = range_comp['operator']
            range_version = range_comp['version']
            
            if operator == '=':
                if version != range_version:
                    return False
            elif operator == '>':
                if not (version > range_version):
                    return False
            elif operator == '>=':
                if not (version >= range_version):
                    return False
            elif operator == '<':
                if not (version < range_version):
                    return False
            elif operator == '<=':
                if not (version <= range_version):
                    return False
        
        return True


def get_solidity_source(target):
    with open(target, 'r') as f:
        source_code = f.read()
    return source_code


def get_version_list():
    url = f"https://binaries.soliditylang.org/{soliditylang_platform()}/list.json"
    list_json = requests.get(url).content
    releases = json.loads(list_json)["releases"]
    return releases


def get_intalled_versions():
    if not SOLC_BINARIES_DIR.exists():
        return []
    return [str(p.name).replace("solc-", "") for p in SOLC_BINARIES_DIR.iterdir() if p.is_dir()]


def get_current_version():
    if os.path.exists(f"{SOLC_PARSER_DIR}/global-version"):
        with open(f"{SOLC_PARSER_DIR}/global-version", "r", encoding="utf-8") as f:
            return f.read()
    else:
        return None


def check_version(version_list, version):
    for v in version:
        if v not in version_list:
            return False
        else:
            return True

def check_installed_version(version):
    if not SOLC_BINARIES_DIR.exists():
        return False
    
    version_dir = SOLC_BINARIES_DIR / f"solc-{version}"
    if not version_dir.exists():
        return False
    
    # solc 바이너리 파일이 존재하는지 확인
    solc_binary = version_dir / "solc"
    return solc_binary.exists() and solc_binary.is_file()

def find_matching_index(versions, version_list):
    for i, v in enumerate(version_list):
        if versions == v:
            return i
    return None


def parse_solidity_version(source_code):
    """
    Parse Solidity pragma statements using npm semver rules.
    Supports:
    - pragma solidity version ranges
    - pragma abicoder v1/v2
    - pragma experimental ABIEncoderV2, SMTChecker
    """
    pragmas = {
        'solidity': [],
        'abicoder': [],
        'experimental': []
    }
    
    # Parse pragma solidity
    solidity_pattern = r"pragma\s+solidity\s+(.+?);"
    solidity_matches = re.findall(solidity_pattern, source_code, re.IGNORECASE)
    pragmas['solidity'] = [match.strip() for match in solidity_matches]
    
    # Parse pragma abicoder
    abicoder_pattern = r"pragma\s+abicoder\s+(v[12]);"
    abicoder_matches = re.findall(abicoder_pattern, source_code, re.IGNORECASE)
    pragmas['abicoder'] = [match.strip() for match in abicoder_matches]
    
    # Parse pragma experimental
    experimental_pattern = r"pragma\s+experimental\s+([^;]+);"
    experimental_matches = re.findall(experimental_pattern, source_code, re.IGNORECASE)
    pragmas['experimental'] = [match.strip() for match in experimental_matches]
    
    return pragmas


def satisfies_version_range(version, version_range):
    """
    Check if a version satisfies a version range using npm semver rules.
    """
    try:
        range_obj = VersionRange.parse(version_range)
        return range_obj.satisfies(version)
    except (ValueError, TypeError):
        # Fallback for invalid semver strings
        return False


def find_best_matching_version(version_ranges, available_versions):
    """
    Find the best matching version that satisfies all version ranges.
    Uses npm semver rules for version comparison and range satisfaction.
    """
    if not version_ranges:
        return None
    
    # Sort available versions in descending order (newest first)
    sorted_versions = sorted(available_versions, key=lambda v: Version.parse(v), reverse=True)
    
    # Find the highest version that satisfies all ranges
    for version in sorted_versions:
        satisfies_all = True
        for version_range in version_ranges:
            if not satisfies_version_range(version, version_range):
                satisfies_all = False
                break
        
        if satisfies_all:
            return version
    
    return None


def find_best_matching_version_from_source(source_code, available_versions):
    """
    Parse source code for pragma statements and find the best matching solc version.
    """
    pragmas = parse_solidity_version(source_code)
    version_requirements = analyze_pragma_requirements(pragmas)
    
    if not version_requirements:
        # No version requirements found, return latest version
        return max(available_versions, key=lambda v: Version.parse(v))
    
    return find_best_matching_version(version_requirements, available_versions)


def get_version_constraints(version_range):
    """
    Parse version range and return minimum and maximum version constraints.
    """
    try:
        range_obj = VersionRange.parse(version_range)
        min_version, max_version = None, None
        for comparator in range_obj.ranges:
            op = comparator['operator']
            v = comparator['version']
            if op == '=':
                return str(v), str(v)
            if op in ('>=', '>'):
                if min_version is None or v > min_version:
                    min_version = v
            if op in ('<=', '<'):
                if max_version is None or v < max_version:
                    max_version = v
        return str(min_version) if min_version else None, str(max_version) if max_version else None
    except (ValueError, TypeError):
        return None, None


def compare_version(sign_list, version_list):
    """
    Legacy function - kept for backward compatibility.
    Use find_best_matching_version for new code.
    """
    min_version = min(version_list)
    min_index = version_list.index(min_version)
    return list([sign_list[min_index]]), list([min_version])


def get_highest_version(version_list, target_version):
    matching_versions = []
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    return matching_versions[-1]


def install_solc(version):
    # OS별 바이너리 경로 결정
    system = platform.system().lower()
    if system == "linux":
        platform_key = "linux-amd64"
    elif system == "darwin":
        platform_key = "macosx-amd64"
    else:
        print("지원하지 않는 OS입니다.")
        return False

    artifacts = get_version_list()
    if version not in artifacts:
        print(f"지원하지 않는 버전: {version}")
        return False

    url = f"https://binaries.soliditylang.org/{platform_key}/" + artifacts[version]
    version_dir = SOLC_BINARIES_DIR / f"solc-{version}"
    version_dir.mkdir(parents=True, exist_ok=True)
    binary_path = version_dir / "solc"

    # 이미 설치된 경우
    if binary_path.exists():
        print(f"Version {version} is already installed.")
        return True

    print(f"Downloading solc {version} from {url} ...")
    response = requests.get(url)
    with open(binary_path, "wb") as file:
        file.write(response.content)
    os.chmod(binary_path, 0o755)
    print(f"Version '{version}' installed at {binary_path}")
    return True


def uninstall_solc(version):
    artifact_file_dir = SOLC_BINARIES_DIR.joinpath(f"solc-{version}")
    if os.path.exists(artifact_file_dir):
        print(f"Uninstalling solc '{version}'...")
        shutil.rmtree(artifact_file_dir)
        print(f"Version '{version}' uninstalled.")
        if version == get_current_version():
            os.remove(f"{SOLC_PARSER_DIR}/global-version")
            print(
                f"Version '{version}' was the global version. Switching to version.")
    else:
        print(
            f"'{version}' is not installed. Use 'solc-parser --list' to see all available versions.")
        return


def get_solc_path():
    """Get the current solc binary path"""
    link_path = SOLC_BINARIES_DIR.joinpath("solc")
    if link_path.exists() and link_path.is_symlink():
        return link_path.resolve()
    return None


def setup_path_instructions():
    """Print instructions for adding solc to PATH"""
    print("\n=== PATH SETTING INSTRUCTIONS ===")
    print(f"solc binary location: {SOLC_BINARIES_DIR}")
    print("\nPlease add the following to your PATH (IMPORTANT: Add to the BEGINNING):")
    print("\n1. Temporary setting (current terminal only):")
    print(f"   export PATH=\"{SOLC_BINARIES_DIR}:$PATH\"")
    print("\n2. Permanent setting (bash):")
    print(f"   echo 'export PATH=\"{SOLC_BINARIES_DIR}:$PATH\"' >> ~/.bashrc")
    print("   source ~/.bashrc")
    print("\n3. Permanent setting (zsh):")
    print(f"   echo 'export PATH=\"{SOLC_BINARIES_DIR}:$PATH\"' >> ~/.zshrc")
    print("   source ~/.zshrc")
    print("\n4. Alternative: Use alias (add to ~/.bashrc or ~/.zshrc):")
    print(f"   alias solc='{SOLC_BINARIES_DIR}/solc'")
    print("\nAfter setting, check with 'solc --version'.")
    print("To check which solc is being used: 'which solc'")


def auto_setup_path():
    """Automatically setup PATH for current session"""
    import subprocess
    import os
    
    # 현재 PATH에 이미 추가되어 있는지 확인
    current_path = os.environ.get('PATH', '')
    if str(SOLC_BINARIES_DIR) in current_path:
        print(f"PATH already contains {SOLC_BINARIES_DIR}")
        return True
    
    # PATH에 추가
    new_path = f"{SOLC_BINARIES_DIR}:{current_path}"
    os.environ['PATH'] = new_path
    
    print(f"Added {SOLC_BINARIES_DIR} to PATH for current session")
    print("To make it permanent, follow the instructions above")
    
    # 확인
    try:
        result = subprocess.run(['which', 'solc'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Current solc location: {result.stdout.strip()}")
        else:
            print("solc not found in PATH")
    except Exception as e:
        print(f"Error checking solc location: {e}")
    
    return True


def switch_global_version(version, create_symlink=True):
    if not SOLC_BINARIES_DIR.exists():
        SOLC_BINARIES_DIR.mkdir(parents=True, exist_ok=True)
    
    if version in get_intalled_versions():
        if create_symlink:
            # 기존 심볼릭 링크/파일/디렉토리 모두 안전하게 제거
            if SOLC_SYMLINK.exists() or SOLC_SYMLINK.is_symlink():
                try:
                    if SOLC_SYMLINK.is_symlink() or SOLC_SYMLINK.is_file():
                        SOLC_SYMLINK.unlink()
                    elif SOLC_SYMLINK.is_dir():
                        import shutil
                        shutil.rmtree(SOLC_SYMLINK)
                except Exception as e:
                    print(f"Failed to remove existing symlink or file: {e}")
            # 새로운 심볼릭 링크 생성
            SOLC_SYMLINK.symlink_to(SOLC_BINARIES_DIR / f"solc-{version}" / "solc")
            print(f"Global solc version switched to {version}")
        return True
    else:
        print(f"Version {version} is not installed")
        return False


def get_abicoder_version_requirements(abicoder_version):
    """
    Get solc version requirements for ABI coder versions.
    
    ABI coder v2:
    - Available as experimental since 0.5.0
    - Non-experimental since 0.6.0
    - Default since 0.8.0
    
    ABI coder v1:
    - Default until 0.7.4
    - Can be explicitly selected since 0.7.4
    """
    if abicoder_version == 'v2':
        # ABI coder v2 requires solc >= 0.5.0
        return '>=0.5.0'
    elif abicoder_version == 'v1':
        # ABI coder v1 is supported in all versions
        return '*'
    else:
        return None


def get_experimental_requirements(experimental_feature):
    """
    Get solc version requirements for experimental features.
    """
    requirements = {
        'ABIEncoderV2': '>=0.5.0',  # Available since 0.5.0
        'SMTChecker': '>=0.5.0',    # Available since 0.5.0
    }
    return requirements.get(experimental_feature, None)


def analyze_pragma_requirements(pragmas):
    """
    Analyze all pragma statements and return version requirements.
    """
    version_requirements = []
    
    # Process solidity version requirements
    for solidity_range in pragmas['solidity']:
        version_requirements.append(solidity_range)
    
    # Process abicoder requirements
    for abicoder_version in pragmas['abicoder']:
        requirement = get_abicoder_version_requirements(abicoder_version)
        if requirement:
            version_requirements.append(requirement)
    
    # Process experimental requirements
    for experimental_feature in pragmas['experimental']:
        requirement = get_experimental_requirements(experimental_feature)
        if requirement:
            version_requirements.append(requirement)
    
    return version_requirements
