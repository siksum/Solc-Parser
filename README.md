# Solc-Parser

A powerful Solidity compiler (solc) version management tool that automatically parses Solidity files and installs the appropriate solc version based on pragma statements and version requirements.

## Features

- **Automatic Version Detection**: Parses Solidity files to extract version requirements from pragma statements
- **Complete npm Semver Support**: Full implementation of npm semantic versioning rules including:
  - Caret ranges (`^1.2.3`)
  - Tilde ranges (`~1.2.3`)
  - Hyphen ranges (`1.2.3 - 2.3.4`)
  - X-ranges (`1.2.x`, `1.x`, `*`, `0.8.*`)
  - Comparison operators (`>=`, `<=`, `>`, `<`, `=`)
  - Logical OR (`||`)
  - Prerelease tags (`1.2.3-alpha.1`)
  - Build metadata (`1.2.3+build.1`)
- **Advanced Pragma Support**: Parses and handles:
  - `pragma solidity` version ranges
  - `pragma abicoder v1/v2`
  - `pragma experimental ABIEncoderV2, SMTChecker`
- **Automatic Installation**: Downloads and installs solc binaries from official sources
- **Global Version Management**: Creates symbolic links for easy version switching
- **Cross-Platform Support**: Works on Linux and macOS
- **PATH Integration**: Provides instructions for PATH setup

## Installation

### From Source

```bash
git clone https://github.com/siksum/Solc-Parser.git
cd Solc-Parser
pip install -e .
```

### Using pip

```bash
pip install solc-parser
```

## Usage

### Basic Usage

Parse a Solidity file and automatically install the appropriate solc version:

```bash
solc-parser your_contract.sol
```

### Command Line Options

```bash
# List all available solc versions
solc-parser --list

# Install specific version(s)
solc-parser --install 0.8.30
solc-parser --install 0.7.*  # Install latest 0.7.x version

# Use specific version
solc-parser --use 0.8.30
solc-parser --use 0.7.*  # Use latest 0.7.x version

# Uninstall version(s)
solc-parser --uninstall 0.7.6

# Show current version
solc-parser --version
```

### Examples

#### Simple Solidity File
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleContract {
    uint256 public value;
    
    function setValue(uint256 _value) external {
        value = _value;
    }
}
```

Running `solc-parser simple.sol` will:
1. Parse the pragma statement `^0.8.0`
2. Find the latest compatible version (e.g., 0.8.30)
3. Download and install solc 0.8.30
4. Create a symbolic link for global use

#### Advanced Solidity File with Multiple Pragmas
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
pragma abicoder v2;
pragma experimental SMTChecker;

contract AdvancedContract {
    struct ComplexStruct {
        uint256[] numbers;
        string name;
    }
    
    function processData(ComplexStruct memory data) external pure returns (uint256) {
        return data.numbers.length;
    }
}
```

Running `solc-parser advanced.sol` will:
1. Parse all pragma statements
2. Determine version requirements:
   - `^0.8.0` (solidity version)
   - `>=0.5.0` (abicoder v2 requirement)
   - `>=0.5.0` (SMTChecker requirement)
3. Find the best matching version that satisfies all requirements
4. Install and configure the appropriate solc version

## Version Range Support

### Caret Ranges (`^`)
- `^1.2.3` := `>=1.2.3 <2.0.0`
- `^0.2.3` := `>=0.2.3 <0.3.0`
- `^0.0.3` := `>=0.0.3 <0.1.0`

### Tilde Ranges (`~`)
- `~1.2.3` := `>=1.2.3 <1.3.0`
- `~1.2` := `>=1.2.0 <1.3.0`
- `~1` := `>=1.0.0 <2.0.0`

### X-Ranges
- `1.2.x` or `1.2.*` := `>=1.2.0 <1.3.0`
- `1.x` or `1.*` := `>=1.0.0 <2.0.0`
- `*` or `x` := accepts all versions

### Hyphen Ranges
- `1.2.3 - 2.3.4` := `>=1.2.3 <=2.3.4`

### Comparison Operators
- `>=1.2.3`, `<=1.2.3`, `>1.2.3`, `<1.2.3`, `=1.2.3`

### Logical OR
- `^1.2.3 || ^2.3.4` := satisfies either range

## Installation Directory

Solc binaries are installed in:
```
~/.solc-parser/bin/
├── solc-0.7.6/
│   └── solc
├── solc-0.8.30/
│   └── solc
└── solc -> solc-0.8.30/solc  # Symbolic link to current version
```

## PATH Setup

After installation, add the binary directory to your PATH:

### Temporary (current session only)
```bash
export PATH="$HOME/.solc-parser/bin:$PATH"
```

### Permanent (bash)
```bash
echo 'export PATH="$HOME/.solc-parser/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permanent (zsh)
```bash
echo 'export PATH="$HOME/.solc-parser/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Alternative: Use alias
```bash
echo "alias solc='$HOME/.solc-parser/bin/solc'" >> ~/.bashrc
source ~/.bashrc
```

## Requirements

- Python 3.8 or higher
- Linux or macOS
- Internet connection for downloading solc binaries

## Dependencies

- `requests`: For downloading solc binaries

## Development

### Building

```bash
./build.sh
```

### Testing

```bash
python -m pytest tests/
```

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Issues

If you encounter any issues, please report them on the [GitHub Issues page](https://github.com/siksum/Solc-Parser/issues).

## Author

**Namryeong Kim** - [GitHub](https://github.com/siksum)

## Acknowledgments

- Solidity team for the official solc binaries
- npm semver specification for version range parsing rules
