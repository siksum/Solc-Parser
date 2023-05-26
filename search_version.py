from packaging import version


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


def main(version_list, target_version, target_sign):
    if target_sign == '<':
        version = get_higher_version(version_list, target_version)
        return version
    elif target_sign == '>':
        version = get_lower_version(version_list, target_version)
        return version
    elif (target_sign == '^' or target_sign == '~'):
        version = get_highest_version(version_list, target_version)
        return version
    elif (target_sign == '=' or target_sign == '>=' or target_sign == '<=' or (target_sign == "" and target_version is not None)):
        return target_version
    else:
        print("incorrect target_sign")
        return 0


if __name__ == '__main__':
    main()
