#!/bin/bash

solidity_file="$1"  # Solidity 파일 경로
# python_script="get_version_list.py"  # Python 스크립트 파일명

# # Solidity 버전 리스트 생성
# version_create=$(python3 "$python_script")

function print_version_info(){
    echo "Solidity version: $target_version"
    echo "Solidity sign: $target_sign"
}

function install_solc(){
    solc-select install $1
    solc-select use $1
}

# 솔리디티 버전 추출
target_version=$(python3 parse_solc_version.py "$solidity_file" --type version)
target_sign=$(python3 parse_solc_version.py "$solidity_file" --type sign)

if [[ -n "$target_version" && ( -z "$target_sign" || "$target_sign" == "=" || "$target_sign" == "<=" ) ]]; then
    print_version_info
    install_solc "$target_version"

elif [[ -n "$target_version" && ( "$target_sign" == "^" || "$target_sign" == "~" || "$target_sign" == ">=" ) ]]; then
    print_version_info
    get_version=$(python3 search_highest_version.py "$target_version")
    install_solc "$get_version"
elif [[ -n "$target_version" && ( "$target_sign" == "<" || "$target_sign" == ">" ) ]]; then
    print_version_info
    get_version=$(python3 search_less_or_greater_case.py "$target_version" "$target_sign")
    install_solc "$get_version"
else
  echo "Solidity version not found."
fi