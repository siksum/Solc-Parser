import sys
from packaging import version


def get_solc_version_list():
    with open('solc_list.txt', 'r') as f:
        version_list = f.read().splitlines()
    return version_list


def get_highest_version(version_list, target_version):
    matching_versions = []
    target_major_minor = '.'.join(target_version.split('.')[:2])
    for v in version_list:
        if v.startswith(target_major_minor):
            matching_versions.append(v)
    if not matching_versions:
        return None
    return str(max(map(version.parse, matching_versions)))


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} [target_version]")
        sys.exit(1)
    target_version = sys.argv[1]
    version_list = get_solc_version_list()
    highest_version = get_highest_version(version_list, target_version)
    print(highest_version)


if __name__ == '__main__':
    main()
