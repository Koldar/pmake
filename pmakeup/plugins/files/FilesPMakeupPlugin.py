import logging
import os
import re
import shutil
import stat
from typing import Iterable, Union, Optional, Any, List, Callable

import pmakeup as pm


class FilesPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("files")
    def find_executable_in_program_directories(self, program_name: str, fail_if_program_is_not_found: bool = False) -> \
    Optional[pm.path]:
        """
        Find a program ouside the path as well. Paths is still considered

        :param program_name: name of the program to look for
        :param fail_if_program_is_not_found: if true, we will raise an exception if the program is not found
        :return: first absolute path of the program found. None if we did not find the program
        """
        self._log_command(
            f"""Find the executable \"{program_name}\" in the place where the operating system usually puts installed programs...""")
        result = self.platform.find_executable_in_program_directories(
            program_name=program_name,
        )
        if result is None and fail_if_program_is_not_found:
            raise pm.PMakeupException(f"We could not find the program \"{program_name}\" on the system!")
        return result

    @pm.register_command.add("files")
    def create_empty_file(self, name: pm.path, encoding: str = "utf-8"):
        """
        Create an empty file. if the file is relative, it is relative to the CWD

        :param name: file name to create
        :param encoding: encoding of the file. If unspecified, it is utf-8
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Creating empty file {p}")
        with open(p, "w", encoding=encoding) as f:
            pass

    @pm.register_command.add("files")
    def allow_file_to_be_executed_by_anyone(self, file: pm.path):
        """
        Allow the file to be executed by anyone. On a linux system it should be equal to "chmod o+x"

        :param file: the file whose permission needs to be changed
        """
        p = self.paths.abs_path(file)
        self._log_command(f"""Allowing any user to unr {p}""")
        os.chmod(p, mode=stat.S_IEXEC)

    @pm.register_command.add("files")
    def make_directories(self, *folder: pm.path) -> None:
        """
        Create all the needed directories for the given path.
        Note that if you inject the path `temp/foo/hello.txt` (you can see hello.txt shoudl be a file)
        the function will generate hello.txt as a **directory**!

        :param folder: folders to create
        """
        f = self._abs_wrt_cwd(*folder)
        self._log_command(f"""Recursively create directories \"{f}\"""")

        os.makedirs(self.paths.abs_path(f), exist_ok=True)

    @pm.register_command.add("files")
    def is_file(self, *p: pm.path) -> bool:
        """
        Check if the given path represents a file or a directory

        :param p: paths to check
        return: true if the concatenated version of p is a file. False otherwise
        """

        to_check = self._abs_wrt_cwd(*p)
        return os.path.isfile(to_check)

    @pm.register_command.add("files")
    def is_directory(self, *p: pm.path) -> bool:
        """
        Check if the given path is a directory

        :param p: paths to check
        return: true if the concatenated version of p is a directory. False otherwise
        """

        to_check = self._abs_wrt_cwd(*p)
        return os.path.isdir(to_check)

    @pm.register_command.add("files")
    def get_file_size(self, *f: pm.path) -> int:
        """
        Get the filesize of a given file. If the file is a directory, return the cumulative size of all the files in it

        :param f: the path of the file to consider
        :return: number of bytes
        """

        to_check = self._abs_wrt_cwd(*f)
        if self.is_file(to_check):
            return os.path.getsize(to_check)
        elif self.is_directory(to_check):
            # see https://stackoverflow.com/a/1392549/1887602
            nbytes = sum(d.stat().st_size for d in os.scandir('../..') if d.is_file())
            return nbytes
        else:
            raise ValueError(f"file {to_check} is neither a file nor a directory! What is this?")

    @pm.register_command.add("files")
    def create_empty_directory(self, name: pm.path) -> pm.path:
        """
        Create an empty directory in the CWD (if the path is relative)

        :param name:the name of the driectory to create
        :return: the full path of the directory just created
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Creating folder {p}")
        os.makedirs(name=p, exist_ok=True)
        return p

    @pm.register_command.add("files")
    def is_file_exists(self, name: pm.path) -> bool:
        """
        Check if a file exists

        :param name: file whose existence we need to assert
        :return: true if the file exists, false otherwise
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Checking if the file {p} exists")
        return os.path.exists(p)

    @pm.register_command.add("files")
    def is_file_empty(self, name: pm.path) -> bool:
        """
        Checks if a file exists. If exists, check if it empty as well.

        :param name: file to check
        :return: true if the file exists **and** has no bytes; false otherwise
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Checking if the file {p} exists and is empty")
        if not os.path.exists(p):
            return False
        with open(p, "r") as f:
            return f.read(1) == ""

    @pm.register_command.add("files")
    def is_directory_exists(self, name: pm.path) -> bool:
        """
        Check if a directory exists.

        :param name: folder to check
        :return: true if the folder exists, false otherwise
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Checking if the folder {p} exists")
        if os.path.exists(p) and os.path.isdir(p):
            return True
        return False

    @pm.register_command.add("files")
    def is_directory_empty(self, name: pm.path) -> bool:
        """
        Check if a directory exists and is empty

        :param name: folder to check
        :return: true if the folder exists and is empty, false otherwise
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Checking if the folder {p} exists and is empty")
        if os.path.exists(p) and os.path.isdir(p):
            return len(os.listdir(p)) == 0
        return False

    @pm.register_command.add("files")
    def is_file_non_empty(self, *name: pm.path) -> bool:
        """
        Checks if a file exists. If exists, check if it is not empty as well.

        :param name: file to check
        :return: true if the file exists **and** has at least one byte; false otherwise
        """
        p = self.paths.abs_path(*name)
        self._log_command(f"Checking if the file {p} exists and is empty")
        if not os.path.exists(p):
            return False
        return self.get_file_size(p) > 0

    @pm.register_command.add("files")
    def write_file(self, name: pm.path, content: Any, encoding: str = "utf-8", overwrite: bool = False,
                   add_newline: bool = True):
        """
        Write into a file with the specified content. if overwrite is unset, we will do nothing if the file already exists

        :param name: name of the file to create
        :param content: content of the file to create.
        :param encoding: encoding fo the file to create. utf-8 by default
        :param overwrite: if true, we will overwrite the file
        :param add_newline: if true, we will add a new line at the end of the content
        """

        p = self.paths.abs_path(name)
        self._log_command(f"Writing file \"{p}\" with content \"{self._truncate_string(content, 20)}\"")
        if not overwrite and os.path.exists(p):
            return
        else:
            with open(p, "w", encoding=encoding) as f:
                f.write(str(content))
                if add_newline:
                    f.write("\n")

    @pm.register_command.add("files")
    def write_lines(self, name: pm.path, content: Iterable[Any], encoding: str = "utf-8", overwrite: bool = False):
        """
        Write severla lines into a file. if overwrite is unset, we will do nothing if the file already exists

        :param name: name of the file to create
        :param content: lines of the file to create. We will append a new ine at the end of each line
        :param encoding: encoding fo the file to create. utf-8 by default
        :param overwrite: if true, we will overwrite the file
        """

        p = self.paths.abs_path(name)
        self._log_command(f"Writing file {p} with content {len(list(content))} lines")
        if not overwrite and os.path.exists(p):
            return
        else:
            with open(p, "w", encoding=encoding) as f:
                for x in content:
                    f.write(str(x) + "\n")

    @pm.register_command.add("files")
    def read_lines(self, name: pm.path, encoding: str = "utf-8") -> Iterable[str]:
        """
        Read the content of a file and yields as many item as there are lines in the file.
        Strip from the line ending new lines. Does not consider empty lines

        :param name: name of the file
        :param encoding: encoding of the file. If unspecified, it is utf-8
        :return: iterable containing the lines of the file
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Reading lines from file {p}")
        with open(p, "r", encoding=encoding) as f:
            for line in f.readlines():
                if line is None:
                    continue
                if line.strip() == "":
                    continue
                yield line.rstrip("\n\r")

    @pm.register_command.add("files")
    def read_file_content(self, name: pm.path, encoding: str = "utf-8", trim_newlines: bool = True) -> str:
        """
        Read the whole content of the file in a single string

        :param name: name of the file to load
        :param encoding: the encoding of the file. If unspecified, it is utf-8
        :param trim_newlines: if true, we will trim the newlines, spaces and tabs at the beginning and at the end of the file
        :return: string repersenting the content of the file
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Reading file {p} content")
        with open(p, "r", encoding=encoding) as f:
            result = f.read()
        if trim_newlines:
            result = result.strip("\t\n\r ")
        return result

    @pm.register_command.add("files")
    def remove_last_n_line_from_file(self, name: pm.path, n: int = 1, consider_empty_line: bool = False,
                                     encoding: str = "utf-8") -> List[str]:
        """
        Read the content of a file and remove the last n lines from the file involved. Then, rewrites the whole file

        :param name: file involved. If relative, it is relative to ::cwd()
        :param n: the number of lines to remove at the end.
        :param consider_empty_line: if True, we consider empty lines as well.
        :param encoding: the encoding used to rewrite file
        :return: the lines just removed
        """

        p = self.paths.abs_path(name)

        self._log_command(f"Remove {n} lines at the end of file {p} (consider empty line = {consider_empty_line})")
        with open(name, mode="r", encoding=encoding) as f:
            lines = list(f.readlines())

        result = []
        final_i = 0
        for i, line in enumerate(reversed(lines)):
            if final_i == n:
                break

            if consider_empty_line and line.strip() == "":
                result.append(line)
                continue
            result.append(line)
            final_i += 1

        # write the file
        with open(name, mode="w", encoding=encoding) as f:
            f.writelines(lines[:-final_i])

        return result

    @pm.register_command.add("files")
    def append_string_at_end_of_file(self, name: pm.path, content: Any, encoding: str = "utf-8") -> None:
        """
        Append a string at the end of the file. carriage return is automatically added

        :param name: filename
        :param content: string to append
        :param encoding: encoding of the file. If missing, "utf-8" is used
        """
        self.append_strings_at_end_of_file(
            name=name,
            content=[content],
            encoding=encoding
        )

    @pm.register_command.add("files")
    def append_strings_at_end_of_file(self, name: pm.path, content: Iterable[Any], encoding: str = "utf-8") -> None:
        """
        Append a string at the end of the file. carriage return is automatically added

        :param name: filename
        :param content: string to append
        :param encoding: encoding of the file. If missing, "utf-8" is used
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Appending {content} into file file {p}")
        with open(p, "a", encoding=encoding) as f:
            for x in content:
                f.write(str(x) + "\n")

    @pm.register_command.add("files")
    def copy_file(self, src: pm.path, dst: pm.path, create_dirs: bool = True):
        """
        Copy a single file from a position to another one.
        If the destination folder hierarchy does not exist, we will create it

        :param src: file to copy
        :param dst: destination where the file will be copied to. If a file, we will copy the src file into another
            file with different name. If a directory, we will copy the specified file into the dirctory dst (without
            altering the filename)
        :param create_dirs: if true, we will create the directories of dst if non existent
        """
        asrc = self.paths.abs_path(src)
        adst = self.paths.abs_path(dst)

        if self.is_directory(adst):
            adst = os.path.join(adst, self.paths.get_basename(asrc))

        if not self.is_directory_exists(self.paths.get_parent_directory(adst)) and create_dirs:
            self.make_directories(self.paths.get_parent_directory(adst))

        self._log_command(f"""copy file from \"{asrc}\" to \"{adst}\"""")
        shutil.copyfile(asrc, adst)

    @pm.register_command.add("files")
    def copy_tree(self, src: pm.path, dst: pm.path):
        """
        Copy a whole directory tree or a single file.
        If you specifies a file rather than a directory, the function behaves like :see copy_file

        :param src: the folder or the file to copy.
        :param dst: the destination where the copied folder will be positioned
        """

        asrc = self.paths.abs_path(src)
        adst = self.paths.abs_path(dst)
        self._log_command(f"""Recursively copy files from \"{asrc}\" to \"{adst}\"""")
        if os.path.isdir(asrc):
            shutil.copytree(
                asrc,
                adst,
                dirs_exist_ok=True,
            )
        elif os.path.isfile(asrc):
            self.copy_file(asrc, adst)
        else:
            raise pm.InvalidScenarioPMakeupException(f"Cannot determine if {asrc} is a file or a directory!")

    @pm.register_command.add("files")
    def copy_folder_content(self, folder: pm.path, destination: pm.path):
        """
        Copy all the content of "folder" into the folder "destination"

        :param folder: folder to copy files from
        :param destination: folder where the contents will be copied into
        """
        afolder = self.paths.abs_path(folder)
        adestination = self.paths.abs_path(destination)
        self._log_command(f"""Copies all files inside \"{afolder}\" into the folder \"{adestination}\"""")

        try:
            self.get_shared_variables()._disable_log_command = False
            for x in self.ls(afolder, generate_absolute_path=False):
                self.copy_tree(
                    src=os.path.join(afolder, x),
                    dst=os.path.abspath(os.path.join(adestination, x))
                )
        finally:
            self.get_shared_variables()._disable_log_command = True

    @pm.register_command.add("files")
    def find_regex_match_in_file(self, pattern: str, *p: pm.path, encoding: str = "utf8",
                                 flags: Union[int, re.RegexFlag] = 0) -> Optional[re.Match]:
        """
        FInd the first regex pattern in the file

        If you used named capturing in the pattern, you can gain access via result.group("name")

        :param pattern: regex pattern to consider
        :param p: file to consider
        :param encoding: encoding of the file to search. Defaults to utf8
        :param flags: flags of the regex to build. Passed as-is
        :return: a regex match representing the first occurence. If None we could not find anything
        """

        fn = self._abs_wrt_cwd(*p)
        self._log_command(f"""Looking for pattern {pattern} in file {fn}.""")
        with open(fn, mode="r", encoding=encoding) as f:
            content = f.read()

        return re.search(pattern, content, flags=flags)

    @pm.register_command.add("files")
    def replace_string_in_file(self, name: pm.path, substring: str, replacement: str, count: int = -1,
                               encoding: str = "utf-8"):
        """
        Replace some (or all) the occurences of a given substring in a file

        :param name: path of the file to handle
        :param substring: substring to replace
        :param replacement: string that will replace *substring*
        :param count: the number of occurences to replace. -1 if you want to replace all occurences
        :param encoding: encoding used for reading the file
        """
        p = self.paths.abs_path(name)
        self._log_command(
            f"Replace substring \"{substring}\" in \"{replacement}\" in file {p} (up to {count} occurences)")
        with open(p, mode="r", encoding=encoding) as f:
            content = f.read()

        with open(p, mode="w", encoding=encoding) as f:
            try:
                # the sub operation may throw exception. In this case the file is reset. This is obviously very wrong,
                # hence we added the try except in order to at least leave the file instact
                content = content.replace(substring, replacement, count)
            finally:
                f.write(content)

    @pm.register_command.add("files")
    def replace_regex_in_file(self, name: pm.path, regex: str, replacement: str, count: int = -1,
                              encoding: str = "utf-8"):
        """
        Replace some (or all) the occurences of a given regex in a file.

        If you want to use named capturing group, you can do so! For instance,

        replace_regex_in_file(file_path, '(?P<word>\\w+)', '(?P=word)aa')
        'spring' will be replaced with 'springaa'

        It may not work, so you can use the following syntax to achieve the same:
        replace_regex_in_file(file_path, '(?P<word>\\w+)', r'\\g<word>aa')
        'spring' will be replaced with 'springaa'


        :param name: path of the file to handle
        :param regex: regex to replace
        :param replacement: string that will replace *substring*
        :param count: the number of occurences to replace. -1 if you want to replace all occurences
        :param encoding: encoding used for reading the file
        :see: https://docs.python.org/3/howto/regex.html
        """
        pattern = re.compile(regex)
        if count < 0:
            count = 0

        p = self.paths.abs_path(name)
        with open(p, mode="r", encoding=encoding) as f:
            content = f.read()

        with open(p, mode="w", encoding=encoding) as f:
            try:
                # the sub operation may throw exception. In this case the file is reset. This is obviously very wrong,
                # hence we added the try except in order to at least leave the file instact
                self._log_command(
                    f"Replace pattern \"{pattern}\" into \"{replacement}\" in file {p} (up to {count} occurences)")
                content = re.sub(
                    pattern=pattern,
                    repl=replacement,
                    string=content,
                    count=count,
                )
            finally:
                f.write(content)

    @pm.register_command.add("files")
    def find_file(self, root_folder: pm.path, filename: str) -> Iterable[str]:
        """
        Find all the files with the given filename (extension included)

        :param root_folder: fodler where we need to look int
        :param filename: filename we need to fetch
        :return: list of files with thwe given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return f == filename

        self._log_command(f"""Finding file with filename {filename} in directory {root_folder}""")
        yield from self.find_file_st(root_folder, match)

    @pm.register_command.add("files")
    def find_directory(self, root_folder: pm.path, folder: str) -> Iterable[str]:
        """
        Find all the directories with the given name

        :param root_folder: fodler where we need to look int
        :param folder: name of the folder we need to fetch
        :return: list of files with thwe given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return f == folder

        self._log_command(f"""Finding directory named {folder} in directory {root_folder}""")
        yield from self.find_folder_st(root_folder, match)

    @pm.register_command.add("files")
    def find_file_with_filename_compliant_with_regex(self, root_folder: pm.path, filename_regex: str) -> Iterable[str]:
        """
        Find all the files containign (search) the given regex

        :param root_folder: folder where we need to look int
        :param filename_regex: the regex any filename should be compliant
        :return: list of files with thwe given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return re.search(pattern=filename_regex, string=f) is not None

        self._log_command(f"""Finding file whose filename is compliant with regex {filename_regex} in directory {root_folder}""")
        yield from self.find_file_st(root_folder, match)

    @pm.register_command.add("files")
    def find_directory_with_filename_compliant_with_regex(self, root_folder: pm.path, folder_regex: str) -> Iterable[str]:
        """
        Find all the directories with the given name

        :param root_folder: fodler where we need to look int
        :param folder_regex: regex the folder name should be compliant with
        :return: list of files with thwe given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return re.search(pattern=folder_regex, string=f) is not None

        self._log_command(
            f"""Finding folder whose name is compliant with regex {folder_regex} in directory {root_folder}""")
        yield from self.find_folder_st(root_folder, match)

    @pm.register_command.add("files")
    def find_file_with_fullpath_compliant_with_regex(self, root_folder: pm.path, filename_regex: str) -> Iterable[str]:
        """
        Find all the files containing (search) the given regex

        :param root_folder: folder where we need to look int
        :param filename_regex: the regex any filename should be compliant
        :return: list of files with the given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return re.search(pattern=filename_regex, string=whole_path) is not None

        self._log_command(f"""Finding file whose full absolute path is compliant with regex {filename_regex} in directory {root_folder}""")
        yield from self.find_file_st(root_folder, match)

    @pm.register_command.add("files")
    def find_directory_with_fullpath_compliant_with_regex(self, root_folder: pm.path, folder_regex: str) -> Iterable[str]:
        """
        Find all the directories with the given name

        :param root_folder: folder where we need to look int
        :param folder_regex: regex the folder name should be compliant with
        :return: list of files with thwe given filename
        """

        def match(root: pm.path, f: str, whole_path: pm.path) -> bool:
            return re.search(pattern=folder_regex, string=whole_path) is not None

        self._log_command(f"""Finding directory whose absolute path is compliant with regex {folder_regex} in directory {root_folder}""")
        yield from self.find_folder_st(root_folder, match)

    @pm.register_command.add("files")
    def find_file_st(self, root_folder: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> Iterable[str]:
        """
        Find all the files matchign the given function

        :param root_folder: folder where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: list of files compliant with the given function
        """

        for root, dirs, files in os.walk(root_folder):
            for f in files:
                whole_path = os.path.join(root, f)
                if match(root, f, whole_path):
                    yield whole_path

    @pm.register_command.add("files")
    def find_first_file_st(self, root_folder: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> Optional[str]:
        """
        Find the first file matching the given function

        :param root_folder: folder where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: file compliant with the given function or None
        """
        for f in self.find_file_st(root_folder, match):
            return f

        return None

    @pm.register_command.add("files")
    def find_first_file_st_or_fail(self, root_folder: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> str:
        """
        Find the first file matching the given function. If no such file exists, generates an exception

        :param root_folder: folder where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: file compliant with the given function or None
        """
        result = self.find_first_file_st(root_folder, match)
        if result is None:
            raise ValueError(f"Could not find file satysfing the given criterion from the root {root_folder}!")
        return result

    @pm.register_command.add("files")
    def find_file_in_roots_st(self, root_folders: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> Iterable[str]:
        """
        Find all the files matchign the given function

        :param root_folders: folders where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: list of files compliant with the given function
        """

        for root_folder in root_folders:
            yield from self.find_file_st(root_folder, match)

    @pm.register_command.add("files")
    def find_first_file_in_roots_st(self, root_folders: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> Optional[str]:
        """
        Find the first file matching the given function

        :param root_folders: folders where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: file compliant with the given function or None
        """
        for f in self.find_file_in_roots_st(root_folders, match):
            return f

        return None

    @pm.register_command.add("files")
    def find_first_file_in_roots_st_or_fail(self, root_folders: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> str:
        """
        Find the first file matching the given function. If no such file exists, generates an exception

        :param root_folders: folders where we need to look int
        :param match: a function that defines if you want to include the file into the output. The first parameter
            is the folder containing the given file. The second parameter is the involved file. The third is the
            absolute path of the involved path
        :return: file compliant with the given function or None
        """
        result = self.find_first_file_in_roots_st(root_folders, match)
        if result is None:
            raise ValueError(f"Could not find file satisfying the given criterion from the root {root_folders}!")
        return result

    @pm.register_command.add("files")
    def find_folder_st(self, root_folder: pm.path, match: Callable[[pm.path, str, pm.path], bool]) -> Iterable[str]:
        """
        Find all the folder matching a given function

        :param root_folder: folder where we need to look int
        :param match: a function that defines if you want to include the folder into the output. The first parameter
            is the folder containing the given folder. The second parameter is the involved folder. The third is the
            absolute path of the involved path
        :return: list of folders compliant with the given function
        """

        for root, dirs, files in os.walk(root_folder):
            for f in dirs:
                whole_path = os.path.join(root, f)
                if match(root, f, whole_path):
                    yield whole_path

    @pm.register_command.add("files")
    def copy_files_that_basename(self, src: pm.path, dst: pm.path, regex: str):
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
        s = self.paths.abs_path(src)
        d = self.paths.abs_path(dst)
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

    @pm.register_command.add("files")
    def move_tree(self, src: pm.path, dst: pm.path):
        """
        Move an entire directory tree from one position to another one

        :param src: path of the directory to move
        :param dst: path of the directory that we will create
        """
        self._log_command(f"""Recursively move files from \"{src}\" to \"{dst}\"""")
        self.copy_tree(src, dst)
        self.remove_tree(src)

    @pm.register_command.add("files")
    def remove_tree(self, *folder: pm.path, ignore_if_not_exists: bool = True) -> None:
        """
        Remove a dirctory tree

        :param folder: path to the directory to remove
        :param ignore_if_not_exists: if the directory does not exists, we do nothing if htis field is true
        """
        p = self.paths.abs_path(*folder)
        self._log_command(f"""Recursively remove files from \"{p}\"""")
        try:
            shutil.rmtree(p)
        except Exception as e:
            if not ignore_if_not_exists:
                raise e

    @pm.register_command.add("files")
    def remove_files_that_basename(self, src: pm.path, regex: str):
        """
        Remove the files located (directly or indirectly) in src.
        We will copy only the files whose basename (e.g. foo.txt is the basename of /opt/foo/bar/foo.txt).
        We will copy the directories where a file is located as well
        matches the given regex

        :param src: folder where we will find files to copy
        :param regex: regex that determines wether or not a file is copies
        :return:
        """
        s = self.paths.abs_path(src)
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

    @pm.register_command.add("files")
    def move_file(self, src: pm.path, dst: pm.path):
        """
        Move a single file from a location to another one

        :param src: the file to move
        :param dst: the path where the file will be moved to
        """
        asrc = self.paths.abs_path(src)
        adst = self.paths.abs_path(dst)
        self._log_command(f"""move file from \"{asrc}\" to \"{adst}\"""")
        shutil.move(asrc, adst)

    @pm.register_command.add("files")
    def remove_file(self, name: pm.path, ignore_if_not_exists: bool = True) -> bool:
        """
        Remove a file. If the cannot be removed (for some reason), ignore_if_not_exists determines if somethign goes wrong

        :param name: file to delete
        :param ignore_if_not_exists: if true, we won't raise exception if the file does not exists or cannot be removed
        :return: true if we have removed the file, false otherwise
        """
        p = self.paths.abs_path(name)
        self._log_command(f"remove file {p}")
        try:
            os.unlink(p)
            return True
        except Exception as e:
            if not ignore_if_not_exists:
                raise e
            return False

    @pm.register_command.add("files")
    def remove_string_in_file(self, name: pm.path, substring: str, count: int = -1, encoding: str = "utf-8"):
        """
        Remove some (or all) the occurences of a given substring in a file

        :param name: path of the file to handle
        :param substring: substring to replace
        :param count: the number of occurences to remove. -1 if you want to remove all occurences
        :param encoding: encoding used for reading the file
        """
        p = self.paths.abs_path(name)
        self._log_command(f"Remove substring \"{substring}\" in file {p} (up to {count} occurences)")
        with open(p, mode="r", encoding=encoding) as f:
            content = f.read()

        with open(p, mode="w", encoding=encoding) as f:
            content = content.replace(substring, "", count)
            f.write(content)

    @pm.register_command.add("files")
    def ls(self, folder: pm.path = None, generate_absolute_path: bool = False) -> Iterable[pm.path]:
        """
        Show the list of all the files in the given directory

        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders.
            Otherwise we will return only the
        :return: iterable of all the files in the given directory
        """
        if folder is None:
            folder = self.get_cwd()
        self._log_command(f"""listing files of folder \"{self.paths.abs_path(folder)}\"""")
        yield from self.platform.ls(folder, generate_absolute_path)

    @pm.register_command.add("files")
    def ls_only_files(self, folder: pm.path = None, generate_absolute_path: bool = False) -> Iterable[pm.path]:
        """
        Show the list of all the files (but not directories) in the given directory

        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders. Otherwise we will return only the
        :return:
        """
        if folder is None:
            folder = self.get_cwd()
        p = self.paths.abs_path(folder)
        self._log_command(f"""listing files in fodler \"{p}\"""")
        yield from self.platform.ls_only_files(p, generate_absolute_path)

    @pm.register_command.add("files")
    def ls_only_directories(self, folder: pm.path = None, generate_absolute_path: bool = False) -> Iterable[pm.path]:
        """
        Show the list of all the directories in the given directory

        :param folder: folder to scan. default to CWD
        :param generate_absolute_path: if true, we will generate in the outptu the absolute path of the subfolders. Otherwise we will return only the
        names
        :return:
        """
        if folder is None:
            folder = self.get_cwd()
        p = self.paths.abs_path(folder)
        self._log_command(f"""listing folders in folder \"{p}\"""")
        yield from self.platform.ls_only_directories(p, generate_absolute_path)

    @pm.register_command.add("files")
    def ls_recursive(self, folder: pm.path = None) -> Iterable[pm.path]:
        """
        Show the list of all the files in the given folder

        :param folder: folder to scan (default to cwd)
        :return: list of absolute filename representing the stored files
        """
        self._log_command(f"""listing direct and indirect files of folder \"{self.paths.abs_path(folder)}\"""")
        for dirpath, dirnames, filenames in os.walk(folder):
            # dirpath: the cwd wheren dirnames and filesnames are
            # dirnames: list of all the directories in dirpath
            # filenames: list of all the files in dirpath
            for filename in filenames:
                yield self.paths.abs_path(os.path.join(dirpath, filename))

    @pm.register_command.add("files")
    def ls_directories_recursive(self, folder: pm.path) -> Iterable[pm.path]:
        """
        Show the list of all the directories in the given folder

        :param folder: folder to scan (default to cwd)
        :return: list of absolute filename representing the stored directories
        """
        self._log_command(f"""listing direct and indirect folders of folder \"{self.paths.abs_path(folder)}\"""")
        for dirpath, dirnames, filenames in os.walk(folder):
            # dirpath: the cwd wheren dirnames and filesnames are
            # dirnames: list of all the directories in dirpath
            # filenames: list of all the files in dirpath
            for dirname in dirnames:
                yield self.paths.abs_path(os.path.join(dirpath, dirname))


FilesPMakeupPlugin.autoregister()
