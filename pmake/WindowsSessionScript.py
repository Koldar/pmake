__doc__ = """
Special commands related to windows
"""

import os
import winreg
from typing import Any, Tuple, Iterable

from pmake import show_on_help
from pmake.SessionScript import SessionScript, path


class WindowsSessionScript(SessionScript):

    def __init__(self, model: "PMakeModel.PMakeMode"):
        super().__init__(model)

    @show_on_help.add_command('windows')
    def test_windows(self, string: str):
        """
        Test if windows commands is loaded
        :param string: the string to echo'ed
        """
        self.echo(string)

    @show_on_help.add_command('windows-registry')
    def get_registry_local_machine_values(self, key: str, architecture: int = None) -> Iterable[Tuple[str, Any]]:
        yield from self.get_registry_values(winreg.HKEY_LOCAL_MACHINE, key, architecture=architecture)

    @show_on_help.add_command('windows-registry')
    def get_registry_current_user_values(self, key: str, architecture: int = None) -> Iterable[Tuple[str, Any]]:
        yield from self.get_registry_values(winreg.HKEY_CURRENT_USER, key, architecture=architecture)

    @show_on_help.add_command('windows-registry')
    def get_registry_values(self, hkey: int, key: str, architecture: int = None) -> Iterable[Tuple[str, Any, int]]:
        """
        Get the values of all the key-pair items in a given key

        :param hkey: registry root
        :param key: key to open
        :param architecture: architecture of the registry
        :return: iterable of key-value pairs. The first element is the name of the keyvale, the second is the value
        associated. The third is the type of the value. see https://docs.python.org/3.9/library/winreg.html?highlight=winreg#value-types

        """

        architecture = architecture or self.get_architecture()
        if architecture == 32:
            other_architecture = winreg.KEY_WOW64_64KEY
        elif architecture == 64:
            other_architecture = winreg.KEY_WOW64_32KEY
        else:
            raise ValueError(f"Invalid architecture {architecture}!")

        with winreg.ConnectRegistry(None, hkey) as reg:
            try:
                # try current architecture
                with winreg.OpenKey(reg, key, access=winreg.KEY_READ) as regkey:
                    i = 0
                    while True:
                        try:
                            reg_key_value = winreg.EnumValue(regkey, i)
                            i = i + 1
                            yield reg_key_value[0], reg_key_value[1], reg_key_value[2]
                        except OSError:
                            break
            except FileNotFoundError:
                # try the other architectuer

                try:
                    with winreg.OpenKey(reg, key, access=winreg.KEY_READ | other_architecture) as regkey:
                        i = 0
                        while True:
                            try:
                                reg_key_value = winreg.EnumValue(regkey, i)
                                i = i + 1
                                yield reg_key_value[0], reg_key_value[1], reg_key_value[2]
                            except OSError:
                                break
                except FileNotFoundError:
                    raise KeyError(f"Cannot find registry key \"{key}\" was not found")

    @show_on_help.add_command('windows-registry')
    def read_registry_local_machine_value(self, key: str, item: str, architecture: int = None) -> Any:
        return self.read_registry_value(winreg.HKEY_LOCAL_MACHINE, key, item, architecture=architecture)

    @show_on_help.add_command('windows-registry')
    def read_registry_current_user_value(self, key: str, item: str, architecture: int = None) -> Any:
        return self.read_registry_value(winreg.HKEY_CURRENT_USER, key, item, architecture=architecture)

    @show_on_help.add_command('windows-registry')
    def read_registry_value(self, hkey: int, key: str, item: str, architecture: int = None) -> Any:
        """
        Get the value associated to a single key-pair value in the given key

        :param key: key to open
        :param item: name of the key-value pair to obtain
        :param architecture: architecture of the registry to connect to
        :return: value associated to the item
        """
        return (list(filter(lambda x: x[0] == item, self.get_registry_values(hkey, key, architecture=architecture)))[0])[1]

    @show_on_help.add_command('windows-registry')
    def has_registry_value(self, hkey: int, key: str, item: str, architecture: int = None) -> bool:
        """
        Check if there exists a value in the given key

        :param hkey: root key to access
        :param key: key involved
        :param item: key-vaue pair that may or may not exists
        :return: true if the key-value does not exists in the given `key`
        """
        return len(list(filter(lambda x: x[0] == item, self.get_registry_values(hkey, key, architecture=architecture)))) > 0

    @show_on_help.add_command('windows-registry')
    def has_registry_local_machine_value(self, key: str, item: str, architecture: int = None) -> bool:
        """
        Check if there exists a value in the given key

        :param hkey: root key to access
        :param key: key involved
        :param item: key-vaue pair that may or may not exists
        :return: true if the key-value does not exists in the given `key`
        """
        return self.has_registry_value(winreg.HKEY_LOCAL_MACHINE, key, item, architecture=architecture)

    @show_on_help.add_command('windows-registry')
    def has_registry_current_user_value(self, key: str, item: str, architecture: int = None) -> bool:
        """
        Check if there exists a value in the given key

        :param hkey: root key to access
        :param key: key involved
        :param item: key-vaue pair that may or may not exists
        :return: true if the key-value does not exists in the given `key`
        """
        return self.has_registry_value(winreg.HKEY_CURRENT_USER, key, item, architecture=architecture)

    @show_on_help.add_command('windows')
    def add_to_regasm(self, dll: path, architecture: int, regasm_exe: path = None, use_codebase: bool = True, use_tlb: bool = True):
        """
        Add a dll into a regasm (either 32 or 64 bit)
        :param regasm_exe: executable of regasm.
        :param dll: the dll to include in the regasm
        :param architecture: number of bits the processor has. either 32 or 64
        :param use_codebase: if set we will add /codebase
        :param use_tlb: if set, we will add /tlb
        """
        cmds = []

        if regasm_exe is None:
            regasm_exe = self.get_latest_path_with_architecture("regasm", architecture)

        cmds.append(regasm_exe)
        cmds.append(dll)
        if use_codebase:
            cmds.append("/codebase")
        if use_tlb:
            cmds.append("/tlb")
        self.execute_admin_stdout_on_screen(
            commands=[' '.join(cmds)],
            cwd=os.path.dirname(dll)
        )

    @show_on_help.add_command('windows')
    def publish_dotnet_project(self, cwd: path, runtime: str, configuration: str, solution_directory: path) -> None:
        """
        publish a dotnet project.
        For example:

            echo start "PUBLISHING RUNEXTERNALLY" /D "$(SolutionDir)xplan-subsystem-topshelf-service" /WAIT
                dotnet publish
                --runtime "$(PublishRuntime)"
                --configuration "$(PublishConfiguration)"
                /p:SolutionDir="$(SolutionDir)\"

        :param cwd: directory where to call the dotnet publish
        :param runtime: runtime that you will use to publish. Allowed values are 'x86' or 'x64'
        :param configuration: configuration used to build the artifact. Allowed values are 'Debug' or 'Release'
        :param solution_directory: directory containing the a .sln file containing the project that you need to build
        """

        solution_dir = str(solution_directory)
        if not solution_dir.endswith(os.sep):
            solution_dir = solution_dir + os.sep

        self.execute_stdout_on_screen(
            commands=[' '.join(["dotnet", "publish", "--runtime", runtime, "--configuration", configuration, f"/p:SolutionDir={solution_dir}"])],
            cwd=cwd,
        )
