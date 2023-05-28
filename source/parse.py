import sys
import subprocess
import re
import json
import urllib.request
import env as env


def get_solidity_source():
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    return source_code

def get_version_list():
    url = f"https://binaries.soliditylang.org/{env.soliditylang_platform()}/list.json"
    list_json = urllib.request.urlopen(url).read()
    available_releases = json.loads(list_json)["releases"]
    available_releases = list(available_releases.keys())
    return available_releases

def check_version(version_list, version):
    for v in version:
        if v not in version_list:
            return False   
        else:
            return True

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
    return list(sign_list[min_index]), list([min_version])


def get_lower_version(version_list, target_version):
    matching_version = []
    for v in version_list:
        if v == target_version:
            matching_version.append(version_list[version_list.index(v) - 1])
    if not matching_version:
        return None
    return matching_version[0]


def get_higher_version(version_list, target_version):
    matching_version = []
    for v in version_list:
        if v == target_version:
            matching_version.append(version_list[version_list.index(v) + 1])
    if not matching_version:
        return None
    return matching_version[0]


def get_highest_version(version_list, target_version):
    matching_versions = []
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    if not matching_versions:
        return None
    return matching_versions[0]


def install_solc(version):
    print('solc-select install', version)
    subprocess.run(['solc-select', 'install', version],
                   capture_output=True, text=True)
    print('solc-select use', version)
    subprocess.run(['solc-select', 'use', version],
                   capture_output=True, text=True)
