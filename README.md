# solc_parser_v2

## 기본 형태

```solidity
pragma solidity [version];
```

## Description

- `버전 파싱 방법` :
  - 사용자가 input으로 넣어준 파일에 대해 버전 파싱
  - range 형태로 입력한 경우(ex. >=0.5.0 <=0.8.9) 해당 범위 내에서 가장 최신 버전을 설치할 수 있도록 max 값 추출함
    - range로 입력되더라도, ~0.8.16 <0.8.13 이런식으로 들어온다면 0.8.12를 골라야 함
    - 해당 경우는 <, <= 부등호 존재 여부에 따른 로직이 수행되도록 함
  - ^, ~, >= 기호가 있다면 해당 버전의 부버전 중 가장 최신의 패치 버전을 가져옴
    - 예) ^0.8.9 라면, 0.8.20 버전 가져옴. ~0.7이라면 0.7.6
  - \> , < 기호가 있다면 해당 버전의 부버전 중 가장 가까운 패치 버전을 선택함
  - 선택해야 하는 버전에 대해 `solc-select install`과 `use` 명령을 수행함

## Usage

```shell
./solc-parser [file_path]
```

## Option

```shell
./solc-parser [file_path] list
```

- 설치 가능한 solc 버전 리스트 반환

## Requirement

- solc-select
- 지원 사양: macos m2

```shell
pip3 install solc-select
```

---

## 변경 사항

<aside>
💡 V1 update

    1. solc version list crawling 방식
        - ethereum/solidity release 페이지에서 정적 크롤링
        - selenium, chromedriver를 이용한 동적 크롤링
        - request 모듈을 이용한 크롤링
        → https://binaries.soliditylang.org/macosx-amd64/list.json에서 release key 추출하는 방식(solc-select 방식 차용)
        → solc_list.txt output을 따로 두지 않더라도 빠르게 list 형태로 접근 가능함

    2. 명령 실행 방식
        - shell script로 사용자의 입력을 처리하고, 기호에 따른 로직을 수행함. 최종적으로 solc-select install/use 하는 방식
        → 수행 로직은 parse.py에 모두 정의하고 main.py에서 호출하는 방식(python으로 모두 처리 가능함)

    3. 버전 파싱
        - range로 들어왔을 때, max 버전에 위치한 기호에 따라 로직을 수행하도록 정의
        → min 버전에 위치한 기호에 따른 로직을 수행하며 `<`, `<=` 와 함께 다른 기호가 정의되어 있다면, 기호 뒤에 기술된 버전이 min 버전이 아니더라도 해당 기호에 따른 로직을 처리함

    4. 적절한 버전 선택(가장 높은 패치 버전을 선택해야 할 때)
        - 부버전을 추출하여 같은 버전 리스트에 같은 부버전이 있을 때, 패치 버전에서 -1/+1
        → 해당 버전이 리스트에 존재할 때, 바로 앞/뒤 버전을 선택하도록 변경(따로 부버전 추출할 필요 없음)

</aside>

## 고려해야할 사항

<aside>
💡 경우의 수

    - [x] 0.x
    - [x] 0.x.x
    - 사용할 수 있는 기호
    - [x] ^ : 최신 마이너 버전
    - [x] ~ : 최신 패치 버전
    - [ ] \* : 모든 버전
        - pragma solidity \*
        - pragma solidity \*.0
        - pragma solidity \*.x
        - pragma solidity \*.\*
        - pragma solidity \*.\*.0
        - pragma solidity \*.\*.x
        - pragma solidity \*.\*.\*
        - pragma soldity 0.\*
        - pragma soldity 0.\*.\*
        - pragma soldity 0.0.\*
    - [x] = : 특정 버전
    - [x] ≥ : 특정 버전 이상
    - [x] ≤ : 특정 버전 이하
    - [x] > : 특정 버전 초과
    - [x] < : 특정 버전 미만
    - [x] 숫자만 기입
        - pragma solidty 0.x.x
    - [x] range 설정
    - ≥0.4.5 ≤0.7.0

</aside>

<aside>
💡 List

    1. 부버전과 일치하는 것 중 가장 높은 버전을 고르면 되는 경우
        - [x] 캐럿 기호(^)
        - [x] ~
        - [x] ≥
        - [x] range
        - [ ] \*
    2. 추출한 target_version과 동일한 버전을 고르면 되는 경우
        - [x] =
        - [x] ≤
        - [x] 숫자만 기입
    3. 입력한 버전의 패치버전에서 -1(list에서)
        - [x] <
    4. 입력한 버전의 패치버전에서 +1(list에서)
        - [x] >
    5. range로 들어온 경우
        - [x] 기호와 버전을 각각 분리해서 저장 → list
        - [x] 버전 리스트 중 가장 높은 버전의 기호에 따른 1-4 로직 연결

</aside>

## 개선 및 해결해야할 것

<aside>
💡 List

    1. 와일드카드(*) 경우의 수 처리하기

</aside>
