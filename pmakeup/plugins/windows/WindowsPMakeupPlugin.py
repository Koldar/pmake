# __doc__ = """
# Special commands related to windows
# """
#
# import os
# import winreg
# from typing import Any, Tuple, Iterable
#
# import pmakeup as pm
#
#
# class WindowsPMakeupPlugin(pm.CorePMakeupPlugin):
#
#     def __init__(self, model: "pm.PMakeupModel"):
#         super().__init__(model)
#
#     @pm.show_on_help.add_command('windows')
#     def test_windows(self, string: str):
#         """
#         Test if windows commands is loaded
#         :param string: the string to echo'ed
#         """
#         self.echo(string)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def delete_registry(self, root: str, key_relative_to_root: str, key: str, architecture: int = None) -> bool:
#         """
#         Delete a key in the registry. Is not recursive
#
#         :param root: e.g., winreg.HKEY_CURRENT_USER
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param architecture: architecture to user in the regedit
#         :return: true if the oepration suceeds, false otheriwse
#         """
#
#         key_name = f"{key_relative_to_root}\\{key}"
#         open_key = None
#
#         try:
#             try:
#                 print(f"open_key = {key_name}")
#                 open_key = winreg.OpenKey(root, key_name, 0, winreg.KEY_ALL_ACCESS)
#                 try:
#                     sub_key = winreg.EnumKey(open_key, 0)
#                     print(f"subkey considered is {sub_key}")
#                     winreg.DeleteKeyEx(open_key, sub_key)
#                     return True
#                 except OSError:
#                     pass
#             finally:
#                 if open_key is not None:
#                     winreg.CloseKey(open_key)
#         except FileNotFoundError:
#             architecture = architecture or self.get_architecture()
#             if architecture == 32:
#                 other_architecture = winreg.KEY_WOW64_64KEY
#             elif architecture == 64:
#                 other_architecture = winreg.KEY_WOW64_32KEY
#             else:
#                 raise ValueError(f"Invalid architecture {architecture}!")
#
#             try:
#                 print(f"open_key = {key_name}")
#                 open_key = winreg.OpenKey(root, key_name, 0, winreg.KEY_ALL_ACCESS)
#                 try:
#                     sub_key = winreg.EnumKey(open_key, 0)
#                     print(f"subkey considered is {sub_key}")
#                     winreg.DeleteKeyEx(open_key, sub_key)
#                     return True
#                 except OSError:
#                     pass
#             except FileNotFoundError as e:
#                 raise FileNotFoundError(f"Cannot find the registry key {root}\\{key_relative_to_root}\\{key}")
#             finally:
#                 if open_key is not None:
#                     winreg.CloseKey(open_key)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def delete_registry_from_current_user(self, key_relative_to_root: str, key: str, architecture: int = None) -> bool:
#         """
#         Delete a simple key-value pair in the registry. Is not recursive
#
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param architecture: architecture to user in the regedit
#         """
#         return self.delete_registry(
#             root=winreg.HKEY_CURRENT_USER,
#             key_relative_to_root=key_relative_to_root,
#             key=key,
#             architecture=architecture
#         )
#
#     @pm.show_on_help.add_command('windows-registry')
#     def delete_registry_from_hkey_local_machine(self, key_relative_to_root: str, key: str, architecture: int = None) -> bool:
#         """
#                 Delete a simple key-value pair in the registry. Is not recursive
#
#                 :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#                 :param key: key to generate within root + key_relative_to_root
#                 :param architecture: architecture to user in the regedit
#                 """
#         return self.delete_registry(
#             root=winreg.HKEY_LOCAL_MACHINE,
#             key_relative_to_root=key_relative_to_root,
#             key=key,
#             architecture=architecture
#         )
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry(self, root: str, key_relative_to_root: str, key: str, value_type, value: Any, architecture: int = None) -> bool:
#         """
#         Set a key in the registry
#         :param root: e.g., winreg.HKEY_CURRENT_USER
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value_type: type of the vlaue to create
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         :return: true if the oepration suceeds, false otheriwse
#         """
#
#
#         architecture = architecture or self.get_architecture()
#         if architecture == 32:
#             other_architecture = winreg.KEY_WOW64_64KEY
#         elif architecture == 64:
#             other_architecture = winreg.KEY_WOW64_32KEY
#         else:
#             raise ValueError(f"Invalid architecture {architecture}!")
#
#         try:
#             winreg.CreateKey(root, key_relative_to_root)
#             registry_key = None
#             try:
#                 registry_key = winreg.OpenKey(root, key_relative_to_root, 0, winreg.KEY_WRITE | other_architecture)
#                 winreg.SetValueEx(registry_key, key, 0, value_type, value)
#                 return True
#             finally:
#                 if registry_key is not None:
#                     winreg.CloseKey(registry_key)
#         except WindowsError:
#             return False
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry_as_int(self, root: str, key_relative_to_root: str, key: str, value: int, architecture: int = None) -> bool:
#         """
#         Set a key which is an int.
#
#         :param root: e.g., winreg.HKEY_CURRENT_USER
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         """
#         return self.set_registry(
#             root=root,
#             key_relative_to_root=key_relative_to_root,
#             key=key,
#             value_type=winreg.REG_DWORD,
#             value=str(value),
#             architecture=architecture
#         )
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry_in_current_user_as_int(self, key_relative_to_root: str, key: str, value: int, architecture: int = None) -> bool:
#         """
#         Set a key which is an int inside a current user
#
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         """
#         return self.set_registry_as_int(
#             root=winreg.HKEY_CURRENT_USER,
#             key_relative_to_root=key_relative_to_root,
#             key=key,
#             value=str(value),
#             architecture=architecture
#         )
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry_as_string(self, root: str, key_relative_to_root: str, key: str, value: str, architecture: int = None) -> bool:
#         """
#         Set a key which is an int.
#
#         :param root: e.g., winreg.HKEY_CURRENT_USER
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         """
#         return self.set_registry(root, key_relative_to_root, key, winreg.REG_SZ, str(value), architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry_in_current_user_as_string(self, key_relative_to_root: str, key: str, value: str, architecture: int = None) -> bool:
#         """
#         Set a key which is an int inside a current user
#
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         """
#         return self.set_registry_as_string(winreg.HKEY_CURRENT_USER, key_relative_to_root, key, str(value), architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def set_registry_in_local_machine_as_string(self, key_relative_to_root: str, key: str, value: str,
#                                                architecture: int = None) -> bool:
#         """
#         Set a key which is an int inside a current user
#
#         :param key_relative_to_root: you can use "SOFTWARE\\Microsoft\\Internet Explorer\\Main" to set it to internet explorer
#         :param key: key to generate within root + key_relative_to_root
#         :param value: value to set
#         :param architecture: architecture to user in the regedit
#         """
#         return self.set_registry_as_string(winreg.HKEY_LOCAL_MACHINE, key_relative_to_root, key, str(value),
#                                            architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def get_registry_local_machine_values(self, key: str, architecture: int = None) -> Iterable[Tuple[str, Any]]:
#         yield from self.get_registry_values(winreg.HKEY_LOCAL_MACHINE, key, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def get_registry_current_user_values(self, key: str, architecture: int = None) -> Iterable[Tuple[str, Any]]:
#         yield from self.get_registry_values(winreg.HKEY_CURRENT_USER, key, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def get_registry_values(self, hkey: int, key: str, architecture: int = None) -> Iterable[Tuple[str, Any, int]]:
#         """
#         Get the values of all the key-pair items in a given key
#
#         :param hkey: registry root
#         :param key: key to open
#         :param architecture: architecture of the registry
#         :return: iterable of key-value pairs. The first element is the name of the keyvale, the second is the value
#         associated. The third is the type of the value. see https://docs.python.org/3.9/library/winreg.html?highlight=winreg#value-types
#
#         """
#
#         architecture = architecture or self.get_architecture()
#         if architecture == 32:
#             other_architecture = winreg.KEY_WOW64_64KEY
#         elif architecture == 64:
#             other_architecture = winreg.KEY_WOW64_32KEY
#         else:
#             raise ValueError(f"Invalid architecture {architecture}!")
#
#         with winreg.ConnectRegistry(None, hkey) as reg:
#             try:
#                 # try current architecture
#                 with winreg.OpenKey(reg, key, access=winreg.KEY_READ) as regkey:
#                     i = 0
#                     while True:
#                         try:
#                             reg_key_value = winreg.EnumValue(regkey, i)
#                             i = i + 1
#                             yield reg_key_value[0], reg_key_value[1], reg_key_value[2]
#                         except OSError:
#                             break
#             except FileNotFoundError:
#                 # try the other architectuer
#
#                 try:
#                     with winreg.OpenKey(reg, key, access=winreg.KEY_READ | other_architecture) as regkey:
#                         i = 0
#                         while True:
#                             try:
#                                 reg_key_value = winreg.EnumValue(regkey, i)
#                                 i = i + 1
#                                 yield reg_key_value[0], reg_key_value[1], reg_key_value[2]
#                             except OSError:
#                                 break
#                 except FileNotFoundError:
#                     raise KeyError(f"Cannot find registry key \"{key}\" was not found")
#
#     @pm.show_on_help.add_command('windows-registry')
#     def read_registry_local_machine_value(self, key: str, item: str, architecture: int = None) -> Any:
#         return self.read_registry_value(winreg.HKEY_LOCAL_MACHINE, key, item, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def read_registry_current_user_value(self, key: str, item: str, architecture: int = None) -> Any:
#         return self.read_registry_value(winreg.HKEY_CURRENT_USER, key, item, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def read_registry_value(self, hkey: int, key: str, item: str, architecture: int = None) -> Any:
#         """
#         Get the value associated to a single key-pair value in the given key
#
#         :param key: key to open
#         :param item: name of the key-value pair to obtain
#         :param architecture: architecture of the registry to connect to
#         :return: value associated to the item
#         """
#         return (list(filter(lambda x: x[0] == item, self.get_registry_values(hkey, key, architecture=architecture)))[0])[1]
#
#     @pm.show_on_help.add_command('windows-registry')
#     def has_registry_value(self, hkey: int, key: str, item: str, architecture: int = None) -> bool:
#         """
#         Check if there exists a value in the given key
#
#         :param hkey: root key to access
#         :param key: key involved
#         :param item: key-vaue pair that may or may not exists
#         :return: true if the key-value does not exists in the given `key`
#         """
#         return len(list(filter(lambda x: x[0] == item, self.get_registry_values(hkey, key, architecture=architecture)))) > 0
#
#     @pm.show_on_help.add_command('windows-registry')
#     def has_registry_local_machine_value(self, key: str, item: str, architecture: int = None) -> bool:
#         """
#         Check if there exists a value in the given key
#
#         :param hkey: root key to access
#         :param key: key involved
#         :param item: key-vaue pair that may or may not exists
#         :return: true if the key-value does not exists in the given `key`
#         """
#         return self.has_registry_value(winreg.HKEY_LOCAL_MACHINE, key, item, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows-registry')
#     def has_registry_current_user_value(self, key: str, item: str, architecture: int = None) -> bool:
#         """
#         Check if there exists a value in the given key
#
#         :param hkey: root key to access
#         :param key: key involved
#         :param item: key-vaue pair that may or may not exists
#         :return: true if the key-value does not exists in the given `key`
#         """
#         return self.has_registry_value(winreg.HKEY_CURRENT_USER, key, item, architecture=architecture)
#
#     @pm.show_on_help.add_command('windows')
#     def add_to_regasm(self, dll: pm.path, architecture: int, regasm_exe: pm.path = None, use_codebase: bool = True, use_tlb: bool = True):
#         """
#         Add a dll into a regasm (either 32 or 64 bit)
#         :param regasm_exe: executable of regasm.
#         :param dll: the dll to include in the regasm
#         :param architecture: number of bits the processor has. either 32 or 64
#         :param use_codebase: if set we will add /codebase
#         :param use_tlb: if set, we will add /tlb
#         """
#         cmds = []
#
#         if regasm_exe is None:
#             regasm_exe = self.get_latest_path_with_architecture("regasm", architecture)
#
#         cmds.append(regasm_exe)
#         cmds.append(dll)
#         if use_codebase:
#             cmds.append("/codebase")
#         if use_tlb:
#             cmds.append("/tlb")
#         self.execute_admin_stdout_on_screen(
#             commands=[' '.join(cmds)],
#             cwd=os.path.dirname(dll)
#         )
#
#     @pm.show_on_help.add_command('windows')
#     def remove_from_regasm(self, dll: pm.path, architecture: int, regasm_exe: pm.path = None, use_codebase: bool = True,
#                       use_tlb: bool = True):
#         """
#         Remove a dll into a regasm (either 32 or 64 bit)
#         :param regasm_exe: executable of regasm.
#         :param dll: the dll to include in the regasm
#         :param architecture: number of bits the processor has. either 32 or 64
#         :param use_codebase: if set we will add /codebase
#         :param use_tlb: if set, we will add /tlb
#         """
#         cmds = []
#
#         if regasm_exe is None:
#             regasm_exe = self.get_latest_path_with_architecture("regasm", architecture)
#
#         cmds.append(regasm_exe)
#         cmds.append(dll)
#         if use_codebase:
#             cmds.append("/codebase")
#         if use_tlb:
#             cmds.append("/tlb")
#         cmds.append("/unregister")
#         self.execute_admin_stdout_on_screen(
#             commands=[' '.join(cmds)],
#             cwd=os.path.dirname(dll)
#         )
#
#     @pm.show_on_help.add_command('windows')
#     def publish_dotnet_project(self, cwd: pm.path, runtime: str, configuration: str, solution_directory: pm.path) -> None:
#         """
#         publish a dotnet project.
#         For example:
#
#             echo start "PUBLISHING RUNEXTERNALLY" /D "$(SolutionDir)xplan-subsystem-topshelf-service" /WAIT
#                 dotnet publish
#                 --runtime "$(PublishRuntime)"
#                 --configuration "$(PublishConfiguration)"
#                 /p:SolutionDir="$(SolutionDir)\"
#
#         :param cwd: directory where to call the dotnet publish
#         :param runtime: runtime that you will use to publish. Allowed values are 'x86' or 'x64'
#         :param configuration: configuration used to build the artifact. Allowed values are 'Debug' or 'Release'
#         :param solution_directory: directory containing the a .sln file containing the project that you need to build
#         """
#
#         solution_dir = str(solution_directory)
#         if not solution_dir.endswith(os.sep):
#             solution_dir = solution_dir + os.sep
#
#         self.execute_stdout_on_screen(
#             commands=[' '.join(["dotnet", "publish", "--runtime", runtime, "--configuration", configuration, f"/p:SolutionDir={solution_dir}"])],
#             cwd=cwd,
#         )
