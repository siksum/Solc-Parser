from bs4 import BeautifulSoup
import re
import sys
import requests
from natsort import natsorted


def get_version_list():
    url = 'https://github.com/ethereum/solidity/releases'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    versions = []
    current_version = set()

    while True:
        releases = soup.find_all('a', class_='Link--primary')
        for release in releases:
            version = release.get_text(strip=True).replace('Version ', '')
            version = re.search(r'\d+(\.\d+)*', version).group()
            if version not in current_version:  # 중복 버전인 경우 건너뛰기
                versions.append(version)
                current_version.add(version)

        next_page_link = soup.find('a', class_='next_page')
        if not next_page_link:
            break

        next_page_url = 'https://github.com' + next_page_link['href']
        response = requests.get(next_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

    versions = natsorted(versions, key=lambda x: x.split('.')[
                         0])  # 메이저 버전 순으로 정렬
    return versions


def write_version_list(version_list):
    output_file = './solc_list.txt'
    # 버전 리스트를 파일에 저장
    with open(output_file, 'w') as f:
        for version in version_list:
            f.write(f"{version}\n")


def main():
    version_list = get_version_list()
    write_version_list(version_list)


if __name__ == '__main__':
    main()
