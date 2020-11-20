import logging
import os
import subprocess
from typing import Union, List, Tuple, Dict

from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath
from pmake.commons_types import path
from pmake.exceptions.PMakeException import PMakeException


class LinuxOSSystem(IOSSystem):

    def execute_command(self, commands: List[Union[str, List[str]]], show_output_on_screen: bool, capture_stdout: bool,
                        cwd: str = None, env: Dict[str, str] = None, check_exit_code: bool = True, timeout: int = None,
                        execute_as_admin: bool = False, admin_password: str = None,
                        log_entry: bool = False) -> Tuple[int, str, str]:

        if env is None:
            env = {}

        # create tempfile
        with self.create_temp_directory_with("pmake-command-") as absolute_temp_dir:
            filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".bash", executable_for_owner=True)
            with open(filepath, "w") as f:
                # put the commands in the temp file
                f.write("#!/bin/bash\n")

                for cmd in commands:
                    if isinstance(cmd, str):
                        cmd_str = cmd
                    elif isinstance(cmd, list):
                        cmd_str = ' '.join(cmd)
                    else:
                        raise TypeError(f"Invalid type of command {type(cmd)}!")
                    f.write(cmd_str)
                    f.write("\n")

            stdout_filepath = os.path.join(absolute_temp_dir, "stdout.txt")
            stderr_filepath = os.path.join(absolute_temp_dir, "stderr.txt")

            # Now execute file
            if execute_as_admin:
                if admin_password:
                    password_file = self.create_temp_file(directory=absolute_temp_dir, file_prefix="stdin-")
                    with open(password_file, "w") as f:
                        f.write(f"{admin_password}\n")

                    if show_output_on_screen and capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo --stdin bash '{filepath}'"""
                        actual_capture_output = True
                        actual_read_stdout = False
                    elif show_output_on_screen and not capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo --stdin bash '{filepath}'"""
                        actual_capture_output = False
                        actual_read_stdout = False
                    elif not show_output_on_screen and capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo --stdin bash '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                        actual_capture_output = False
                        actual_read_stdout = True
                    else:
                        actual_command = f"""cat '{password_file}' | sudo --stdin bash '{filepath}' 2>&1 > /dev/null"""
                        actual_capture_output = False
                        actual_read_stdout = False

                else:
                    env_part = ' '.join(map(lambda k: f"{k}='{env[k]}'", env))

                    if show_output_on_screen and capture_stdout:
                        actual_command = f"""sudo --preserve-env {env_part} --login --shell bash '{filepath}'"""
                        actual_capture_output = True
                        actual_read_stdout = False
                    elif show_output_on_screen and not capture_stdout:
                        actual_command = f"""sudo --preserve-env {env_part} --login --shell bash '{filepath}'"""
                        actual_capture_output = False
                        actual_read_stdout = False
                    elif not show_output_on_screen and capture_stdout:
                        actual_command = f"""sudo --preserve-env {env_part} --login --shell bash '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                        actual_capture_output = False
                        actual_read_stdout = True
                    else:
                        actual_command = f"""sudo --preserve-env {env_part} --login --shell bash '{filepath}' 2>&1 > /dev/null"""
                        actual_capture_output = False
                        actual_read_stdout = False

            else:
                env_part = ' ; '.join(map(lambda k: f"{k}='{env[k]}'", env))
                if len(env) > 0:
                    env_part += " ; "

                if show_output_on_screen and capture_stdout:
                    actual_command = f"""{env_part}bash --login '{filepath}'"""
                    actual_capture_output = True
                    actual_read_stdout = False
                elif show_output_on_screen and not capture_stdout:
                    actual_command = f"""{env_part}bash --login '{filepath}'"""
                    actual_capture_output = False
                    actual_read_stdout = False
                elif not show_output_on_screen and capture_stdout:
                    actual_command = f"""{env_part}bash --login '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                    actual_capture_output = False
                    actual_read_stdout = True
                else:
                    actual_command = f"""{env_part}bash --login '{filepath}' 2>&1 > /dev/null"""
                    actual_capture_output = False
                    actual_read_stdout = False

            if log_entry:
                log_method = logging.critical
            else:
                log_method = logging.debug
            log_method(f"Executing {actual_command}")
            with open(filepath, "r") as f:
                log_method(f"in file \"{filepath}\" = \n{f.read()}")

            result = subprocess.run(
                args=actual_command,
                cwd=cwd,
                shell=True,
                capture_output=actual_capture_output,
                timeout=timeout,
                env=env
            )

            if check_exit_code and result.returncode != 0:
                raise PMakeException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")

            if actual_capture_output:
                stdout = self._convert_stdout(result.stdout)
                stderr = self._convert_stdout(result.stderr)
            elif actual_read_stdout:
                with open(stdout_filepath) as f:
                    stdout = self._convert_stdout(f.read())
                with open(stderr_filepath) as f:
                    stderr = self._convert_stdout(f.read())
            else:
                stdout = ""
                stderr = ""

            return result.returncode, stdout, stderr

    def get_env_variable(self, name: str) -> str:
        exit_code, stdout, _ = self.execute_command(
            commands=[f"printenv {name}"],
            capture_stdout=True,
            show_output_on_screen=False,
            check_exit_code=False,
        )
        if exit_code != 0:
            raise PMakeException(f"Cannot find the environment variable \"{name}\" for user \"{self.get_current_username()}\"")

        return stdout.strip()

    def get_home_folder(self) -> path:
        return self.get_env_variable("HOME")

    def _fetch_interesting_paths(self, script: "SessionScript") -> Dict[str, List[InterestingPath]]:
        return {}

    def get_current_username(self) -> str:
        code, stdout, stderr = self.execute_command(
            commands=["whoami"],
            show_output_on_screen=False,
            capture_stdout=True,
        )
        return stdout

    def is_program_installed(self, program_name: str) -> bool:
        exit_code, _, _ = self.execute_command(
            commands=[f"which {program_name}"],
            show_output_on_screen=False,
            capture_stdout=True,
            check_exit_code=False
        )
        return exit_code == 0
