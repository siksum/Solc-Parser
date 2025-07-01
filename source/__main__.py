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
    version_dict = get_version_list() 
    # 유효한 solidity 버전들을 최신순으로 정렬 
    available_versions = sorted(list(version_dict.keys()),key=lambda v: semantic_version.Version(v),reverse=True)

    solidity_code = get_solidity_source(target)
    # solidity code에서 갖고 온 solidity 버전들 
    pragma_specs = parse_solidity_version(solidity_code) 

    if not pragma_specs:
        print("pragma solidity not found")
        return None
		
		# pragma_specs에 있는 버전이 available_versions에 있는 버전과 유효한지 판단 
    for v in available_versions:
        try:
            semver_v = semantic_version.Version(v)
            # 최신 버전부터 검사하기 때문에 유효하면 바로 return 
            if any(vv.match(semver_v) for vv in pragma_specs):
                return v
        except:
            continue  # 잘못된 버전 문자열은 건너뜀

		print("matching version not found")
    return None

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
        version =parse_target_file(args.target)
        if version==None:
            print("not version found")
            return 
    else:
        return


if __name__ == "__main__":
    __main__()
