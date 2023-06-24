import sys
import re
import json
import urllib.request
from .env import *
from pathlib import Path

def get_solidity_source():
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    return source_code


def get_version_list():
    url = f"https://binaries.soliditylang.org/{soliditylang_platform()}/list.json"
    list_json = urllib.request.urlopen(url).read()
    available_releases = json.loads(list_json)["releases"]
    available_releases = list(available_releases.keys())
    sorted_list = sorted(available_releases, key=lambda x: [
                         int(v) for v in x.split('.')])

    return sorted_list


def check_version(version_list, version):
    for v in version:
        if v not in version_list:
            return False
        else:
            return True


def find_matching_index(versions, version_list):
    for i, v in enumerate(version_list):
        if versions == v:
            return i
    return None


def parse_solidity_version(source_code):
    pattern = r".*pragma solidity.*"
    pragma_lines = re.findall(pattern, source_code)
    version = []
    sign = []
    for pragma_match in pragma_lines:
        condition_pattern = r"(\^|=|~|>=|<=|>|<)?\s*([0-9]+\.[0-9]+(\.[0-9]+)?)"
        condition_matches = re.findall(condition_pattern, pragma_match)
        for condition_match in condition_matches:
            sign.append(condition_match[0].strip()
                        if condition_match[0] else "")
            version.append(condition_match[1].strip())
    return sign, version


def compare_version(sign_list, version_list):
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
    if "VIRTUAL_ENV" in os.environ:
        HOME_DIR = Path(os.environ["VIRTUAL_ENV"])
    else:
        HOME_DIR = Path.home()
    SOLC_SELECT_DIR = HOME_DIR.joinpath(".solc-select")
    ARTIFACTS_DIR = SOLC_SELECT_DIR.joinpath("artifacts")
    artifact_file_dir = ARTIFACTS_DIR.joinpath(f"solc-{version}")

    artifacts = get_version_list()
    url = f"https://binaries.soliditylang.org/macosx-amd64/" + \
        artifacts.get(version)
    Path.mkdir(artifact_file_dir, parents=True, exist_ok=True)
    print(f"Installing solc '{version}'...")
    # urllib.request.urlretrieve(url, artifact_file_dir.joinpath(f"solc-{version}"))

    response = requests.get(url)
    with open(artifact_file_dir.joinpath(f"solc-{version}"), "wb") as file:
        file.write(response.content)

    # verify_checksum(version)
    # Path.chmod(artifact_file_dir.joinpath(f"solc-{version}"), 0o775)

    file_path = artifact_file_dir.joinpath(f"solc-{version}")
    os.chmod(file_path, 0o775)
    print(f"Version '{version}' installed.")
    return True
