import abc
import inspect
import logging
import os
import re
import shutil
import stat
import sys

import colorama
import urllib.request
from typing import List, Union, Iterable, Tuple, Any, Dict

import semver as semver

from pmake.InterestingPath import InterestingPath
from pmake.LinuxOSSystem import LinuxIOSSystem
from pmake.WindowsOSSystem import WindowsIOSSystem
from pmake.commons_types import path


class SessionScript(abc.ABC):

    def __init__(self, model: "PMakeModel"):
        self._model = model
        self._cwd = os.path.abspath(os.curdir)
        self._locals = {}
        self._foreground_mapping = {
            "RED": colorama.Fore.RED,
            "GREEN": colorama.Fore.GREEN,
            "YELLOW": colorama.Fore.YELLOW,
            "BLUE": colorama.Fore.BLUE,
            "MAGENTA": colorama.Fore.MAGENTA,
            "CYAN": colorama.Fore.CYAN,
            "WHITE": colorama.Fore.WHITE,
        }
        self._background_mapping = {
            "RED": colorama.Back.RED,
            "GREEN": colorama.Back.GREEN,
            "YELLOW": colorama.Back.YELLOW,
            "BLUE": colorama.Back.BLUE,
            "MAGENTA": colorama.Back.MAGENTA,
            "CYAN": colorama.Back.CYAN,
            "WHITE": colorama.Back.WHITE,
        }
        self._disable_log_command: bool = False
        if self.on_windows():
            self._platform = WindowsIOSSystem()
        elif self.on_linux():
            self._platform = LinuxIOSSystem()
        else:
            raise ValueError(f"Cannot identify platform!")

        # fetches the interesting paths
        self.interesting_paths = self._platform._fetch_interesting_paths(self)
        self.latest_interesting_path = self._platform._fetch_latest_paths(self, self.interesting_paths)

    def get_latest_path_with_architecture(self, current_path: str, architecture: int) -> path:
        """
        get the latest path on the system with the specified archietcture
        :param current_path: nominal path name
        :param architecture: either 32 or 64
        :return: the first path compliant with this path name
        """
        max_x = None
        for x in filter(lambda x: x.architecture == architecture, self.interesting_paths[current_path]):
            if max_x is None:
                max_x = x
            elif x.version > max_x.version:
                max_x = x

        return max_x.path

    @staticmethod
    def _list_all_commands() -> Iterable[Tuple[str, str]]:

        def get_str(t: Any) -> str:
            if hasattr(t, "__name__"):
                return t.__name__
            else:
                return str(t)

        for command_name in filter(lambda x: not x.startswith("_"), dir(SessionScript)):
            method = getattr(SessionScript, command_name)
            fullargspec = inspect.getfullargspec(method)
            arg_tmp = []
            if 'return' in fullargspec.annotations:
                result_type = get_str(fullargspec.annotations["return"])
            else:
                result_type = "None"
            for x in fullargspec.args[1:]:
                if x in fullargspec.annotations:
                    param_type = get_str(fullargspec.annotations[x])
                else:
                    param_type = "Any"
                arg_tmp.append(f"{x}: {param_type}")
            method_signature = f"{command_name} ({', '.join(arg_tmp)}) -> {result_type}"

            yield method_signature, method.__doc__

    def _color_str(self, message: str, foreground: str = None, background: str = None) -> str:
        """
        Color a string
        :param message: string involved
        :param foreground: foreground color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :param background: background color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :return: colored string
        """
        result = ""
        should_reset = False
        if foreground is not None:
            result += str(self._foreground_mapping[foreground])
            should_reset = True
        if background is not None:
            result += str(self._background_mapping[background])
            should_reset = True
        result += str(message)
        if should_reset:
            result += colorama.Style.RESET_ALL

        return result

    def _truncate_string(self, string: str, width: int, ndots: int = 3) -> str:
        if len(string) > (width - ndots):
            return string[:(width-ndots)] + "."*ndots
        else:
            return string

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

    def on_windows(self) -> bool:
        """
        Check if we are running on windows
        :return: true if we are running on windows
        """
        self._log_command(f"Checking if we are on a windows system")
        return os.name == "nt"

    def on_linux(self) -> bool:
        """
        Check if we are running on linux
        :return: true if we are running on linux
        """
        self._log_command(f"Checking if we are on a linux system")
        return os.name == "posix"

    def echo(self, message: str, foreground: str = None, background: str = None):
        """
        Print a message on the screen
        :param message: the message to print out
        :param foreground: foreground color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        :param background: background color of the string. Accepted values: RED, GREEN, YELLOW, BLUE, MAGENT, CYAN, WHITE
        """

        self._log_command(f"""echo \"{message}\"""")
        print(self._color_str(message, foreground, background))

    def _log_command(self, message: str):
        """
        reserved. Useful to log the action performed by the user
        :param message: message to log
        """
        if not self._disable_log_command:
            logging.info(message)

    def info(self, message: str):
        """
        Log a message using 'INFO' level
        :param message: the message to log
        """
        logging.info(message)

    def critical(self, message: str):
        """
        Log a message using 'CRITICAL' level
        :param message: the message to log
        """
        logging.critical(message)

    def debug(self, message: str):
        """
        Log a message using 'DEBUG' level
        :param message: the message to log
        """
        logging.debug(message)

    def create_empty_file(self, name: path, encoding: str = "utf-8"):
        """
        Create an empty file. if the file is relative, it is relative to the CWD
        :param name: file name to create
        :param encoding: encoding of the file. If unspecified, it is utf-8
        """
        p = self.get_path(name)
        self._log_command(f"Creating empty file {p}")
        with open(p, "w", encoding=encoding) as f:
            pass

    def create_empty_directory(self, name: path):
        """
        Create an empty directory in the CWD (if the path is relative)
        :param name:the name of the driectory to create
        """
        p = self.get_path(name)
        os.makedirs(name=p, exist_ok=True)

    def is_file_exists(self, name: path) -> bool:
        """
        Check if a file exists
        :param name: file whose existence we need to assert
        :return: true if the file exists, false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"Checking if the file {p} exists")
        return os.path.exists(p)

    def is_file_empty(self, name: path) -> bool:
        """
        Checks if a file exists. If exists, check if it empty as well.
        :param name: file to check
        :return: true if the file exists **and** has no bytes; false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"Checking if the file {p} exists and is empty")
        if not os.path.exists(p):
            return False
        with open(p, "r") as f:
            return f.read(1) == ""

    def is_directory_exists(self, name: path) -> bool:
        """
        Check if a directory exists.
        :param name: folder to check
        :return: true if the folder exists, false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"Checking if the folder {p} exists")
        if os.path.exists(p) and os.path.isdir(p):
            return True
        return False

    def is_directory_empty(self, name: path) -> bool:
        """
        Check if a directory exists and is empty
        :param name: folder to check
        :return: true if the folder exists and is empty, false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"Checking if the folder {p} exists and is empty")
        if os.path.exists(p) and os.path.isdir(p):
            return len(os.listdir(p)) == 0
        return False

    def is_file_non_empty(self, name: path) -> bool:
        """
        Checks if a file exists. If exists, check if it is not empty as well.
        :param name: file to check
        :return: true if the file exists **and** has at least one byte; false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"Checking if the file {p} exists and is empty")
        if not os.path.exists(p):
            return False
        with open(p, "r") as f:
            return f.read(1) != ""

    def write_file(self, name: path, content: Any, encoding: str = "utf-8", overwrite: bool = False, add_newline: bool = True):
        """
        Write into a file with the specified content. if overwrite is unset, we will do nothing if the file already exists
        :param name: name of the file to create
        :param content: content of the file to create.
        :param encoding: encoding fo the file to create. utf-8 by default
        :param overwrite: if true, we will overwrite the file
        :param add_newline: if true, we will add a new line at the end of the content
        """

        p = self.get_path(name)
        self._log_command(f"Writing file {p} with content {self._truncate_string(content, 20)}")
        if not overwrite and os.path.exists(p):
            return
        else:
            with open(p, "w", encoding=encoding) as f:
                f.write(str(content))
                if add_newline:
                    f.write("\n")

    def write_lines(self, name: path, content: Iterable[Any], encoding: str = "utf-8", overwrite: bool = False):
        """
        Write severla lines into a file. if overwrite is unset, we will do nothing if the file already exists
        :param name: name of the file to create
        :param content: lines of the file to create. We will append a new ine at the end of each line
        :param encoding: encoding fo the file to create. utf-8 by default
        :param overwrite: if true, we will overwrite the file
        """

        p = self.get_path(name)
        self._log_command(f"Writing file {p} with content {len(list(content))} lines")
        if not overwrite and os.path.exists(p):
            return
        else:
            with open(p, "w", encoding=encoding) as f:
                for x in content:
                    f.write(str(x) + "\n")

    def read_lines(self, name: path, encoding: str = "utf-8") -> Iterable[str]:
        """
        Read the content of a file and yields as many item as there are lines in the file.
        Strip from the line ending new lines. Does not consider empty lines
        :param name: name of the file
        :param encoding: encoding of the file. If unspecified, it is utf-8
        :return: iterable containing the lines of the file
        """
        p = self.get_path(name)
        self._log_command(f"Reading lines from file {p}")
        with open(p, "r", encoding=encoding) as f:
            for line in f.readlines():
                if line is None:
                    continue
                if line.strip() == "":
                    continue
                yield line.rstrip("\n\r")

    def read_file_content(self, name: path, encoding: str = "utf-8") -> str:
        """
        Read the whole content of the file in a single string
        :param name: name of the file to load
        :param encoding: the encoding of the file. If unspecified, it is utf-8
        :return: string repersenting the content of the file
        """
        p = self.get_path(name)
        self._log_command(f"Reading file {p} content")
        with open(p, "r", encoding=encoding) as f:
            return f.read()

    def append_string_at_end_of_file(self, name: path, content: Any, encoding: str = "utf-8"):
        """
        Append a string at the end of the file. carriage return is automatically added
        :param name: filename
        :param content: string to append
        :param encoding: encoding of the file. If missing, "utf-8" is used
        """
        p = self.get_path(name)
        self._log_command(f"Appending {content} into file file {p}")
        with open(p, "a", encoding=encoding) as f:
            f.write(str(content) + "\n")

    def copy_file(self, src: path, dst: path):
        """
        Copy a single file from a position to another one
        :param src: file to copy
        :param dst: destination where the file will be copied to
        """
        asrc = self.get_path(src)
        adst = self.get_path(dst)
        self._log_command(f"""copy file from \"{asrc}\" to \"{adst}\"""")
        shutil.copyfile(asrc, adst)

    def copy_tree(self, src: path, dst: path):
        """
        Copy a whole directory tree or a single file
        :param src: the folder or the file to copy.
        :param dst: the destination where the copied folder will be positioned
        """
        asrc = self.get_path(src)
        adst = self.get_path(dst)
        self._log_command(f"""Recursively copy files from \"{asrc}\" to \"{adst}\"""")
        if os.path.isdir(asrc):
            shutil.copytree(
                asrc,
                adst,
            )
        elif os.path.isfile(asrc):
            shutil.copyfile(
                asrc,
                adst
            )
        else:
            raise ValueError(f"Cannot determine if {asrc} is a file or a directory!")

    def copy_folder_content(self, folder: path, destination: path):
        """
        Copy all the content of "folder" into the folder "destination"
        :param folder: folder to copy files from
        :param destination: folder where the contents will be copied into
        """
        afolder = self.get_path(folder)
        adestination = self.get_path(destination)
        self._log_command(f"""Copies all files inside \"{afolder}\" into the folder \"{adestination}\"""")

        try:
            self._disable_log_command = False
            for x in self.ls(afolder, generate_absolute_path=False):
                self.copy_tree(
                    src=os.path.join(afolder, x),
                    dst=os.path.abspath(os.path.join(adestination, x))
                )
        finally:
            self._disable_log_command = True

    def download_url(self, url: str, destination: path = None, ignore_if_file_exists: bool = True) -> path:
        """
        Download an artifact from internet
        :param url: the url where the file is lcoated
        :param destination: the folder where the file will be created
        :param ignore_if_file_exists: if true, we will not perform the download at all
        :return: path containing the downloaded item
        """
        dst = self.get_path(destination)
        self._log_command(f"""Downloading {url} from internet into {dst}""")
        if ignore_if_file_exists and os.path.exists(dst):
            return dst

        result, http_message = urllib.request.urlretrieve(url, dst)
        return result

    def allow_file_to_be_executed_by_anyone(self, file: path):
        """
        Allow the file to be executed by anyone. On a linux system it should be equal to "chmod o+x"
        :param file: the file whose permission needs to be changed
        """
        p = self.get_path(file)
        self._log_command(f"""Allowing any user to unr {p}""")
        os.chmod(p, mode=stat.S_IEXEC)

    def copy_files_that_basename(self, src: path, dst: path, regex: str):
        """
        Copy the files located (directly or indirctly) in src into dst.
        We will copy only the files whose basename (e.g. foo.txt is the basename of /opt/foo/bar/foo.txt).
        We will copy the directories where a file is located as well
        matches the given regex
        :param src: folder where we will find files to copy
        :param dst: destination of the files
        :param regex: regex that determines wether or not a file is copies
        :return:
        """
        s = self.get_path(src)
        d = self.get_path(dst)
        self._log_command(f"Copy files from {s} into {d} which basename follows {regex}")
        try:
            self._disable_log_command = False
            for x in self.ls_recursive(src):
                if re.search(pattern=regex, string=os.path.basename(x)):
                    rel = os.path.relpath(x, s)
                    copied_d = os.path.abspath(os.path.join(d, rel))
                    os.makedirs(os.path.dirname(copied_d), exist_ok=True)
                    shutil.copyfile(src=x, dst=copied_d)
        finally:
            self._disable_log_command = True

    def move_tree(self, src: path, dst: path):
        self._log_command(f"""Recursively move files from \"{src}\" to \"{dst}\"""")
        self.copy_tree(src, dst)
        self.remove_tree(src)

    def remove_tree(self, src: path, ignore_if_not_exists: bool = True):
        self._log_command(f"""Recursively remove files from \"{src}\"""")
        try:
            shutil.rmtree(src)
        except Exception as e:
            if not ignore_if_not_exists:
                raise e

    def remove_files_that_basename(self, src: path, regex: str):
        """
        Remove the files located (directly or indirectly) in src.
        We will copy only the files whose basename (e.g. foo.txt is the basename of /opt/foo/bar/foo.txt).
        We will copy the directories where a file is located as well
        matches the given regex
        :param src: folder where we will find files to copy
        :param regex: regex that determines wether or not a file is copies
        :return:
        """
        s = self.get_path(src)
        self._log_command(f"Remove the files from {s} which basename follows {regex}")
        try:
            self._disable_log_command = False
            for x in self.ls_recursive(src):
                logging.debug(f"Checking if {x} should be removed")
                if re.search(pattern=regex, string=os.path.basename(x)):
                    try:
                        logging.debug(f"Removing {x}")
                        os.unlink(x)
                    except Exception as e:
                        pass
        finally:
            self._disable_log_command = True

    def move_file(self, src: path, dst: path):
        """
        Move a single file from a location to another one
        :param src: the file to move
        :param dst: the path where the file will be moved to
        """
        asrc = self.get_path(src)
        adst = self.get_path(dst)
        self._log_command(f"""move file from \"{asrc}\" to \"{adst}\"""")
        shutil.move(asrc, adst)

    def remove_file(self, name: path, ignore_if_not_exists: bool = True) -> bool:
        """
        Remove a file. If the cannot be removed (for some reason), ignore_if_not_exists determines if somethign goes wrong
        :param name: file to delete
        :param ignore_if_not_exists: if true, we won't raise exception if the file does not exists or cannot be removed
        :return: true if we have removed the file, false otherwise
        """
        p = self.get_path(name)
        self._log_command(f"remove file {p}")
        try:
            os.unlink(p)
            return True
        except Exception as e:
            if not ignore_if_not_exists:
                raise e
            return False

    def cwd(self) -> path:
        """

        :return: the CWD the commands operates in
        """
        return os.path.abspath(self._cwd)

    def get_path(self, p: path) -> path:
        if os.path.isabs(p):
            return os.path.abspath(p)
        else:
            return os.path.abspath(os.path.join(self._cwd, p))

    def ls(self, folder: path = None, generate_absolute_path: bool = False) -> Iterable[path]:
        """
        Show the list of all the files in the given directory
        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders. Otherwise we will return only the
        :return:
        """
        if folder is None:
            folder = self._cwd
        self._log_command(f"""listing files of folder \"{self.get_path(folder)}\"""")
        for x in os.listdir(folder):
            if generate_absolute_path:
                yield os.path.abspath(os.path.join(folder, x))
            else:
                yield x

    def ls_only_files(self, folder: path = None, generate_absolute_path: bool = False) -> Iterable[path]:
        """
        Show the list of all the files (but not directories) in the given directory
        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders. Otherwise we will return only the
        :return:
        """
        if folder is None:
            folder = self._cwd
        p = self.get_path(folder)
        self._log_command(f"""listing files in fodler \"{p}\"""")
        for f in os.listdir(p):
            if os.path.isfile(f):
                if generate_absolute_path:
                    yield os.path.abspath(os.path.join(p, f))
                else:
                    yield f

    def ls_only_directories(self, folder: path = None, generate_absolute_path: bool = False) -> Iterable[path]:
        """
        Show the list of all the directories in the given directory
        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders. Otherwise we will return only the
        names
        :return:
        """
        if folder is None:
            folder = self._cwd
        p = self.get_path(folder)
        self._log_command(f"""listing folders in folder \"{p}\"""")
        for f in os.listdir(p):
            if os.path.isdir(os.path.abspath(os.path.join(p, f))):
                if generate_absolute_path:
                    yield os.path.abspath(os.path.join(p, f))
                else:
                    yield f

    def ls_recursive(self, folder: path = None) -> Iterable[path]:
        """
        Show the list of all the files in the given folder
        :param folder: folder to scan (default to cwd)
        :return: list of absolute filename representing the stored files
        """
        self._log_command(f"""listing direct and indirect files of folder \"{self.get_path(folder)}\"""")
        for dirpath, dirnames, filenames in os.walk(folder):
            # dirpath: the cwd wheren dirnames and filesnames are
            # dirnames: list of all the directories in dirpath
            # filenames: list of all the files in dirpath
            for filename in filenames:
                yield self.get_path(os.path.join(dirpath, filename))

    def match(self, string: str, regex: str) -> bool:
        """
        Check if a given string matches perfectly the given regex
        :param string: the sting to check
        :param regex: the regex to check. The syntax is available at https://docs.python.org/3/library/re.html
        :return: true if such a substring can be found, false otherwise
        """
        m = re.match(regex, string)
        return m is not None

    def get_relative_path_wrt(self, p: path, reference: path):
        """
        If we were in folder reference, what actiosn should we perform in order to reach the file p?
        :param p: the file to reach
        :param reference: the folder we are in right now
        :return: relative path
        """
        return os.path.relpath(path=p, start=reference)

    def search(self, string: str, regex: str):
        """
        Check if a given string has a substring that matches the given regex
        :param string: the sting to check
        :param regex: the regex to check. The syntax is available at https://docs.python.org/3/library/re.html
        :return: true if such a substring can be found, false otherwise
        """
        m = re.match(regex, string)
        return m is not None

    def ls_directories_recursive(self, folder: path) -> Iterable[path]:
        """
        Show the list of all the directories in the given folder
        :param folder: folder to scan (default to cwd)
        :return: list of absolute filename representing the stored directories
        """
        self._log_command(f"""listing direct and indirect folders of folder \"{self.get_path(folder)}\"""")
        for dirpath, dirnames, filenames in os.walk(folder):
            # dirpath: the cwd wheren dirnames and filesnames are
            # dirnames: list of all the directories in dirpath
            # filenames: list of all the files in dirpath
            for dirname in dirnames:
                yield self.get_path(os.path.join(dirpath, dirname))

    def cd(self, folder: path, create_if_not_exists: bool = True):
        """
        Gain access to a directory. If the directory does nto exists, it is created
        If the path is relative, it is relative to the CWD
        :param folder: folder where we need to go into
        :param create_if_not_exists: if true, we will create the directory if we try to cd into a non existent directory
        """
        self._log_command(f"""cd into folder \"{self.get_path(folder)}\"""")
        self._cwd = self.get_path(folder)
        if not os.path.exists(self._cwd) and create_if_not_exists:
            os.makedirs(self._cwd, exist_ok=True)

    def current_user(self) -> str:
        """
        get the user currently logged
        :return:
        """
        return self._platform.get_current_username()

    def abs_wrt_cwd(self, *paths) -> path:
        """
        generate a path relative to cwd and generate the absolute path of it
        :param paths:
        :return:
        """
        return os.path.abspath(os.path.join(self._cwd, *paths))

    def make_directories(self, folder: path):
        """
        Create all the needed directories for the given path
        :param folder:
        :return:
        """
        self._log_command(f"""Recursively create directories \"{self.get_path(folder)}\"""")
        os.makedirs(self.get_path(folder), exist_ok=True)

    def cd_into_directories(self, folder: path, prefix: str, folder_format: str, error_if_mismatch: bool = True):
        """
        Inside the given folder, there can be several folders, each of them with the same format. We cd into the "latest" one.
        How can we determine which is the "latest" one? Via folder_format. it is a string that is either:
         - number: an integer number
         - semver2: a semantic versionign string;
        We fetch the "latest" by looking at the one with the greater value. If the folder contains a folder which it is not compliant
        with folder_format, it is either ignored or rase error
        :param folder: folder where several folders are located
        :param prefix: a string that prefix folder_format
        :param folder_format: either "number" or "semver2"
        :param error_if_mismatch: if a folder is not compliant with folder_format, if true we will generate an exception
        :return:
        """

        try:
            p = self.get_path(folder)
            self._log_command(f"Cd'ing into the \"latest\" directory in folder \"{p}\" according to criterion \"{folder_format}\"")
            self._disable_log_command = True
            self.cd(folder)

            folders = dict()
            for subfolder in self.ls_only_directories(p):
                if not subfolder.startswith(prefix):
                    if error_if_mismatch:
                        raise ValueError(f"subfolder \"{subfolder}\" in \"{p}\" does not start with \"{prefix}\"")
                    else:
                        continue

                subfolder_id = subfolder[len(prefix):]
                try:
                    if folder_format == "semver2":
                        folders[semver.VersionInfo.parse(subfolder_id)] = subfolder
                    elif folder_format == "number":
                        folders[int(subfolder_id)] = subfolder
                    else:
                        raise ValueError(f"invalid folder_format \"{folder_format}\"")
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

    def exec(self, command: Union[str, List[str]], cwd: path = None):
        """
        Execute a command as current user. if you use this command it is assumed you absolutely don't care about
        the outpput of the command
        :param command: command to exexcute. If possible, prefer using a list rather than a string. string are stuill supported though
        :param cwd: directory where this command should be executed. If missing, the cwd is the CWD of the whole script
        """
        self._log_command(f"""Execute command without capturing output \"{command}\"""")
        if cwd is None:
            cwd = self._cwd
        else:
            cwd = self.get_path(cwd)
        self._platform.execute(
            command=command,
            cwd=cwd,
            use_shell=True,
            capture_stdout=False
        )

    def exec_admin(self, command: Union[str, List[str]], cwd: path = None):
        """
        Execute a command as admin. if you use this command it is assumed you absolutely don't care about
        the outpput of the command
        :param command: command to exexcute. If possible, prefer using a list rather than a string. string are stuill supported though
        :param cwd: directory where this command should be executed. If missing, the cwd is the CWD of the whole script
        """
        self._log_command(f"""Execute admin command without capturing output \"{command}\"""")
        if cwd is None:
            cwd = self._cwd
        else:
            cwd = self.get_path(cwd)
        self._platform.execute_admin(
            command=command,
            cwd=cwd,
            use_shell=True,
            capture_stdout=False
        )

    def exec_stdout(self, command: Union[str, List[str]], cwd: path = None) -> str:
        """
        Execute a command as current user. if you use this command it is assumed you care about the output of the command
        :param command: command to exexcute. If possible, prefer using a list rather than a string. string are stuill supported though
        :param cwd: directory where this command should be executed. If missing, the cwd is the CWD of the whole script
        """
        self._log_command(f"""Execute command capturing output \"{command}\"""")
        if cwd is None:
            cwd = self._cwd
        else:
            cwd = self.get_path(cwd)
        code, stdout, stderr = self._platform.execute(
            command=command,
            cwd=cwd,
            use_shell=True,
            capture_stdout=True
        )
        return stdout

    def exec_admin_stdout(self, command: Union[str, List[str]], cwd: path = None) -> str:
        """
        Execute a command as admin. if you use this command it is assumed you care about the output of the command
        :param command: command to exexcute. If possible, prefer using a list rather than a string. string are stuill supported though
        :param cwd: directory where this command should be executed. If missing, the cwd is the CWD of the whole script
        """
        self._log_command(f"""Execute admin command capturing output \"{command}\"""")
        if cwd is None:
            cwd = self._cwd
        else:
            cwd = self.get_path(cwd)
        code, stdout, stderr = self._platform.execute_admin(
            command=command,
            cwd=self._cwd,
            use_shell=True,
            capture_stdout=True
        )
        return stdout

    def include_string(self, string: str):
        self._model.execute_string(string)

    def include_file(self, file: path):
        """
        Replace the include directive with the content fo the included file. Fails if there is no such path
        :param file:
        :return:
        """

        p = self.get_path(file)
        self._log_command(f"include file content \"{p}\"")
        self._model.execute_file(p)



