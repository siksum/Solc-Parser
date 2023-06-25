from setuptools import setup, find_packages

setup(
    name="solc parser",
    version="1.0.4",
    description="Solc Automated Parser and Installation Tool",
    author="Namryeong Kim",
    url="https://github.com/siksum/Solc-Parser",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "solc-parser = source.__main__:__main__",
        ]
    },
)
