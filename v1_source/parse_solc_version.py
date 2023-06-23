import re
import sys


def get_solc_version_list():
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    return source_code


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
    return sign, version


def compare_version(sign_list, version_list):
    max_version = max(version_list)
    max_index = version_list.index(max_version)
    return sign_list[max_index], max_version


def info_version(sign_list, version_list):
    for sign, version in zip(sign_list, version_list):
        print("Sign:", sign)
        print("Version:", version)
        print("===============")


def main():
    # Solidity 버전 파싱
    solidity_code = get_solc_version_list()
    sign_list, version_list = parse_solidity_version(solidity_code)

    if sys.argv[3] == "info":
        info_version(sign_list, version_list)

    if len(version_list) != 1:
        sign, version = compare_version(sign_list, version_list)
        if sys.argv[3] == "sign":
            print(sign)
        else:
            print(version)
    elif len(version_list) == 1:
        if sys.argv[3] == "sign":
            print(sign_list[0])
        else:
            print(version_list[0])


if __name__ == "__main__":
    if len(sys.argv) != 4 and (sys.argv[2] == "--type" and sys.argv[3] not in ["sign", "version", "info"]):
        print(
            f"Usage: python3 {sys.argv[0]} [file] --type [sign | version] or --info")
        sys.exit(1)

    main()
