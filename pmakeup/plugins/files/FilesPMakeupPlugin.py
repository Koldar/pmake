import re
from typing import Iterable, Union, Optional

from pmakeup.commons_types import path
from pmakeup.decorators import show_on_help
from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin


class FilesPMakeupPlugin(AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        pass

    @show_on_help.add_command('files')
    def find_regex_match_in_file(self, pattern: str, *p: path, encoding: str = "utf8",
                                 flags: Union[int, re.RegexFlag] = 0) -> Optional[re.Match]:
        """
        FInd the first regex pattern in the file

        If you used named capturing in the pattern, you can gain access via result.group("name")

        :param pattern: regex pattern to consider
        :param p: file to consider
        :param encoding: encoding of the file to search. Defaults to utf8
        :param flags: flags of the regex to build. Passed as-is
        :return a regex match representing the first occurence. If None we could not find anything
        """

        fn = self.abs_wrt_cwd(*p)
        self._log_command(f"""Looking for pattern {pattern} in file {fn}.""")
        with open(fn, mode="r", encoding=encoding) as f:
            content = f.read()

        return re.search(pattern, content, flags=flags)

    @show_on_help.add_command('files')
    def replace_string_in_file(self, name: path, substring: str, replacement: str, count: int = -1,
                               encoding: str = "utf-8"):
        """
        Replace some (or all) the occurences of a given substring in a file

        :param name: path of the file to handle
        :param substring: substring to replace
        :param replacement: string that will replace *substring*
        :param count: the number of occurences to replace. -1 if you want to replace all occurences
        :param encoding: encoding used for reading the file
        """
        p = self.abs_path(name)
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

    @show_on_help.add_command('files')
    def replace_regex_in_file(self, name: path, regex: str, replacement: str, count: int = -1,
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

        p = self.abs_path(name)
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
