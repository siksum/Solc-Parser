from .solc_parse import *
import argparse
from .env import *


def parse_args():
    parser = argparse.ArgumentParser(prog='solc-parser', formatter_class=argparse.RawTextHelpFormatter, description="[Description]\n""Solc Automated Parser and Installation Tool.\n"
                                     "You can install the appropriate version of the solc binary by automatically extracting the version for the sol file you inserted with input.\n"
                                     "\n"
                                     "solc-parser [target file]\n")
    parser.add_argument("target", nargs='?',
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

def parse_target_file(target):
    version_list = get_version_list()
    solidity_file = get_solidity_source(target)
    sign, version = parse_solidity_version(solidity_file)
    check = check_version(version_list, version)
    if check == False:
        print("incorrect version")
        return
    if len(version) != 1:
        sign, version = compare_version(sign, version)
    return (list(version_list.keys()), sign[0], version[0])

def __main__():
    halt_incompatible_system()
    args = parse_args()

    if args.list:
        version_list =get_version_list()
        for v in version_list:
            print(v)
        return
    elif args.install:
        for v in args.install:
            install_solc(v)
        return
    elif args.uninstall:
        for v in args.uninstall:
            uninstall_solc(v)
        return
    elif args.use:
        switch_global_version(args.use, True)
        return
    elif args.version:
        current_version = get_current_version()
        if not get_current_version():
            current_version = "None"
        print(f"\nCurrent version: {current_version}\n\nInstalled versions: {get_intalled_versions()}\n")
    elif args.target:
        (version_list, sign, version) =parse_target_file(args.target)
        print(version_list)
        index = find_matching_index(version, version_list)

        if sign == '<':
            version = version_list[index + 1]
        elif sign == '>':
            version = version_list[index - 1]
        elif (sign == '^' or sign == '~'):
            version = get_highest_version(version_list, version)
        elif (sign == '=' or sign == '>=' or sign == '<=') or (not sign and version):
            version = version
        else:
            print("incorrect sign")
            return
        if version:
            if not check_installed_version(version):
                install_solc(version)
                switch_global_version(version, True)
            else:
                switch_global_version(version, False)
    else:
        return


if __name__ == "__main__":
    __main__()
