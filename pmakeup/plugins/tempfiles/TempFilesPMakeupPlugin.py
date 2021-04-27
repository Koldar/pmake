import os
import tempfile
from typing import Iterable, Any

import pmakeup as pm


class TempFilesPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("tempfiles")
    def get_temp_filepath(self, prefix: str = None, suffix: str = None) -> pm.path:
        """
        Get the filename of a temp file. You need to manually create such a temp file

        :param prefix: a prefix the temp file to generate has
        :param suffix: a suffix the temp file to generate has
        :return: the absolute path of the temp path
        """

        fd, result = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)
        return result

    @pm.register_command.add("tempfiles")
    def create_temp_directory_with(self, directory_prefix: str) -> Any:
        """
        Create a temporary directory on the file system where to put temporary files

        :param directory_prefix: a prefix to be put before the temporary folder
        :return: the absolute path of the temporary folder created. The function can be used an input of a "with"
            statement. The folder will be automatically removed at the end of the with.
        """
        return self.platform.create_temp_directory_with(directory_prefix)

    @pm.register_command.add("tempfiles")
    def create_temp_file(self, directory: str, file_prefix: str = None, file_suffix: str = None, mode: str = "r",
                         encoding: str = "utf-8", readable_for_all: bool = False, executable_for_owner: bool = False,
                         executable_for_all: bool = False) -> pm.path:
        """
        Creates the file. You need to manually dispose of the file by yourself

        :param directory: the directory where to put the file
        :param file_prefix: a string that will be put at the beginning of the filename
        :param file_suffix: a string that will be put at the end of the filename
        :param mode: how we will open the file. E.g., "r", "w"
        :param encoding: the encodign of the file. Default to "utf-8"
        :param readable_for_all: if True, the file can be read by anyone
        :param executable_for_owner: if True, the file can be executed by the owner
        :param executable_for_all: if True, anyone can execute the file
        :return: the absolute path of the temp file
        """

        self._log_command(f"Create a temporary file")
        return self.platform.create_temp_file(
            directory=directory,
            file_prefix=file_prefix,
            file_suffix=file_suffix,
            readable_for_all=readable_for_all,
            executable_for_owner=executable_for_owner,
            executable_for_all=executable_for_all
        )


TempFilesPMakeupPlugin.autoregister()
