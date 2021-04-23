import os
from typing import Iterable

from semantic_version import Version

import pmakeup as pm


class PathsPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("paths")
    def get_relative_path_wrt(self, p: pm.path, reference: pm.path) -> pm.path:
        """
        If we were in folder reference, what actiosn should we perform in order to reach the file p?

        :param p: the file to reach
        :param reference: the folder we are in right now
        :return: relative path
        """
        return os.path.relpath(path=p, start=reference)

    @pm.register_command.add("paths")
    def get_file_without_extension(self, *p: pm.path) -> pm.path:
        """
        Compute the filename without its last extension

        /path/to/some/file.txt.zip.asc --> /path/to/some/file.txt.zip

        :param p: path to consider
        :return: same absolute path, without extension
        """
        return os.path.splitext(self._abs_wrt_cwd(*p))[0]

    @pm.register_command.add("paths")
    def get_basename(self, *p) -> pm.path:
        """
        Compute the base name of the path

        /path/to/file.txt.zp.asc -> file.txt.zp.asc

        :param p: path to consider
        :return: basename
        """
        return os.path.basename(self._abs_wrt_cwd(*p))

    @pm.register_command.add("paths")
    def get_extension(self, *p) -> pm.path:
        """
        Compute the extension of a file

        :param p: the file to consider
        :return the fiel extension
        """
        f = self._abs_wrt_cwd(*p)
        return os.path.splitext(f)[1].lstrip('.')

    @pm.register_command.add("paths")
    def get_basename_with_no_extension(self, *p) -> pm.path:
        """
        Compute the basename of the path and remove its extension as well

        /path/to/file.txt.zp.asc -> file.txt.zp

        :param p: path to consider
        :return: basename
        """
        return os.path.splitext(self.get_basename(*p))[0]

    @pm.register_command.add("paths")
    def change_filename_extension(self, new_extension: str, *p) -> pm.path:
        """
        Change the extension of the given path

        new extensions: dat
        /path/to/file.txt.zp.asc -> /path/to/file.txt.zp.dat

        :param new_extension: extension that will be set
        :param p: path to chan
        :return: p, but with the updated extensions
        """
        s = self._abs_wrt_cwd(*p)
        return self._abs_wrt_cwd(os.path.splitext(s)[0] + "." + new_extension)

    @pm.register_command.add("paths")
    def get_parent_directory(self, *p) -> pm.path:
        """
        Retrieve the absolute path of the parent directory of the specified path.

        /foo/tbar/tmp.txt -> /foo/tbar

        :param p: path to consider
        :return: parent directory of path
        """

        return self._abs_wrt_cwd(self._abs_wrt_cwd(*p), os.pardir)

    @pm.register_command.add("paths")
    def path(self, *p: str) -> pm.path:
        """
        Generate a path compliant wit the underlying operating system path scheme.

        If the path is relative, we will **not** join it with cwd

        :param p: the path to build
        """

        return os.path.join(*p)

    @pm.register_command.add("paths")
    def abs_path(self, *p: path) -> pm.path:
        """
        Generate a path compliant with the underlying operating system path scheme.

        If the path is relative, it is relative to the cwd

        :param p: the path to build
        """
        actual_path = os.path.join(*p)
        if os.path.isabs(actual_path):
            return os.path.abspath(actual_path)
        else:
            return os.path.abspath(os.path.join(self.get_cwd(), actual_path))

    @pm.register_command.add("paths")
    def cwd(self) -> pm.path:
        """

        :return: the CWD the commands operates in
        """
        return os.path.abspath(self.get_cwd())

    @pm.register_command.add("paths")
    def cd(self, *folder: pm.path, create_if_not_exists: bool = True) -> pm.path:
        """
        Gain access to a directory. If the directory does nto exists, it is created
        If the path is relative, it is relative to the CWD

        :param folder: folder where we need to go into
        :param create_if_not_exists: if true, we will create the directory if we try to cd into a non existent directory
        :return: the directory where we have cd from
        """
        result = self.get_cwd()
        actual_folder = os.path.join(*folder)
        p = self.abs_path(actual_folder)
        self._log_command(f"""cd into folder \"{p}\"""")
        self.set_cwd(p)
        if not os.path.exists(self.get_cwd()) and create_if_not_exists:
            os.makedirs(self.get_cwd(), exist_ok=True)
        return result

    @pm.register_command.add("paths")
    def cd_into_directories(self, folder: pm.path, prefix: str, folder_format: str, error_if_mismatch: bool = True):
        """
        Inside the given folder, there can be several folders, each of them with the same format. We cd into the "latest" one.
        How can we determine which is the "latest" one? Via folder_format. it is a string that is either:
        - "number": an integer number
        - "semver2": a semantic versionign string;
        We fetch the "latest" by looking at the one with the greater value. If the folder contains a folder which it is not compliant
        with folder_format, it is either ignored or rase error

        :param folder: folder where several folders are located
        :param prefix: a string that prefix folder_format
        :param folder_format: either "number" or "semver2"
        :param error_if_mismatch: if a folder is not compliant with folder_format, if true we will generate an exception
        :return:
        """

        try:
            p = self.abs_path(folder)
            self._log_command(f"Cd'ing into the \"latest\" directory in folder \"{p}\" according to criterion \"{folder_format}\"")
            self._disable_log_command = True
            self.cd(folder)

            folders = dict()
            for subfolder in self.files.ls_only_directories(p):
                if not subfolder.startswith(prefix):
                    if error_if_mismatch:
                        raise pm.PMakeupException(f"subfolder \"{subfolder}\" in \"{p}\" does not start with \"{prefix}\"")
                    else:
                        continue

                subfolder_id = subfolder[len(prefix):]
                try:
                    if folder_format == "semver2":
                        folders[Version(subfolder_id)] = subfolder
                    elif folder_format == "number":
                        folders[int(subfolder_id)] = subfolder
                    else:
                        raise pm.InvalidScenarioPMakeupException(f"invalid folder_format \"{folder_format}\"")
                except Exception as e:
                    if error_if_mismatch:
                        raise e
                    else:
                        continue

            # fetch the "latest" by fetching the greater value in "folders"
            latest_folder = list(sorted(folders.keys()))[0]
            self.cd(folders[latest_folder])
        finally:
            self._disable_log_command = False


PathsPMakeupPlugin.autoregister()
