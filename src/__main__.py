import argparse
import sys
from solc_parse import *
from env import *


def parse_args():
    parser = argparse.ArgumentParser(
        prog='solc-parser',
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "[Description]\n"
            "Solc Automated Parser and Installation Tool.\n"
            "You can install the appropriate version of the solc binary by automatically extracting the version for the sol file you inserted with input.\n\n"
            "solc-parser [target file]"
        )
    )
    parser.add_argument("target", nargs='?', help='Input your source file (.sol)')
    parser.add_argument("--list", action="store_true", help="Show solc version list")
    parser.add_argument("--install", nargs='*', help="Install solc version")
    parser.add_argument("--uninstall", nargs='*', help="Uninstall solc version")
    parser.add_argument("--use", nargs='?', help="Use solc version")
    parser.add_argument("--version", action="store_true", help="Displays the current solc version")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def parse_target_file(target):
    version_dict = get_version_list()
    solidity_code = get_solidity_source(target)
    
    # 새로운 pragma 파싱 구조 사용
    pragmas = parse_solidity_version(solidity_code)
    version_requirements = analyze_pragma_requirements(pragmas)
    
    if not version_requirements:
        print("No version requirements found in the file")
        return None
    
    # 모든 버전 요구사항을 만족하는 최적의 버전 찾기
    best_version = find_best_matching_version(version_requirements, list(version_dict.keys()))
    
    if not best_version:
        print("No compatible version found for the requirements")
        return None
    
    return list(version_dict.keys()), None, best_version


def print_version_list():
    for v in get_version_list():
        print(v)


def install_versions(versions):
    for v in versions:
        # x-range 처리 (예: 0.8.*, 1.x 등)
        if '*' in v or 'x' in v.lower():
            version_list = list(get_version_list().keys())
            
            try:
                range_obj = VersionRange.parse(v)
                available_versions = [version for version in version_list if range_obj.satisfies(version)]
                
                if available_versions:
                    # 범위 내에서 최신 버전 선택
                    target_version = max(available_versions, key=lambda version: Version.parse(version))
                    install_solc(target_version)
                else:
                    print(f"No compatible version found for range '{v}'")
            except (ValueError, TypeError):
                print(f"Invalid version range '{v}'")
        else:
            # 일반 버전 처리
            install_solc(v)


def uninstall_versions(versions):
    for v in versions:
        uninstall_solc(v)


def use_version(version):
    # x-range 처리
    if '*' in version:
        # x-range를 만족하는 최신 버전 찾기
        available_versions = get_version_list()
        version_range = VersionRange.parse(version)
        
        # 사용 가능한 버전 중에서 범위를 만족하는 최신 버전 찾기
        matching_versions = []
        for v in available_versions:
            if version_range.satisfies(v):
                matching_versions.append(v)
        
        if not matching_versions:
            print(f"No version matching {version} found")
            return
        
        # 최신 버전 선택
        target_version = max(matching_versions, key=lambda v: Version.parse(v))
        print(f"Found matching version: {target_version} for range {version}")
    else:
        target_version = version
    
    # 버전이 설치되어 있는지 확인
    if not check_installed_version(target_version):
        print(f"Version {target_version} is not installed. Installing...")
        if not install_solc(target_version):
            print(f"Failed to install version {target_version}")
            return
    
    # 전역 버전으로 설정
    if switch_global_version(target_version, True):
        print(f"Successfully switched to version {target_version}")
        print(f"Symlink created at: {SOLC_SYMLINK}")
        print(f"Add to PATH: export PATH=\"{SOLC_SYMLINK.parent}:$PATH\"")
    else:
        print(f"Failed to switch to version {target_version}")


def print_current_version():
    current_version = get_current_version() or "None"
    print(f"\nCurrent version: {current_version}\n\nInstalled versions: {get_intalled_versions()}\n")


def handle_target(target):
    result = parse_target_file(target)
    if not result:
        return
    
    version_list, sign, version = result
    
    print(f"Found best matching version: {version}")
    print(f"Pragma requirements analyzed from {target}")
    
    if not check_installed_version(version):
        print(f"Version {version} is not installed. Installing...")
        if not install_solc(version):
            print(f"Failed to install version {version}")
            return
    
    # 전역 버전으로 설정
    if switch_global_version(version, True):
        print(f"Successfully switched to version {version}")
        print(f"Symlink created at: {SOLC_SYMLINK}")
        print(f"Add to PATH: export PATH=\"{SOLC_SYMLINK.parent}:$PATH\"")
    else:
        print(f"Failed to switch to version {version}")


def main():
    halt_incompatible_system()
    args = parse_args()

    if args.list:
        print_version_list()
    elif args.install:
        install_versions(args.install)
    elif args.uninstall:
        uninstall_versions(args.uninstall)
    elif args.use:
        use_version(args.use)
    elif args.version:
        print_current_version()
    elif args.target:
        handle_target(args.target)


if __name__ == "__main__":
    main()
