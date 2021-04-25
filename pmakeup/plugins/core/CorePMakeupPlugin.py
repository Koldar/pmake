import logging
import os
import re
import shutil
import stat
import sys
import tempfile
from datetime import datetime

import colorama

import urllib.request
from typing import List, Iterable, Tuple, Any, Callable, Optional

from semantic_version import Version

import configparser
import pmakeup as pm


class CorePMakeupPlugin(pm.AbstractPmakeupPlugin):
    """
    Contains all the commands available for the user in a PMakeupfile.py file
    """

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("core")
    def require_pmakeup_plugins(self, *pmakeup_plugin_names: str):
        """
        Tells pmakeup that, in order to run the script, you required a sequence of pmakeup plugins correctly installed (the version does not matter)

        Pmakeup will then arrange itself in installing dependencies and the correct order of the plugins
        """
        # TODO implement
        raise NotImplementedError()

    @pm.register_command.add("core")
    def vars(self) -> "pm.AttrDict":
        """
        Get a dictioanry containing all the variables setup up to this point.
        You can use thi dictionary to gain access to a variable in a more pythonic way (e.g., vars.foo rather
        than get_variable("foo")

        :raises PMakeupException: if the variable is not found
        """
        return self._model._eval_globals.variables

    @pm.register_command.add("core")
    def log_command(self, message: str):
        """
        reserved. Useful to log the action performed by the user

        :param message: message to log
        """

        if not self.get_variable("disable_log_command"):
            logging.info(message)

    @pm.register_command.add("core")
    def get_all_registered_plugins(self) -> Iterable[str]:
        """
        get all the registered pmakeup plugins at this moment
        """
        return map(lambda p: p.get_plugin_name(), self.get_plugins())

    @pm.register_command.add("core")
    def get_all_available_command_names(self) -> Iterable[str]:
        """
        Get all the commands you can execute right now
        """
        yield from self._model._eval_globals

    @pm.register_command.add("core")
    def get_latest_path_with_architecture(self, current_path: str, architecture: int) -> pm.path:
        """
        get the latest path on the system with the specified archietcture

        :param current_path: nominal path name
        :param architecture: either 32 or 64
        :return: the first path compliant with this path name
        """
        max_x = None
        for x in filter(lambda x: x.architecture == architecture, self._model._eval_globals.pmakeup_interesting_paths[current_path]):
            if max_x is None:
                max_x = x
            elif x.version > max_x.version:
                max_x = x

        return max_x.path

    @pm.register_command.add("core")
    def ensure_condition(self, condition: Callable[[], bool], message: str = "") -> None:
        """
        Perform a check. If the condition is **not** satisfied, we raise exception

        :param condition: the condition to check. generate exception if the result is False
        :param message: the message to show if the exception needs to be generated
        """

        if not condition():
            raise pm.AssertionPMakeupException(f"pmakeup needs to generate a custom exception: {message}")

    @pm.register_command.add("core")
    def ensure_has_variable(self, name: str) -> None:
        """
        Ensure the user has passed a variable via "--variable" CLI utils.
        If not, an exception is generated

        :param name: the variable name to check

        """
        return self.ensure_condition(lambda: name in self.get_shared_variables(), message=f"""No variable passed with "--variable" named "{name}".""")

    @pm.register_command.add("core")
    def semantic_version_2_only_core(self, filename: str) -> Version:
        """
        A function that can be used within ::get_latest_version_in_folder

        :param filename: the absolute path of a file that contains a version
        :return: the version
        """
        regex = r"\d+\.\d+\.\d+"
        b = os.path.basename(filename)
        m = re.search(regex, b)
        logging.debug(f"checking if \"{filename}\" satisfies \"{regex}\"")
        if m is None:
            raise pm.PMakeupException(f"Cannot find the regex {regex} within file \"{b}\"!")
        logging.debug(f"yes: \"{m.group(0)}\"")
        return Version(m.group(0))

    @pm.register_command.add("core")
    def quasi_semantic_version_2_only_core(self, filename: str) -> Version:
        """
        A function that can be used within ::get_latest_version_in_folder.
        It accepts values like "1.0.0", but also "1.0" and "1"

        :param filename: the absolute path of a file that contains a version
        :return: the version
        """
        regex = r"\d+(?:\.\d+(?:\.\d+)?)?"
        b = os.path.basename(filename)
        m = re.search(regex, b)
        if m is None:
            raise pm.PMakeupException(f"Cannot find the regex {regex} within file \"{b}\"!")
        result = m.group(0)
        if len(result.split(".")) == 2:
            result += ".0"
        if len(result.split(".")) == 1:
            result += ".0.0"
        return Version(result)

    @pm.register_command.add("core")
    def get_latest_version_in_folder(self, folder: pm.path = None, should_consider: Callable[[pm.path], bool] = None, version_fetcher: Callable[[str], Version] = None) -> Tuple[Version, List[pm.path]]:
        """
        Scan the subfiles and subfolder of a given directory. We assume each file or folder has a version withint it.
        Then fetches the latest version.
        This command is useful in dierctories where all releases of a given software are placed. if we need to fetch
        the latest one,
        this function is perfect for the task.

        :param folder: the folder to consider. If unspecified, it is the current working directory
        :param should_consider: a function that allows you to determine if we need to consider or
            not a subfile/subfolder. The input isan absolute path. If no function is given, we accept all the
            sub files
        :param version_fetcher: a function that extract a version from the filename. If left unspecified, we will
            use ::semantic_version_2_only_core
        :return: the latest version in the folder. The second element of the tuple is a collection of all the filenames
            that specify the latest version
        """

        def default_should_consider(x) -> bool:
            return True

        if folder is None:
            folder = self.get_cwd()
        if should_consider is None:
            should_consider = default_should_consider
        if version_fetcher is None:
            version_fetcher = self.quasi_semantic_version_2_only_core
        p = self.paths.abs_path(folder)

        result_version = None
        result_list = []
        for file in self.platform.ls(p, generate_absolute_path=True):
            logging.debug(f"Shuld we consider {file} for fetching the latest version?")
            if not should_consider(file):
                continue
            # find the version
            v = version_fetcher(file)
            logging.debug(f"fetched version {v}. Latest version detected up until now is {result_version}")
            if result_version is None:
                result_version = v
                result_list = [file]
                logging.debug(f"update version with {result_version}. Files are {' '.join(result_list)}")
            elif v > result_version:
                result_version = v
                result_list = [file]
                logging.debug(f"update version with {result_version}. Files are {' '.join(result_list)}")
            elif v == result_version:
                result_list.append(file)
                logging.debug(f"update version with {result_version}. Files are {' '.join(result_list)}")

        return result_version, result_list

    def _truncate_string(self, string: str, width: int, ndots: int = 3) -> str:
        if len(string) > (width - ndots):
            return string[:(width-ndots)] + "."*ndots
        else:
            return string

    @pm.register_command.add("core")
    def get_architecture(self) -> int:
        """
        check if the system is designed on a 32 or 64 bits

        :return: either 32 or 64 bit
        """
        is_64 = sys.maxsize > 2**32
        if is_64:
            return 64
        else:
            return 32

    @pm.register_command.add("core")
    def on_windows(self) -> bool:
        """
        Check if we are running on windows

        :return: true if we are running on windows
        """
        self._log_command(f"Checking if we are on a windows system")
        return os.name == "nt"

    @pm.register_command.add("core")
    def on_linux(self) -> bool:
        """
        Check if we are running on linux

        :return: true if we are running on linux
        """
        self._log_command(f"Checking if we are on a linux system")
        return os.name == "posix"

    @pm.register_command.add("core")
    def clear_cache(self):
        """
        Clear the cache of pmakeup
        """
        self._model.pmake_cache.reset()

    @pm.register_command.add("core")
    def set_variable_in_cache(self, name: str, value: Any, overwrite_if_exists: bool = True):
        """
        Set a variable inside the program cache. Setting variable in cache allows pmakeup to
        store information between several runs of pmakeup.

        How pmakeup stores the information is implementation dependent and it should not be relied upon

        :param name: name of the variable to store
        :param value: object to store
        :param overwrite_if_exists: if true, if the cache already contain a variable with the same name, such a varaible will be replaced
            with the new one
        """
        self._log_command(f"Setting {name}={value} in cache")
        self._model.pmake_cache.set_variable_in_cache(
            name=name,
            value=value,
            overwrites_is_exists=overwrite_if_exists
        )

    @pm.register_command.add("core")
    def has_variable_in_cache(self, name: str) -> bool:
        """
        Check if a variable is in the pmakeup cache

        :param name: name of the variable to check
        :return: true if a varaible with such a name is present in the cache, false otherwise
        """
        result = self._model.pmake_cache.has_variable_in_cache(
            name=name
        )
        self._log_command(f"Checking if \"{name}\" is present in the pamkeup cache. It is {'present' if result else 'absent'}")
        return result

    @pm.register_command.add("core")
    def get_variable_in_cache(self, name: str) -> Any:
        """
        Get the variable from the cache. if the variable does not exist, an error is generated

        :param name: name of the variable to check
        :return: the value associated to such a variable
        """
        return self._model.pmake_cache.get_variable_in_cache(
            name=name
        )

    @pm.register_command.add("core")
    def get_variable_in_cache_or_fail(self, name: str) -> Any:
        """
        Get the variable value from the cache or raise an error if it does not exist

        :param name: name of the variable to fetch
        :return: the variable value
        """
        if self._model.pmake_cache.has_variable_in_cache(name):
            return self._model.pmake_cache.get_variable_in_cache(name)
        else:
            raise ValueError(f"Cannot find variable \"{name}\" in pmakeup cache!")

    @pm.register_command.add("core")
    def get_variable_in_cache_or(self, name: str, default: Any) -> Any:
        """
        Get the variable value from the cache or get a default value if it does not exist

        :param name: name of the variable to fetch
        :param default: if the variable does not exist in the cache, the value to retturn from this function
        :return: the variable value
        """
        if self._model.pmake_cache.has_variable_in_cache(name):
            return self._model.pmake_cache.get_variable_in_cache(name)
        else:
            return default

    @pm.register_command.add("core")
    def add_or_update_variable_in_cache(self, name: str, supplier: Callable[[], Any], mapper: Callable[[Any], Any]):
        """
        Add a new variable in the cache

        :param name: the variable to set
        :param supplier: function used to generate the value fo the variable if the variable does not exist in the cache
        :param mapper: function used to generate the value fo the variable if the variable does exist in the cache. The input
            is the variable old value
        """
        if self._model.pmake_cache.has_variable_in_cache(name):
            new_value = mapper(self._model.pmake_cache.get_variable_in_cache(name))
        else:
            new_value = supplier()
        self._log_command(f"Setting {name}={new_value} in cache")
        self._model.pmake_cache.set_variable_in_cache(name, new_value)


    @pm.register_command.add("core")
    def get_starting_cwd(self) -> pm.path:
        """
        :return: absolute path of where you have called pmakeup
        """
        return self._model.starting_cwd

    @pm.register_command.add("core")
    def path_wrt_starting_cwd(self, *folder: str) -> pm.path:
        """
        Compute path relative to the starting cwd

        :param folder: other sections of the path
        :return: path relative to the absolute path of where you have called pmakeup
        """
        return os.path.abspath(os.path.join(self._model.starting_cwd, *folder))

    @pm.register_command.add("core")
    def get_pmakeupfile_path(self) -> pm.path:
        """
        :return: absolute path of the main PMakeupfile path
        """
        return self._model.input_file

    @pm.register_command.add("core")
    def get_pmakeupfile_dir(self) -> pm.path:
        """
        The directory where the analyzed pmakeupfile is located

        :return: absolute ptha of the directory of the path under analysis
        """
        return os.path.dirname(self._model.input_file)

    @pm.register_command.add("core")
    def path_wrt_pmakeupfile(self, *folder: str) -> pm.path:
        """
        Compute path relative to the file where PMakeupfile is located

        :param folder: other sections of the path
        :return: path relative to the absolute path of where PMakeupfile is located
        """
        return os.path.abspath(os.path.join(os.path.dirname(self._model.input_file), *folder))

    @pm.register_command.add("core")
    def get_home_folder(self) -> pm.path:
        """
        Get the home fodler of the currently logged used
        """
        return self.platform.get_home_folder()

    @pm.register_command.add("core")
    def get_pmakeupfile_dirpath(self) -> pm.path:
        """
        :return: absolute path of the folder containing the main PMakeupfile path
        """
        return os.path.dirname(self._model.input_file)

    @pm.register_command.add("core")
    def is_process_running(self, program_name: str) -> bool:
        """
        Check if a program with the given name is currently running

        :param program_name: the program we need to check
        :return: true if we are running such a program, false otheriwse
        """
        return self.platform.is_process_with_name_running(program_name)

    @pm.register_command.add("core")
    def kill_process_by_name(self, program_name: str, ignore_if_process_does_not_exists: bool = True):
        """
        Kill a program

        :param program_name: name fo the program that is running on the system
        :param ignore_if_process_does_not_exists: if the proces does not exist and thsi parameter is true, this
            function will **not** throw exception
        """
        self.platform.kill_process_with_name(
            name=program_name,
            ignore_if_process_does_not_exists=ignore_if_process_does_not_exists
        )

    @pm.register_command.add("core")
    def kill_process_by_pid(self, pid: int, ignore_if_process_does_not_exists: bool = True):
        """
        Kill a program

        :param pid: pid of the program that is running on the system
        :param ignore_if_process_does_not_exists: if the proces does not exist and thsi parameter is true, this
            function will **not** throw exception
        """
        self.platform.kill_process_with_pid(
            pid=pid,
            ignore_if_process_does_not_exists=ignore_if_process_does_not_exists
        )

    @pm.register_command.add("core")
    def require_pmakeup_version(self, lowerbound: str) -> None:
        """
        Check if the current version of pmakeup is greater or equal than the given one.
        If the current version of pmakeup is not compliant with this constraint, an error is generated

        :param lowerbound: the minimum version this script is compliant with
        """
        system_version = Version(pm.version.VERSION)
        script_version = Version(lowerbound)
        self._log_command(f"Checking if script minimum pmakeup version {script_version} >= {system_version}")
        if script_version > system_version:
            raise pm.PMakeupException(f"The script requires at least version {script_version} to be installed. Current version is {system_version}")

    @pm.register_command.add("core")
    def get_command_line_string(self) -> str:
        """
        Get the command line string from the user

        :return: argv
        """
        return " ".join(sys.argv)

    @pm.register_command.add("core")
    def read_variables_from_properties(self, file: pm.path, encoding: str = "utf-8") -> None:
        """
        Read a set of easy variables from a property file. All the read variables will be available in the "variables"
        value. If some variable name preexists, it will not be overriden
        :see: https://docs.oracle.com/cd/E23095_01/Platform.93/ATGProgGuide/html/s0204propertiesfileformat01.html

        :param file: the file to read
        :param encoding: encoding of the file. If left missing, we will use utf-8
        """

        p = self.paths.abs_path(file)
        self._log_command(f"Reading variables from property file {p}")
        config = configparser.ConfigParser()
        # see https://stackoverflow.com/a/19359720/1887602
        config.optionxform = str
        with open(p, "r", encoding=encoding) as f:
            config.read_string("[config]\n" + f.read())

        for k, v in config["config"].items():
            if k in self.get_shared_variables():
                logging.warning(f"Ignoring variable \"{k}\" from file {p}, since it alrady exist within the ambient")
                continue
            self._log_command(f"Adding variable \"{k}\" to {v}")
            self.get_shared_variables()[k] = v

    @pm.register_command.add("core")
    def include_string(self, string: str) -> None:
        """
        Include and execute the code within the given string

        :param string: the commands to execute
        """
        self._log_command(f"Include and execute string \"{string}\"")
        self._model.execute_string(string)

    @pm.register_command.add("core")
    def include_file(self, *file: pm.path) -> None:
        """
        Replace the include directive with the content fo the included file. Fails if there is no such path

        :param file: the external file to include in the script
        """

        p = self.paths.abs_path(*file)
        self._log_command(f"include file content \"{p}\"")
        self._model.execute_file(p)


CorePMakeupPlugin.autoregister()
