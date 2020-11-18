import os
import subprocess
import tempfile
import time
from typing import Union, List, Tuple, Dict, Any

import semver

from pmake import commands
from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath


class WindowsIOSSystem(IOSSystem):

    def _fetch_interesting_paths(self, script: "commands.SessionScript") -> Dict[str, List[InterestingPath]]:

        # <Regasm32>C:\Windows\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe</Regasm32>
        # <Regasm64>C:\Windows\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe</Regasm64>
        # fetch regasm

        interesting_paths = {}
        architecture = script.get_architecture()

        # REGASM
        folder32 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework")
        folder64 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework64")

        if "regasm" not in interesting_paths:
            interesting_paths["regasm"] = []

        if os.path.isdir(folder32):
            # subfolder ris something like v1.2.3
            for subfolder in script.ls_only_directories(folder32):
                interesting_paths["regasm"].append(InterestingPath(
                    architecture=architecture,
                    path=script.abs_wrt_cwd(folder32, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        if os.path.isdir(folder64):
            # subfolder ris something like v1.2.3
            for subfolder in script.ls_only_directories(folder64):
                interesting_paths["regasm"].append(InterestingPath(
                    architecture=architecture,
                    path=script.abs_wrt_cwd(folder64, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        return interesting_paths

    def get_current_username(self) -> str:
        code, stdout, stderr = self.execute("whoami")
        return stdout.split("\\")[1]

    def execute(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True, capture_stdout: bool = True) -> \
    Tuple[int, str, str]:
        if cwd is None:
            cwd = os.curdir
        result = subprocess.run(command, cwd=cwd, shell=use_shell, capture_output=capture_stdout)
        if result.returncode != 0:
            raise ValueError(f"cwd=\"{cwd}\" command=\"{command}\" exit=\"{result.returncode}\"")

        if capture_stdout:
            stdout = self._convert_stdout(result.stdout)
            stderr = self._convert_stdout(result.stderr)
        else:
            stdout = ""
            stderr = ""
        return result.returncode, stdout, stderr

    def execute_admin(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True,
                      capture_stdout: bool = True):

        stdout_filename = os.path.abspath(os.path.join(cwd, "stdout.txt"))
        stderr_filename = os.path.abspath(os.path.join(cwd, "stderr.txt"))

        if cwd is None:
            cwd = os.curdir

        if isinstance(command, str):
            cmds = command.split()
            command_name = cmds[0]
            args = ' '.join(map(lambda x: f"{x}", cmds[1:]))
        elif isinstance(command, list):
            command_name = command[0]
            args = ','.join(map(lambda x: f"'{x}'", command[1:]))
        else:
            raise TypeError(f"invalid command type {type(command)}")

        with tempfile.TemporaryDirectory(prefix="pmake_") as temp_dir:
            with tempfile.NamedTemporaryFile(delete=False, prefix="cmd_", suffix=".bat", dir=temp_dir, mode="w") as temp_bat:
                temp_bat.write(f"{command_name} {args}")
                if capture_stdout:
                    temp_bat.write(f" 2>&1 > {stdout_filename}")
                temp_bat.write("\n")
                temp_bat.flush()
                temp_filename = temp_bat.name

            returncode, stdout, stderr = self.execute(
                command=f"""powershell -Command \"Start-Process -FilePath '{temp_filename}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\"""",
                cwd=cwd,
                use_shell=use_shell,
                capture_stdout=capture_stdout
            )
            # this generates stdout and stderr
            stdout = ""
            stderr = ""
            if capture_stdout:
                if os.path.exists(stdout_filename):
                    with open(stdout_filename, "r") as f:
                        stdout = self._convert_stdout(f.read())
                if os.path.exists(stderr_filename):
                    with open(stderr_filename, "r") as f:
                        stderr = self._convert_stdout(f.read())

            return returncode, stdout, stderr

    def execute_admin_with_password(self, command: Union[str, List[str]], password: str, cwd: str = None, use_shell: bool = True) -> str:
        raise NotImplemented()

    def is_program_installed(self, program_name: str) -> bool:
        raise NotImplemented()
