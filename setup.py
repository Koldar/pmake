import os
from typing import Iterable

import setuptools
import pmakeup as pm

PACKAGE_NAME = "pmakeup"
PACKAGE_VERSION = pm.version.VERSION
PACKAGE_DESCRIPTION = "Library for quickly generate ER diagrams"
PACKAGE_URL = "https://github.com/Koldar/pmakeup.git"
PACKAGE_PYTHON_COMPLIANCE=">=3.6"
PACKAGE_EXE = "pmakeup"
PACKAGE_MAIN_MODULE = "pmakeup.main"
PACKAGE_CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
AUTHOR_NAME = "Massimo Bono"
AUTHOR_EMAIL = "massimobono1@gmail.com"

#########################################################
# INTERNALS
#########################################################

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_dependencies() -> Iterable[str]:
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            dep = fh.readline()
            yield dep.split("==")[0]


def get_test_dependencies() -> Iterable[str]:
    if os.path.exists("test_requirements.txt"):
        with open("test_requirements.txt", "r", encoding="utf-8") as fh:
            dep = fh.readline()
            yield dep.split("==")[0]


setuptools.setup(
    name=PACKAGE_NAME,  # Replace with your own username
    version=PACKAGE_VERSION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    # license=license_value,
    url=PACKAGE_URL,
    packages=setuptools.find_packages(),
    classifiers=PACKAGE_CLASSIFIERS,
    include_package_data=True,
    install_requires=list(get_dependencies()),
    tests_require=list(get_test_dependencies()),
    # data_files=get_data_files(),
    python_requires=PACKAGE_PYTHON_COMPLIANCE,
    # add for pyinstaller to work
    entry_points={"console_scripts": [f"{PACKAGE_EXE}={PACKAGE_MAIN_MODULE}:main"]},
    # cmdclass={
    #     'generate_executable': generate_executable,
    #     'build': custom_build,
    # },
)
