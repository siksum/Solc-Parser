# solc-parser

## 기본 형태

```solidity
pragma solidity [version];
```

## Description

- `버전 파싱 방법` :
  - 사용자가 input으로 넣어준 파일에 대해 버전 파싱
  - range 형태로 입력한 경우(ex. >=0.5.0 <=0.8.9) 해당 범위 내에서 가장 최신 버전 설치
    - 해당 경우는 <, <= 부등호 존재 여부에 따른 로직이 수행되도록 함
  - ^, ~, >= 기호가 있다면 해당 버전의 부버전 중 가장 최신의 패치 버전을 가져옴
    - 예) ^0.8.9 라면, 0.8.20 버전 가져옴. ~0.7이라면 0.7.6
  - \> , < 기호가 있다면 해당 버전의 부버전 중 가장 가까운 패치 버전을 선택함

## Requirement

- 지원 사양: macos m2

```shell
pip3 setup.py install
```

---

## Usage

```shell
solc-parser [file_path]
```

## Option

### 설치 가능한 solc 버전 리스트 반환

[Usage]

```shell
solc-parser --list
```

[Output]

```shell
sikk@gimnamlyeong-ui-MacBookPro solc_parser_v2 % solc-parser --list
0.8.20
0.8.19
0.8.18
0.8.17
...
0.5.15
0.5.14
0.5.13
0.5.12
```

<br></br>

### solc 바이너리 설치

[Usage]

```shell
solc-parser --install [version]
```

- 띄워쓰기를 기준으로 복수의 버전 입력할 수 있음

[Output]

```shell
sikk@gimnamlyeong-ui-MacBookPro solc_parser_v2 % solc-parser --install 0.8.2
Installing solc '0.8.2'...
Version '0.8.2' installed.
```

<br></br>

### 현재 사용할 solc 버전 선택

[Usage]

```shell
solc-parser --use [version]
```

[Output]

```shell
sikk@gimnamlyeong-ui-MacBookPro solc_parser_v2 % solc-parser --use 0.8.2
Switched global version to 0.8.2
```

<br></br>

### 현재 선택되어 있는 solc 버전과 설치되어 있는 버전 리스트 반환

[Usage]

```shell
solc-parser --version
```

[Output]

```shell
sikk@gimnamlyeong-ui-MacBookPro solc_parser_v2 % solc-parser --version

Current version: 0.8.2

Installed versions: ['0.6.12', '0.8.2', '0.7.1', '0.8.0']
```

<br></br>

### 설치된 solc 바이너리 삭제

[Usage]

```shell
solc-parser --uninstall [version]
```

- 띄워쓰기를 기준으로 복수 버전 입력 가능

[Output]

```shell
sikk@gimnamlyeong-ui-MacBookPro solc_parser_v2 % solc-parser --uninstall 0.8.2
Uninstalling solc '0.8.2'...
Version '0.8.2' uninstalled.
Version '0.8.2' was the global version. Switching to version.
```

---

## 개선 및 해결해야할 것

<aside>
💡 List

    1. 와일드카드(*) 경우의 수 처리하기
    2. unit test
    3. linux/windows 지원 업데이트

</aside>
