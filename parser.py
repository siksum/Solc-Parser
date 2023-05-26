import sys
import subprocess
import re
from packaging import version


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
    output_file = 'solc_list.txt'
    result = subprocess.run(['solc-select', 'install'],
                            capture_output=True, text=True).stdout.split('\n')
    result.pop(0)
    with open(output_file, 'w') as f:
        for version in result:
            f.write(f"{version}\n")


def read_version_list():
    version_list = []
    with open('/Users/sikk/project_dream/solc_parser_v2/solc_list.txt', 'r') as f:
        for line in f.readlines():
            version_list.append(line.strip())
    return version_list


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
    if len(version) != 1:
        sign, version = compare_version(sign, version)
    return sign, version


def compare_version(sign_list, version_list):
    min_version = min(version_list)
    min_index = version_list.index(min_version)
    return sign_list[min_index], min_version


def get_lower_version(version_list, target_version):
    matching_version = []
    for v in version_list:
        if v == target_version:
            matching_version.append(version_list[version_list.index(v) - 1])
    if not matching_version:
        return None
    return str(max(map(version.parse, matching_version[0])))


def get_higher_version(version_list, target_version):
    matching_version = []
    for v in version_list:
        if v == target_version:
            matching_version.append(version_list[version_list.index(v) + 1])
    if not matching_version:
        return None
    return str(max(map(version.parse, matching_version[0])))


def get_highest_version(version_list, target_version):
    matching_versions = []
    print(target_version)
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    if not matching_versions:
        return None
    return str(max(map(version.parse, matching_versions)))


def install_solc(version):
    print('solc-select install', version)
    subprocess.run(['solc-select', 'install', version],
                   capture_output=True, text=True)
    print('solc-select use', version)
    subprocess.run(['solc-select', 'use', version],
                   capture_output=True, text=True)
