import abc
import logging
import textwrap
from pyexpat import model
from typing import Any, Dict, Optional

import colorama

from pmake.IPMakeCache import IPMakeCache
from pmake.JsonPMakeCache import JsonPMakeCache
from pmake.commands import SessionScript
from pmake.commons_types import path
from pmake.constants import STANDARD_MODULES, STANDARD_VARIABLES


class AttrDict():
    """
    A dictioanry whose values can be accessed with "." notation.
    For instance:

    d.foo is the same as d["foo"]
    """

    def __init__(self, d):
        self.__d = d

    def __getattr__(self, item: str) -> Any:
        return self.__d[item]

    def __getitem__(self, item: str) -> Any:
        return self.__d[item]


class PMakeModel(abc.ABC):
    """
    The application model of pmake progam
    """

    def __init__(self):
        self.input_file: Optional[str] = None
        self.input_string: Optional[str] = None
        self.input_encoding: Optional[str] = None
        self.log_level: Optional[str] = None
        self.session_script: "SessionScript" = SessionScript(self)
        self.variable: Dict[str, Any] = {}
        self.pmake_cache: Optional["IPMakeCache"] = None
        self._eval_globals: Optional[Dict[str, Any]] = None
        self._eval_locals: Optional[Dict[str, Any]] = None

    def _get_eval_global(self) -> Dict[str, Any]:
        result = dict()
        for k in dir(self.session_script):
            if k.startswith("_"):
                continue
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            result[k] = getattr(self.session_script, k)

        for k, v in STANDARD_MODULES:
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            result[k] = v
        for name, value, description in STANDARD_VARIABLES:
            if name in result:
                raise KeyError(f"duplicate key \"{name}\". It is already mapped to the value {result[name]}")
            result[name] = value

        if "variables" in result:
            raise KeyError(f"duplicate key \"variables\". It is already mapped to the value {result['variables']}")
        result["variables"] = AttrDict({k: v for k, v in self.variable})

        return result

    def _get_eval_locals(self) -> Dict[str, Any]:
        return {

        }

    def manage_pmakefile(self):
        """
        Main function used to programmatically call the application
        :return:
        """
        # initialize colorama
        try:
            colorama.init()
            self.execute()
        finally:
            colorama.deinit()
            if self.pmake_cache is not None:
                self.pmake_cache.update_cache()

    def execute(self):
        """
        Read the content of the PMakefile and executes it
        :return:
        """

        if self.input_string is not None:
            self.execute_string(self.input_string)
        else:
            self.execute_file(self.input_file)

    def execute_file(self, input_file: path):
        """
        Execute the content in a file
        :param input_file: file containing the code to execute
        :return:
        """

        with open(input_file, "r", encoding=self.input_encoding) as f:
            input_str = f.read()

        self.execute_string(input_str)

    def execute_string(self, string: str):
        """
        Execute the content of a string
        :param string: string to execute
        :return:
        """

        try:
            # remove the first line if it is empty
            string = string
            string = textwrap.dedent(string)
            logging.debug("input string:")
            logging.debug(string)
            if self._eval_locals is None:
                self._eval_locals = self._get_eval_locals()
            if self._eval_globals is None:
                self._eval_globals = self._get_eval_global()
            if self.pmake_cache is None:
                self.pmake_cache = JsonPMakeCache("pmake-cache.json")
            exec(
                string,
                self._eval_globals,
                self._eval_locals
            )
        except Exception as e:
            logging.critical(f"exception occured {e}")
            raise e

