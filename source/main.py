import parse as ps
import argparse
import env as env

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="[Description]\n""Solc Automated Parser and Installation Tool.\n" 
                                     "You can install the appropriate version of the solc binary by automatically extracting the version for the sol file you inserted with input.\n"
                                     "\n"
                                     "You must install solc-select before using this tool.\n"
                                     "If you want to install solc-select, please refer to the following link.\n"
                                     "https://github.com/crytic/solc-select\n")
    parser.add_argument("input file", nargs=1,help='Input your source file (.sol)')
    parser.add_argument("list", nargs='?', help="Show solc version list")
    args = parser.parse_args()

    if args.list:
        print(ps.get_version_list())
        return 
    else:
        version_list = ps.get_version_list()
        solidity_file = ps.get_solidity_source()
        sign, version = ps.parse_solidity_version(solidity_file)
        check = ps.check_version(version_list, version)
        if check == False:
            print("incorrect version")
            return
        if len(version) != 1:
            sign, version = ps.compare_version(sign, version)
        return version_list, sign[0], version[0]



def main():
    env.halt_incompatible_system()
    args = parse_args()
    
    if args:
        version_list, sign, version = args
        index = ps.find_matching_index(version, version_list)

        if sign == '<':
            version = version_list[index - 1]
            print("[Output]", version)
            ps.install_solc(version)
        elif sign == '>':
            version = version_list[index + 1]
            print("[Output]", version)
            ps.install_solc(version)
        elif (sign == '^' or sign == '~'):
            version = ps.get_highest_version(version_list, version)
            print("[Output]", version)
            ps.install_solc(version)
        elif (sign == '=' or sign == '>=' or sign == '<=') or (not sign and version):
            print("[Output]", version)
            ps.install_solc(version)
        else:
            print("incorrect sign")
            return
    else:
        return

    

if __name__ == "__main__":
    main()
