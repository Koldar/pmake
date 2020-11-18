import logging
import os
import stat
import subprocess
import tempfile
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
        if isinstance(command, str):
            logging.info(f"exeucting {command}")
        elif isinstance(command, list):
            logging.info(f"executing", {' '.join(command)})
        else:
            raise TypeError(f"Invalid type of command {type(command)}!")

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

    def execute_admin_with_password(self, command: Union[str, List[str]], password: str, cwd: str = None, use_shell: bool = True) -> str:
        if cwd is None:
            cwd = os.curdir

        if isinstance(command, str):
            command_str = command
        elif isinstance(command, list):
            command_str = ' '.join(command)
        else:
            raise TypeError(f"invalid command type {type(command)}")

        with tempfile.TemporaryDirectory(prefix="pmake_") as temp_dir:
            try:
                with tempfile.NamedTemporaryFile(mode="w", dir=temp_dir, prefix="execute_admin_with_password_", suffix=".bash", delete=False, encoding="utf-8") as temp_cmd:
                    temp_cmd.write("#!/bin/bash\n")
                    temp_cmd.write(command_str)
                    temp_cmd.write("\n")

                with tempfile.NamedTemporaryFile(mode="w", dir=temp_dir, prefix="password_", suffix=".txt", delete=False, encoding="utf-8") as temp_stdin:
                    temp_stdin.write(password)
                    temp_stdin.write("\n")

                os.chmod(temp_cmd.name, 0o505)

                # echo 'password' | sudo -S 'bash -i --login ./file'
                exit_code, stdout, stderr = self.execute(
                    command=f"""cat '{temp_stdin.name}' | sudo --stdin bash '{temp_cmd.name}'""",
                    cwd=temp_dir,
                    use_shell=use_shell,
                    capture_stdout=True
                )
                return stdout
            except Exception as e:
                raise e
            finally:
                os.unlink(temp_stdin.name)
                os.unlink(temp_cmd.name)
