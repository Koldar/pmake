import logging
import os
import stat
import subprocess
import tempfile
from typing import Union, List, Tuple, Dict

from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath
from pmake.commons_types import path


class LinuxOSSystem(IOSSystem):

    def get_env_variable(self, name: str) -> str:
        exit_code, stdout, _ = self.execute(
            command=f"printenv {name}",
            use_shell=True,
            capture_stdout=True,
            check_output=False
        )
        if exit_code != 0:
            raise ValueError(f"Cannot find the environment variable \"{name}\" for user \"{self.get_current_username()}\"")

        return stdout.strip()

    def get_home_folder(self) -> path:
        return self.get_env_variable("HOME")

    def _fetch_interesting_paths(self, script: "SessionScript") -> Dict[str, List[InterestingPath]]:
        return {}

    def get_current_username(self) -> str:
        code, stdout, stderr = self.execute("whoami")
        return stdout

    def execute(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True, capture_stdout: bool = True, check_output: bool = True) -> \
    Tuple[int, str, str]:
        if cwd is None:
            cwd = os.curdir
        if isinstance(command, str):
            logging.info(f"exeucting {command}")
        elif isinstance(command, list):
            logging.info(f"executing", {' '.join(command)})
        else:
            raise TypeError(f"Invalid type of command {type(command)}!")

        result = subprocess.run(args=command, cwd=cwd, shell=use_shell, capture_output=capture_stdout)
        if check_output:
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
                      capture_stdout: bool = True, check_output: bool = True):
        if cwd is None:
            cwd = os.curdir
        if isinstance(command, str):
            return self.execute(
                command=f"sudo {command}",
                cwd=cwd,
                use_shell=use_shell,
                capture_stdout=capture_stdout,
                check_output=check_output
            )
        elif isinstance(command, list):
            tmp = ["sudo"]
            tmp.extend(command)
            return self.execute(
                command=tmp,
                cwd=cwd,
                use_shell=use_shell,
                capture_stdout=capture_stdout,
                check_output=check_output
            )
        else:
            raise TypeError(f"invalid command type {type(command)}")

    def execute_admin_with_password(self, command: Union[str, List[str]], password: str, cwd: str = None, use_shell: bool = True, check_output: bool = True) -> str:
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
                    capture_stdout=True,
                    check_output=check_output
                )
                return stdout
            except Exception as e:
                raise e
            finally:
                os.unlink(temp_stdin.name)
                os.unlink(temp_cmd.name)

    def is_program_installed(self, program_name: str) -> bool:
        exit_code, _, _ = self.execute(
            command=f"which {program_name}",
            use_shell=True,
            capture_stdout=True,
            check_output=False
        )
        return exit_code == 0
