import sys
import subprocess
import re
import json
import urllib.request
import env as env
from pyparsing import Regex, Combine, Literal, OneOrMore
import textwrap
from termcolor import colored


def get_solidity_source():
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    return source_code

def get_version_list():
    url = f"https://binaries.soliditylang.org/{env.soliditylang_platform()}/list.json"
    list_json = urllib.request.urlopen(url).read()
    available_releases = json.loads(list_json)["releases"]
    available_releases = list(available_releases.keys())
    sorted_list = sorted(available_releases, key=lambda x: [int(v) for v in x.split('.')])

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
    equal = Literal("=")
    carrot = Literal("^")
    tilde = Literal("~")
    inequality = Literal("<=") | Literal(">=") | Literal("<") | Literal(">")
    combined_inequality = Combine(inequality)

    pragma_pattern = r".*pragma solidity.*"
    pragma_lines = re.findall(pragma_pattern, source_code)

    version_condition = Regex(r"\d+\.\d+(\.\d+)?")
    version_with_condition = (carrot | tilde | combined_inequality | equal) + version_condition
    pragma = Literal("pragma") + Literal("solidity") + OneOrMore(version_with_condition)

    sign = []
    version = []
    parsed_results = pragma.parseString(pragma_lines[0])
    try:
        for i, result in enumerate(parsed_results[2:]):
            if i % 2 == 0:
                sign.append(result)
            else:
                version.append(result)
    except:
        pass
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
    print('solc-select install', version)
    subprocess.run(['solc-select', 'install', version],
                   capture_output=True, text=True)
    print('solc-select use', version)
    subprocess.run(['solc-select', 'use', version],
                   capture_output=True, text=True)
    print('execute slither')
    result = subprocess.run(['slither', sys.argv[1]], capture_output=True, text=True).stderr

    indented_result = textwrap.indent(result, '  ')
    colored_result = colored(indented_result, 'cyan')
    print(colored_result)