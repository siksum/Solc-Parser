import sys
import subprocess
import re
from packaging import version

# get information


def get_solidity_source():
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    return source_code


def info_version(sign_list, version_list):
    for sign, version in zip(sign_list, version_list):
        print("Sign:", sign)
        print("Version:", version)
        print("===============")


def write_version_list():
    output_file = './solc_list.txt'
    result = subprocess.run(['solc-select', 'install'],
                            capture_output=True, text=True).stdout.split('\n')
    result.pop(0)
    with open(output_file, 'w') as f:
        for version in result:
            f.write(f"{version}\n")


def read_version_list():
    version_list = []
    with open('./solc_list.txt', 'r') as f:
        for line in f.readlines():
            version_list.append(line.strip())
    print(version_list)
    return version_list

# parse solidity version


def parse_solidity_version(source_code):
    version_pattern = r"pragma solidity\s+(.*?);"
    pragma_matches = re.findall(version_pattern, source_code, re.DOTALL)
    version = []
    sign = []
    for pragma_match in pragma_matches:
        condition_pattern = r"(\^|=|~|>=|<=|>|<)?\s*([0-9]+\.[0-9]+(\.[0-9]+)?)"
        condition_matches = re.findall(condition_pattern, pragma_match)
        for condition_match in condition_matches:
            sign.append(condition_match[0].strip()
                        if condition_match[0] else "")
            version.append(condition_match[1].strip())
    print(sign, version)
    if len(version) != 1:
        compare_version(sign, version)
    return sign, version


def compare_version(sign_list, version_list):
    min_version = min(version_list)
    min_index = version_list.index(min_version)
    return sign_list[min_index], min_version


# search correct solc version
def get_lower_version(version_list, target_version):
    for v in version_list:
        if v == target_version:
            matching_version = version_list[version_list.index(v) - 1]
    if not matching_version:
        return None
    return matching_version


def get_higher_version(version_list, target_version):
    for v in version_list:
        if v == target_version:
            matching_version = version_list[version_list.index(v) + 1]
    if not matching_version:
        return None
    return matching_version


def get_highest_version(version_list, target_version):
    matching_versions = []
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    if not matching_versions:
        return None
    return str(max(map(version.parse, matching_versions)))

# install correct solc version


def install_solc(version):
    print('solc-select install', version)
    subprocess.run(['solc-select', 'install', version],
                   capture_output=True, text=True)
    print('solc-select use', version)
    subprocess.run(['solc-select', 'use', version],
                   capture_output=True, text=True)
