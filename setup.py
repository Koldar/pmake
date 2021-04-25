import os
from typing import List, Tuple, Iterable

import setuptools
import pmakeup as pm

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_dependencies() -> Iterable[str]:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        dep = fh.readline()
        yield dep.split("==")[0]


def get_test_dependencies() -> Iterable[str]:
    with open("test_requirements.txt", "r", encoding="utf-8") as fh:
        dep = fh.readline()
        yield dep.split("==")[0]



setuptools.setup(
    name="pmakeup",  # Replace with your own username
    version=pm.version.VERSION,
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Library for quickly generate ER diagrams",
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
    install_requires=list(get_dependencies()),
    tests_require=list(get_test_dependencies()),
    # data_files=get_data_files(),
    python_requires='>=3.6',
    # add for pyinstaller to work
    entry_points={"console_scripts": ["pmakeup=pmakeup.main:main"]},
    # cmdclass={
    #     'generate_executable': generate_executable,
    #     'build': custom_build,
    # },
)
