from typing import Union, List, Dict, Tuple, Any, Iterable

from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin
from pmakeup.commons_types import path
from pmakeup.decorators import show_on_help


class OpeatingSystemPmakeupPlugin(AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        pass

    @show_on_help.add_command('operating system')
    def execute_and_forget(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=False,
            admin_password=None,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=True,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=False,
            admin_password=None,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=True,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=False,
            admin_password=None,
            log_entry=True
        )
        return exit_code, stdout, stderr

    @show_on_help.add_command('operating system')
    def execute_admin_and_forget(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=None,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_admin_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=True,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=None,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_admin_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]], cwd: path = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=True,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=None,
            log_entry=True
        )
        return exit_code, stdout, stderr

    @show_on_help.add_command('operating system')
    def execute_admin_with_password_fire_and_forget(self, commands: Union[str, List[Union[str, List[str]]]],
                                                    password: str,
                                                    cwd: str = None, env: Dict[str, Any] = None,
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
            cwd = self.cwd()
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=password,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_admin_with_password_stdout_on_screen(self, commands: Union[str, List[Union[str, List[str]]]],
                                                     password: str, cwd: path = None, env: Dict[str, Any] = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        result, _, _ = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=True,
            capture_stdout=False,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=password,
            log_entry=True,
        )
        return result

    @show_on_help.add_command('operating system')
    def execute_admin_with_password_return_stdout(self, commands: Union[str, List[Union[str, List[str]]]],
                                                  password: str, cwd: path = None, env: Dict[str, Any] = None,
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
            cwd = self._cwd
        else:
            cwd = self.abs_path(cwd)

        if isinstance(commands, str):
            commands = [commands]

        exit_code, stdout, stderr = self.platform().execute_command(
            commands=commands,
            show_output_on_screen=False,
            capture_stdout=True,
            cwd=cwd,
            env=env,
            check_exit_code=check_exit_code,
            timeout=timeout,
            execute_as_admin=True,
            admin_password=password,
            log_entry=True
        )
        return exit_code, stdout, stderr

OpeatingSystemPmakeupPlugin.autoregister()