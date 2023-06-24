import sys
import re
import os
import requests
import json
from .env import *
from pathlib import Path
import shutil

if "VIRTUAL_ENV" in os.environ:
    HOME_DIR = Path(os.environ["VIRTUAL_ENV"])
else:
    HOME_DIR = Path.home()
SOLC_PARSER_DIR = HOME_DIR.joinpath(".solc-parser")
SOLC_BINARIES_DIR = SOLC_PARSER_DIR.joinpath("solc_binaries")


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
    return [str(p.name).replace("solc-", "") for p in SOLC_BINARIES_DIR.iterdir() if p.is_dir()]


def get_current_version():
    with open(f"{SOLC_PARSER_DIR}/global-version", "r", encoding="utf-8") as f:
        return f.read()


def check_version(version_list, version):
    for v in version:
        if v not in version_list:
            return False
        else:
            return True

def check_installed_version(version):
    for _, _, files in os.walk(SOLC_BINARIES_DIR):
        for file in files:
            installed_version = file.split('-')[1]
            if (installed_version == version):
                return True
    return False

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
    artifact_file_dir = SOLC_BINARIES_DIR.joinpath(f"solc-{version}")
    artifacts = get_version_list()
    url = f"https://binaries.soliditylang.org/macosx-amd64/" + \
        artifacts.get(version)
    Path.mkdir(artifact_file_dir, parents=True, exist_ok=True)
    print(f"Installing solc '{version}'...")

    response = requests.get(url)
    with open(artifact_file_dir.joinpath(f"solc-{version}"), "wb") as file:
        file.write(response.content)

    file_path = artifact_file_dir.joinpath(f"solc-{version}")
    os.chmod(file_path, 0o775)
    print(f"Version '{version}' installed.")
    return True


def uninstall_solc(version):
    artifact_file_dir = SOLC_BINARIES_DIR.joinpath(f"solc-{version}")
    if os.path.exists(artifact_file_dir):
        print(f"Uninstalling solc '{version}'...")
        shutil.rmtree(artifact_file_dir)
        print(f"Version '{version}' uninstalled.")
        if version == get_current_version():
            print(
                f"Version '{version}' was the global version. Switching to version.")
    else:
        print(
            f"'{version}' is not installed. Use 'solc-parser --list' to see all available versions.")
        return


def switch_global_version(version: str, always_install: bool) -> None:
    if version in get_intalled_versions():
        with open(f"{SOLC_PARSER_DIR}/global-version", "w", encoding="utf-8") as f:
            f.write(version)
        print("Switched global version to", version)
    elif version in get_version_list():
        if always_install:
            install_solc([version])
            switch_global_version(version, always_install)
        else:
            raise argparse.ArgumentTypeError(
                f"'{version}' must be installed prior to use.")
    else:
        raise argparse.ArgumentTypeError(f"Unknown version '{version}'")
