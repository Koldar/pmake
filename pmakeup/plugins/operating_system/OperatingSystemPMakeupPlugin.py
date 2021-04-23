import os
from typing import Union, List, Dict, Tuple, Any, Iterable

import pmakeup as pm


class OperatingSystemPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("operating system")
    def is_program_installed(self, program_name: str) -> bool:
        """
        Check if a program is reachable via commandline. We will look **only** in the PATH environment variable.
        If you want to look in other parts as well, conside rusing

        :param program_name: the name of the program (e.g., dot)
        :return: true if there is a program accessible to the PATH with the given name, false otherwise
        """
        self._log_command(f"""Checking if the executable \"{program_name}\" is in PATH""")
        return self.platform.is_program_installed(program_name)

    @pm.register_command.add("operating system")
    def get_program_path(self) -> Iterable[pm.path]:
        """
        List of paths in PATH environment variable

        :return: collections of path
        """
        return self.platform.get_program_path()

    @pm.register_command.add("operating system")
    def current_user(self) -> str:
        """
        get the user currently logged

        :return: the user currently logged
        """
        return self.platform.get_current_username()

    @pm.register_command.add("operating system")
    def execute_and_run_in_background(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None, env: Dict[str, str] = None) -> int:
        """
        Execute a command but ensure that no stdout will be printed on the console

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :return: pid of running process
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_command_and_forget(
            commands=commands,
            cwd=cwd,
            env=env,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_and_forget(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                           env: Dict[str, str] = None, check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command but ensure that no stdout will be printed on the console

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured), the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_command_and_wait(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                                 env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command. We won't capture the stdout but we will show it on pmakeup console

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured), the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_command_and_show_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                              env: Dict[str, Any] = None,
                              check_exit_code: bool = True, timeout: int = None) -> Tuple[int, str, str]:
        """
        Execute a command. We won't show the stdout on pmakeup console but we will capture it and returned it

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured), the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform.fire_command_and_capture_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            log_entry=True
        )
        return exit_code, stdout, stderr

    @pm.register_command.add("operating system")
    def execute_admin_and_run_in_background(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None, env: Dict[str, Any] = None) -> int:
        """
        Execute a command as admin but ensure that no stdout will be printed on the console

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :return: pid of running process
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_admin_command_and_forget(
            commands=commands,
            cwd=cwd,
            env=env,
            credential_type="password",
            credential=None,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_and_forget(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                                 env: Dict[str, Any] = None,
                                 check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command as admin but ensure that no stdout will be printed on the console

        :param commands: the command to execute. They will be exeucte in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured), the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_admin_command_and_wait(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=None,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                                       env: Dict[str, Any] = None,
                                       check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command as an admin. We won't capture the stdout but we will show it on pmakeup console

        :param commands: the command to execute. They will be execute in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured),
            the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_admin_command_and_show_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=None,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]], cwd: pm.path = None,
                                    env: Dict[str, Any] = None,
                                    check_exit_code: bool = True, timeout: int = None) -> Tuple[int, str, str]:
        """
        Execute a command as an admin. We won't show the stdout on pmakeup console but we will capture it and returned it

        :param commands: the command to execute. They will be execute in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured),
            the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform.fire_admin_command_and_capture_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=None,
            log_entry=True
        )
        return exit_code, stdout, stderr

    @pm.register_command.add("operating system")
    def execute_admin_with_password_and_run_in_background(self, commands: Union[str, List[Union[str, List[str]]]], password: str, cwd: pm.path = None,
                                            env: Dict[str, Any] = None) -> int:
        """
        Execute a command as admin but ensure that no stdout will be printed on the console

        :param commands: the command to execute. They will be exeucte in the same context
        :param password: password of the user to invoke the program as an admin
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :return: triple. The first element is the error code, the second is the stdout (if captured), the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform.fire_admin_command_and_forget(
            commands=commands,
            cwd=cwd,
            env=env,
            credential_type="password",
            credential=password,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_with_password_fire_and_forget(self, commands: Union[str, List[Union[str, List[str]]]],
                                                    password: str,
                                                    cwd: pm.path = None, env: Dict[str, Any] = None,
                                                    check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command as admin by providing the admin password. **THIS IS INCREDIBLE UNSAFE!!!!!!!!!!!!**.
        Please, I beg you, do **NOT** use this if you need any level of security!!!!! This will make the password visible
        on top, on the history, everywhere on your system. Please use it only if you need to execute a command on your
        local machine.

        :param commands: the command to execute. They will be executed in the same context
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :param password: **[UNSAFE!!!!]** If you **really** need, you might want to run a command as an admin
            only on your laptop, and you want a really quick and dirty way to execute it, like as in the shell.
            Do **not** use this in production code, since the password will be 'printed in clear basically everywhere!
            (e.g., history, system monitor, probably in a file as well)
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform.fire_admin_command_and_wait(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=password,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_with_password_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]],
                                                     password: str, cwd: pm.path = None, env: Dict[str, Any] = None,
                                                     check_exit_code: bool = True, timeout: int = None) -> int:
        """
        Execute a command as an admin. We won't capture the stdout but we will show it on pmakeup console

        :param commands: the command to execute. They will be execute in the same context
        :param password: **[UNSAFE!!!!]** If you **really** need, you might want to run a command as an admin
            only on your laptop, and you want a really quick and dirty way to execute it, like as in the shell.
            Do **not** use this in production code, since the password will be 'printed in clear basically everywhere!
            (e.g., history, system monitor, probably in a file as well)
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured),
            the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result = self.platform.fire_admin_command_and_show_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=password,
            log_entry=True,
        )
        return result

    @pm.register_command.add("operating system")
    def execute_admin_with_password_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]],
                                                  password: str, cwd: pm.path = None, env: Dict[str, Any] = None,
                                                  check_exit_code: bool = True,
                                                  timeout: int = None) -> Tuple[int, str, str]:
        """
        Execute a command as an admin. We won't show the stdout on pmakeup console but we will capture it and returned it

        :param commands: the command to execute. They will be execute in the same context
        :param password: **[UNSAFE!!!!]** If you **really** need, you might want to run a command as an admin
            only on your laptop, and you want a really quick and dirty way to execute it, like as in the shell.
            Do **not** use this in production code, since the password will be 'printed in clear basically everywhere!
            (e.g., history, system monitor, probably in a file as well)
        :param cwd: current working directory where the command is executed
        :param env: a dictionary representing the key-values of the environment variables
        :param check_exit_code: if true, we will generate an exception if the exit code is different than 0
        :param timeout: if positive, we will give up waiting for the command after the amount of seconds
        :return: triple. The first element is the error code, the second is the stdout (if captured),
            the third is stderr
        """
        if cwd is None:
            cwd = self.paths.cwd()
        else:
            cwd = self.paths.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform.fire_admin_command_and_capture_stdout(
            commands=commands,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            credential_type="password",
            credential=password,
            log_entry=True
        )
        return exit_code, stdout, stderr


OperatingSystemPMakeupPlugin.autoregister()
