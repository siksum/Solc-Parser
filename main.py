import parser as ps
import argparse

def main():
    version_list = ps.read_version_list()
    solidity_file = ps.get_solidity_source()
    sign, version = ps.parse_solidity_version(solidity_file)

    if sign == '<':
        version = ps.get_higher_version(version_list, version)
        ps.install_solc(version)
    elif sign == '>':
        version = ps.get_lower_version(version_list, version)
        ps.install_solc(version)
    elif (sign == '^' or sign == '~'):
        version = ps.get_highest_version(version_list, version)
        ps.install_solc(version)
    elif (sign == '=' or sign == '>=' or sign == '<=' or (sign == "" and version is not None)):
        ps.install_solc(version)
    else:
        print("incorrect sign")
        return

if __name__ == "__main__":
    main()
