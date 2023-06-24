from .solc_parse import *
import argparse
from .env import *


def parse_args():
    parser = argparse.ArgumentParser(prog='solc-parser', formatter_class=argparse.RawTextHelpFormatter, description="[Description]\n""Solc Automated Parser and Installation Tool.\n"
                                     "You can install the appropriate version of the solc binary by automatically extracting the version for the sol file you inserted with input.\n"
                                     "\n"
                                     "solc-parser [target file]\n")
    parser.add_argument("input file", nargs='?',
                        help='Input your source file (.sol)')
    parser.add_argument(
        "--list", help="Show solc version list", action="store_true")
    parser.add_argument("--install", nargs='*', help="Install solc version")
    parser.add_argument("--uninstall", nargs='*',
                        help="Uninstall solc version")
    parser.add_argument("--use", nargs='?', help="Use solc version")
    parser.add_argument("--version",
                        help="Displays the current solc version", action="store_true")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def __main__():
    halt_incompatible_system()
    args = parse_args()
    print(args)

    if args.list:
        version_list =get_version_list()
        for v in version_list:
            print(v)
        return
    elif args.install:
        install_solc(args.install[0])
        return
    # else:
    #     version_list = get_version_list()
    #     solidity_file = get_solidity_source()
    #     sign, version = parse_solidity_version(solidity_file)
    #     check = check_version(version_list, version)
    #     if check == False:
    #         print("incorrect version")
    #         return
    #     if len(version) != 1:
    #         sign, version = compare_version(sign, version)
    #     version_list, sign[0], version[0]

    # if args:
    #     version_list, sign, version = args
    #     index = find_matching_index(version, version_list)

    #     if sign == '<':
    #         version = version_list[index - 1]
    #         print("[Output]", version)
    #         install_solc(version)
    #     elif sign == '>':
    #         version = version_list[index + 1]
    #         print("[Output]", version)
    #         install_solc(version)
    #     elif (sign == '^' or sign == '~'):
    #         version = get_highest_version(version_list, version)
    #         print("[Output]", version)
    #         install_solc(version)
    #     elif (sign == '=' or sign == '>=' or sign == '<=') or (not sign and version):
    #         print("[Output]", version)
    #         install_solc(version)
    #     else:
    #         print("incorrect sign")
    #         return
    # else:
    #     return


if __name__ == "__main__":
    __main__()
