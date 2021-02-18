import os
from typing import List, Tuple

import setuptools
from pmakeup import version
from pmakeup.exceptions.PMakeupException import InvalidScenarioPMakeupException

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_data_files() -> List[Tuple[str, List[str]]]:
    if os.name == "nt":
        return [
            # put exe into C:\Python38\Scripts
            ("Scripts", [os.path.join("scripts", "pmakeup.exe")])
        ]
    elif os.name == "posix":
        return [
            # /usr/local/bin
            ("bin", [os.path.join("scripts", "pmakeup")])
        ]
    else:
        raise InvalidScenarioPMakeupException(f"invalid os name {os.name}")


setuptools.setup(
    name="pmakeup",  # Replace with your own username
    version=version.VERSION,
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Library for quickly develop makefile-like files, platform independent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # license=license_value,
    url="https://github.com/Koldar/pmakeup.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=[
        "colorama",
        "decorator",
        "semver",
        "networkx",
        "psutil",
    ],
    # data_files=get_data_files(),
    python_requires='>=3.6',
    # add for pyinstaller to work
    entry_points={"console_scripts": ["pmakeup=pmakeup.main:main"]},
    # cmdclass={
    #     'generate_executable': generate_executable,
    #     'build': custom_build,
    # },
)
