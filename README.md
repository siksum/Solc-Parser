# solc-parser

## The default format

```solidity
pragma solidity [version];
```

## Description

- `Version parsing method` :
  - Parsing the version from the file provided by the user as input.
  - If the range is specified (e.g., >=0.5.0 <=0.8.9), the latest version within that range is installed.
    - The logic is performed based on the presence of <, <= signs.
  - If ^, ~, or >= symbols are present, the latest patch version of the corresponding minor version is retrieved.
    - For example, ^0.8.9 would retrieve version 0.8.20. ~0.7 would retrieve version 0.7.6.
  - If >, < symbols are present, the closest patch version to the specified version is selected.

## Requirements

- Operating System: macOS (updating for Linux and Windows . . .)
- Python Versions: Python 3.8 and above

```shell
$ pip3 install solc-parser
```

---

## Usage

```shell
$ solc-parser [file_path]
```

## Option

### Retrieve the list of available solc versions for installation

[Usage]

```shell
$ solc-parser --list
```

[Output]

```shell
$ solc-parser --list
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

### Install the solc binary

[Usage]

```shell
$ solc-parser --install [version]
```

- Multiple versions can be specified, separated by spaces.
- The solc binary will be installed under the `.solc-parser/binaries` directory.


[Output]

```shell
$ solc-parser --install 0.8.2
Installing solc '0.8.2'...
Version '0.8.2' installed.
```

<br></br>

### Select the currently desired solc version

[Usage]

```shell
$ solc-parser --use [version]
```

[Output]

```shell
$ solc-parser --use 0.8.2
Switched global version to 0.8.2
```

<br></br>

### Return the currently selected solc version and the list of installed versions

[Usage]

```shell
$ solc-parser --version
```

[Output]

```shell
$ solc-parser --version

Current version: 0.8.2

Installed versions: ['0.6.12', '0.8.2', '0.7.1', '0.8.0']
```

<br></br>

### Uninstall the installed solc binaries

[Usage]

```shell
$ solc-parser --uninstall [version]
```

- Multiple versions can be specified, separated by spaces.

[Output]

```shell
$ solc-parser --uninstall 0.8.2
Uninstalling solc '0.8.2'...
Version '0.8.2' uninstalled.
Version '0.8.2' was the global version. Switching to version.
```

---

## Improvements and tasks to be addressed

<aside>
💡 List

    1. Handling wildcard (*) scenarios.
    2. Implement unit test
    3. Update to support Linux and Windows platforms.

</aside>
