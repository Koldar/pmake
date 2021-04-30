import re
from typing import Any, Iterable, Tuple, List

import pmakeup as pm


class UtilsPMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("utils")
    def grep(self, lines: Iterable[str], regex: str, reverse_match: bool = False) -> Iterable[str]:
        """
        Filter the lines fetched from terminal

        :param lines: the lines to fetch
        :param regex: a python regex. If a line contains a substring which matches the given regex, the line is returned
        :param reverse_match: if True, we will return lines which do not match the pattern
        :return: lines compliant with the regex
        """
        for line in lines:
            m = re.search(regex, line)
            if reverse_match:
                if m is None:
                    yield line
            else:
                if m is not None:
                    yield line

    @pm.register_command.add("utils")
    def get_column_of_table(self, table: List[List[str]], index: int) -> List[str]:
        """
        Select a single column from the table, generated by ::convert_table

        :param table: the table generated by ::convert_table
        :param index: index of the column to return. Starts from 0
        :return: the column requested
        """
        return list(map(lambda x: x[index], table))

    @pm.register_command.add("utils")
    def get_column_of_table_by_name(self, table: List[List[str]], column_name: str) -> List[str]:
        """
        Select a single column from the table, generated by ::convert_table
        We assumed the first row of the table is a header, contaiing the column names

        :param table: the table generated by ::convert_table
        :param column_name: name of the column to return.
        :return: the column requested
        """
        header = table[0]
        column_index = None
        for index, name in enumerate(header):
            if name == column_name:
                column_index = index
                break
        if column_index is None:
            raise pm.PMakeupException(f"Cannot find column named '{column_name}' in header: {', '.join(header)}")

        return self.get_column_of_table(table, column_index)

    @pm.register_command.add("utils")
    def convert_table(self, table_str: str) -> List[List[str]]:
        """
        Convert a table printed as:

        Port         Type              Board Name              FQBN                 Core
        /dev/ttyACM1 Serial Port (USB) Arduino/Genuino MKR1000 arduino:samd:mkr1000 arduino:samd

        Into a list of lists of strings

        :param table_str: representation of a table
        :return: list of lists of strings
        """

        def is_column(index: int, lines: List[str]) -> bool:
            column_found = True
            # a column is found when in all lines the same character is " "
            for line in lines:
                # the char in index needs to be a whitespace for all lines
                column_found = line[index] == " "
                if not column_found:
                    return False
                # the char after index needs not to be a whitespace for all lines
                if 0 < (index + 1) < len(line):
                    column_found = line[index + 1] != " "
                if not column_found:
                    return False
            return True

        column_index = [0]
        result = []
        lines = list(
            filter(
                lambda x: len(x) > 0,
                map(
                    lambda x: x.strip(),
                    table_str.split("\n")
                )
            )
        )
        min_length = min(map(lambda x: len(x), lines))
        for index in range(min_length):
            if is_column(index, lines):
                column_index.append(index + 1)
        # append last column
        column_index.append(-1)

        for line in lines:
            tmp = []
            for (start, end) in self.pairs(column_index):
                if end == -1:
                    tmp.append(line[start:].strip())
                else:
                    tmp.append(line[start:(end - 1)].strip())
            result.append(tmp)

        return result

    @pm.register_command.add("utils")
    def pairs(self, it: Iterable[Any]) -> Iterable[Tuple[Any, Any]]:
        """
        Convert the iterable into an iterable of pairs.

        1,2,3,4,5,6 becomes (1,2), (2,3), (3,4), (4,5), (5,6)

        :param it: iterable whose sequence we need to generate
        :return: iterable of pairs
        """
        previous = None
        for x in it:
            if previous is None:
                previous = x
            else:
                yield previous, x
                previous = x

    @pm.register_command.add("utils")
    def as_bool(self, v: Any) -> bool:
        """
        Convert a value into a boolean

        :param v: value to convert as a boolean
        :return: true of false
        """
        if isinstance(v, bool):
            return v
        elif isinstance(v, str):
            v = v.lower()
            d = {
                "true": True,
                "false": False,
                "ok": True,
                "ko": False,
                "yes": True,
                "no": False,
                "1": True,
                "0": False
            }
            return d[v]
        elif isinstance(v, int):
            return v != 0
        else:
            raise TypeError(f"Cannot convert {v} (type {type(v)}) into a bool")


UtilsPMakeupPlugin.autoregister()