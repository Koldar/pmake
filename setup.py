import os
import subprocess

import setuptools
from pmake import version

from distutils.core import Command
from distutils.command.build import build

from typing import List, Tuple

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# with open("LICENSE.md", "r", encoding="utf-8") as fh:
#     license_value = fh.read()


# creates executable
class generate_executable(Command):

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        if getattr(self, 'dry_run', False):
            return
        # then, generates the executable
        # pyinstaller --hidden-import "colorama"
        # --noconfirm --onefile --name "pmake" --icon "images\icon.ico" "pmake\pmake.py"
        main_script = os.path.abspath(os.path.join("pmake", "main.py"))
        print(f"generating executable of pmake using main {main_script}...")
        PYINSTALLER = [
            "pyinstaller",
            "--hidden-import", "semver",
            "--noconfirm", "--onefile",
            "--distpath", os.path.join("scripts"),
            "--name", "pmake",
            "--icon", os.path.join("images", "icon.ico"),
            main_script
        ]
        print(f"calling {' '.join(PYINSTALLER)}")
        subprocess.call(' '.join(PYINSTALLER), shell=True)
        print(f"Done")


class custom_build(build):
    # plug `build_bootloader` into the `build` command
    def run(self):
        print("generate executable step...")
        self.run_command('generate_executable')
        print("done generate executable...")
        build.run(self)


def get_data_files() -> List[Tuple[str, List[str]]]:
    if os.name == "nt":
        return [
            # put exe into C:\Python38\Scripts
            ("Scripts", [os.path.join("scripts", "pmake.exe")])
        ]
    elif os.name == "posix":
        return [
            # /usr/local/bin
            ("bin", [os.path.join("scripts", "pmake")])
        ]
    else:
        raise InvalidScenarioPMakeException(f"invalid os name {os.name}")


setuptools.setup(
    name="pmake",  # Replace with your own username
    version=version.VERSION,
    author="Massimo Bono",
    author_email="massimobono1@gmail.com",
    description="Library for quickly develop makefile-like files, platform independent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # license=license_value,
    url="https://github.com/Koldar/pmake.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=get_data_files(),
    python_requires='>=3.6',
    cmdclass={
        'generate_executable': generate_executable,
        'build': custom_build,
    },
)
