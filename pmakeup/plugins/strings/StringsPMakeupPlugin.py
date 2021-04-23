import re
from typing import Iterable

import pmakeup as pm


class StringsPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("strings")
    def replace_regex_in_string(self, string: str, regex: str, replacement: str, count: int = -1,
                              encoding: str = "utf-8") -> str:
        """
        Replace some (or all) the occurences of a given string

        If you want to use named capturing group, you can do so! For instance,

        replace_regex_in_string('3435spring9437', r'(?P<word>[a-z]+)', r'\1aa')
        'spring' will be replaced with 'springaa'

        It may not work, so you can use the following syntax to achieve the same:
        replace_regex_in_file(file_path, '(?P<word>\\w+)', r'\\g<word>aa')
        'spring' will be replaced with 'springaa'


        :param string: string that will be involved in the replacements
        :param regex: regex to replace
        :param replacement: string that will replace *substring*
        :param count: the number of occurences to replace. -1 if you want to replace all occurences
        :param encoding: encoding used for reading the file
        :see: https://docs.python.org/3/howto/regex.html
        """
        pattern = re.compile(regex)
        if count < 0:
            count = 0

        content = re.sub(
            pattern=pattern,
            repl=replacement,
            string=string,
            count=count,
        )
        return content

    @pm.register_command.add("strings")
    def match(self, string: str, regex: str) -> bool:
        """
        Check if a given string matches perfectly the given regex

        :param string: the sting to check
        :param regex: the regex to check. The syntax is available at https://docs.python.org/3/library/re.html
        :return: true if such a substring can be found, false otherwise
        """
        m = re.match(regex, string)
        return m is not None

    @pm.register_command.add("strings")
    def search(self, string: str, regex: str):
        """
        Check if a given string has a substring that matches the given regex

        :param string: the sting to check
        :param regex: the regex to check. The syntax is available at https://docs.python.org/3/library/re.html
        :return: true if such a substring can be found, false otherwise
        """
        m = re.match(regex, string)
        return m is not None

    @pm.register_command.add("strings")
    def replace_substring_in_string(self, string: str, substring: str, replacement: str, count: int = -1) -> str:
        """
        Replace some (or all) the occurences of a given string

        :param string: string that will be involved in the replacements
        :param substring: the string to repplace
        :param replacement: string that will replace *substring*
        :param count: the number of occurences to replace. -1 if you want to replace all occurences
        """

        content = string.replace(substring, replacement, count)
        return content


StringsPMakeupPlugin.autoregister()
