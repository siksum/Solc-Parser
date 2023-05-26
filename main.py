import parser as ps


def main():
    version_list = ps.read_version_list()
    solidity_file = ps.get_solidity_source()
    sign, version = ps.parse_solidity_version(solidity_file)

    if sign[0] == '<':
        version = ps.get_higher_version(version_list, version[0])
        ps.install_solc(version)
    elif sign[0] == '>':
        version = ps.get_lower_version(version_list, version[0])
        ps.install_solc(version)
    elif (sign[0] == '^' or sign[0] == '~'):
        version = ps.get_highest_version(version_list, version[0])
        ps.install_solc(version)
    elif (sign[0] == '=' or sign[0] == '>=' or sign[0] == '<=' or (sign[0] == "" and version[0] is not None)):
        ps.install_solc(version)
    else:
        print("incorrect sign")
        return
    # correct_version = str(ps.search_version(version_list, version, sign))
    # ps.install_solc(correct_version)


if __name__ == "__main__":
    main()
