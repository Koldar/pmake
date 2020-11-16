import os
import subprocess
from typing import Union, List, Tuple, Dict

from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath


class LinuxIOSSystem(IOSSystem):

    def _fetch_interesting_paths(self, script: "SessionScript") -> Dict[str, List[InterestingPath]]:
        return {}

    def get_current_username(self) -> str:
        code, stdout, stderr = self.execute("whoami")
        return stdout

    def execute(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True, capture_stdout: bool = True) -> \
    Tuple[int, str, str]:
        if cwd is None:
            cwd = os.curdir
        result = subprocess.run(command, cwd=cwd, shell=use_shell, capture_output=capture_stdout)
        if result.returncode != 0:
            raise ValueError(f"cwd={cwd} command={command} exit={result.returncode}")

        if capture_stdout:
            stdout = self._convert_stdout(result.stdout)
            stderr = self._convert_stdout(result.stderr)
        else:
            stdout = ""
            stderr = ""
        return result.returncode, stdout, stderr

    def execute_admin(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True,
                      capture_stdout: bool = True):
        if cwd is None:
            cwd = os.curdir
        if isinstance(command, str):
            return self.execute(command=f"sudo {command}", cwd=cwd, use_shell=use_shell, capture_stdout=capture_stdout)
        elif isinstance(command, list):
            tmp = ["sudo"]
            tmp.extend(command)
            return self.execute(command=tmp, cwd=cwd, use_shell=use_shell, capture_stdout=capture_stdout)
        else:
            raise TypeError(f"invalid command type {type(command)}")
