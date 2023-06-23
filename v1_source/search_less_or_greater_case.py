import sys
from packaging import version


def get_solc_version_list():
    with open('solc_list.txt', 'r') as f:
        version_list = f.read().splitlines()
    return version_list


def get_lower_version(version_list, target_version):
    matching_versions = []
    for v in version_list:
        v_tuple = tuple(map(int, v.split('.')))
        target_tuple = tuple(map(int, target_version.split('.')))
        if v_tuple < target_tuple or (v_tuple[:-1] == target_tuple[:-1] and len(v_tuple) < len(target_tuple)):
            matching_versions.append(v)
    if not matching_versions:
        return None
    latest_version = max(matching_versions, key=version.parse)
    return latest_version


def get_higher_version(version_list, target_version):
    matching_versions = []
    for v in version_list:
        v_tuple = tuple(map(int, v.split('.')))
        target_tuple = tuple(map(int, target_version.split('.')))
        if v_tuple > target_tuple or (v_tuple[:-1] == target_tuple[:-1] and len(v_tuple) > len(target_tuple)):
            matching_versions.append(v)
    if not matching_versions:
        return None
    latest_version = min(matching_versions, key=version.parse)
    return latest_version


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} [target_version] [target_sign]")
        sys.exit(1)
    target_version = sys.argv[1]
    target_sign = sys.argv[2]
    version_list = get_solc_version_list()

    if target_sign == '<':
        lowest_version = get_lower_version(version_list, target_version)
        print(lowest_version)
    elif target_sign == '>':
        highest_version = get_higher_version(version_list, target_version)
        print(highest_version)
    else:
        print("incorrect target_sign")


if __name__ == '__main__':
    main()
