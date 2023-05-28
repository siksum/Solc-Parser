from setuptools import setup, find_packages

setup(
    name="solc parser",
    version="0.0.1",
    description="Solc Automated Parser and Installation Tool",
    author="Namryeong Kim",
    url="https://github.com/Namryeong-Kim/solc_parser_v2",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "solc_parser = source.main:main",
        ]
    },
    install_requires=["packaging", "requests", "solc-select"],