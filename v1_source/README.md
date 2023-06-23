# solc-parser

## 기본 형태

```solidity
pragma solidity [version];
```

## 사용법

```shell
./solc-parser.sh [file_path]
```

## 각 파일에 대한 설명

- `parse_solc_version.py` :

  - 사용자가 input으로 넣어준 파일에 대해 버전 파싱
  - range 형태로 입력한 경우(ex. >=0.5.0 <=0.8.9) 해당 범위 내에서 가장 최신 버전을 설치할 수 있도록 max 값 추출함
  - 단독 실행 시 사용 형태
    ```shell
    python3 parse_solc_version.py [file_path] [option] [option_value]
    ```
  - option :

    `--info`: input 파일의 버전, 버전에 사용된 기호 확인 가능. range일 경우 모든 기호, 버전 정보 출력

    `--type`: sign, version을 value에 입력할 수 있음.

        - sign, version을 각각 확인할 수 있으며, range일 경우 쓰여진 버전 중 가장 높은 버전과 해당 버전이 갖는 기호를 반환함

- `get_version_list.py` :

  - ethereum/solidity의 release 페이지에서 update된 버전 정보를 크롤링하여 가져옴
  - solc_list.txt에 버전만 추출하여 저장함
  - 단독 실행 시 사용 형태
    ```shell
    python3 get_version_list.py
    ```

- `search_highest_version.py` :

  - ^, ~, >= 기호가 있다면 해당 버전의 부버전 중 가장 최신의 패치 버전을 가져옴
  - 예) ^0.8.9 라면, 0.8.20 버전 가져옴. ~0.7이라면 0.7.6
  - 단독 실행 시 사용 형태
    ```shell
    python3 search_highest_version.py [target_version]
    ```

- `search_less_or_greater_case.py` :

  - \> , < 기호가 있다면 해당 버전의 부버전 중 가장 가까운 패치 버전을 선택함

    - 마지막 패치 버전(ex. 0.7.6)일때는 부버전에 +1을 해줘야함

    - 나머지 경우에는 해당 부버전 중 가장 최신의 패치 버전을 가져와야 하는데, 이부분은 아직 해결 안됨

- `solc-parser.sh`
  - 버전 리스트 update 및 기호 조건에 따른 python 파일 호출함
  - 선택해야 하는 버전에 대해 `solc-select install`과 `use` 명령을 수행함

## 고려해야할 사항

- 최신 버전 사용

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

## 조건에 따른 버전 선택

### 고려해야할 것

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
3. 입력한 버전의 패치버전에서 -1
   - [x] <
         → 0.8 이런식으로 부버전만 줬을때는 부버전 -1 해줘야 됨
4. 입력한 버전의 패치버전에서 +1
   - [x] >
5. range로 들어온 경우
   - [x] 기호와 버전을 각각 분리해서 저장 → list
   - [x] 버전 리스트 중 가장 높은 버전의 기호에 따른 1-4 로직 연결

- [x] 기호도 추출할 수 있어야 함
</aside>

## 개선 및 해결해야할 것

<aside>
💡 List

    1. 예외 발생시 페이지 로딩을 1초 기다렸다가 수행함 → output 출력까지 시간이 좀 걸림
    → selenium 무거워서 request 이용하는 형태로 변경

    2. 현재는 실행할 때마다 전체 리스트를 크롤링하는 방식 → 따로 파일에 저장해두고 새로운 버전 릴리즈가 나올때 새로운 버전만 추가하는 방식으로 변경해야할 것 같음
    - 내림차순으로 정렬해서 for문으로 저장된 파일의 처음과 릴리즈 크롤링한 값이 같다면 새로운 버전이 나온 것이 아니므로 break/return하면 되지 않을까?
    [x] 내림차순 정렬 완료
    [x] 파일에 저장하도록 변경

    3. 와일드카드(*) 경우의 수 처리하기

    4. >, >= 기호 처리
    [] 마지막 패치 버전(ex. 0.7.6)일때는 부버전에 +1을 해줘야함
    [] 나머지 경우에는 해당 부버전 중 가장 최신의 패치 버전을 가져와야 하는데, 이부분은 아직 해결 안됨
    - >= 0.7.6이면 0.7 버전중에 가장 높은 0.7.6을 설치하는게 맞는지, 0.8버전을 설치해야 하는지 모르겠음
    - remix로 아래 코드 돌려보니 자동으로 0.4버전 중에 가장 높은 0.4.26 버전 고름

</aside>

```solidity
pragma solidity >0.4.24;

contract Test {
    constructor() public {
        b = 0x12345678901234567890123456789012;
    }

    event Event(uint indexed a, bytes32 b);
    event Event2(uint indexed a, bytes32 b);
    function foo(uint a) public {
        emit Event(a, b);
    }

    bytes32 b;
}
```
