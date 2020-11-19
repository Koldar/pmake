import abc
import logging
import os
import textwrap
from typing import Any, Dict, Optional, List

import colorama

from pmake.JsonPMakeCache import JsonPMakeCache
from pmake.commands import SessionScript
from pmake.commons_types import path
from pmake.constants import STANDARD_MODULES, STANDARD_VARIABLES
from pmake.linux_commands import LinuxSessionScript
from pmake.windows_commands import WindowsSessionScript


class AttrDict(object):

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
        """
        File representing the "Makefile" of pmake
        """
        self.input_string: Optional[str] = None
        """
        String to be used in place of ::input_file
        """
        self.input_encoding: Optional[str] = None
        """
        Encoding of ::input_file
        """
        self.log_level: Optional[str] = None
        """
        level of the logger. INFO, DEBUG, CRITICAL
        """

        self.variable: Dict[str, Any] = {}
        """
        Variables passed by the user from the command line via "--variable" argument
        """
        self.targets: List[str] = []
        """
        List of targets that the user wants to perform. This
        list of targets are mpretty mch like the make one's (e.g., all, clean, install, uninstall)
        """
        self.starting_cwd: path = os.path.abspath(os.curdir)
        """
        current working directory when pamke was executed
        """
        self.pmake_cache: Optional["IPMakeCache"] = None
        """
        Cache containing data that the user wants t persist between different pmake runs
        """
        self._eval_globals: Optional[Dict[str, Any]] = None
        self._eval_locals: Optional[Dict[str, Any]] = None

        if os.name == "nt":
            self.session_script: "SessionScript" = WindowsSessionScript(self)
        elif os.name == "posix":
            self.session_script: "SessionScript" = LinuxSessionScript(self)
        else:
            self.session_script: "SessionScript" = SessionScript(self)

    def _get_eval_global(self) -> Dict[str, Any]:
        result = dict()
        for k in dir(self.session_script):
            if k.startswith("_"):
                continue
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            logging.debug(f"Adding variable {k}")
            result[k] = getattr(self.session_script, k)

        for k, v in STANDARD_MODULES:
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            logging.debug(f"Adding standard variable {k}")
            result[k] = v
        for name, value, description in STANDARD_VARIABLES:
            if name in result:
                raise KeyError(f"duplicate key \"{name}\". It is already mapped to the value {result[name]}")
            result[name] = value

        # SPECIAL VARIABLES

        if "variables" in result:
            raise KeyError(f"duplicate key \"variables\". It is already mapped to the value {result['variables']}")
        logging.debug(f"Adding standard variable 'variable'")
        result["variables"] = AttrDict({k: v for k, v in self.variable})

        if "model" in result:
            raise KeyError(f"duplicate key \"model\". It is already mapped to the value {result['model']}")
        logging.debug(f"Adding standard variable 'model'")
        result["model"] = self

        if "commands" in result:
            raise KeyError(f"duplicate key \"commands\". It is already mapped to the value {result['commands']}")
        logging.debug(f"Adding standard variable 'commands'")
        result["commands"] = self.session_script

        if "targets" in result:
            raise KeyError(f"duplicate key \"targets\". It is already mapped to the value {result['targets']}")
        logging.debug(f"Adding standard variable 'targets'")
        result["targets"] = self.targets

        if "interesting_paths" in result:
            raise KeyError(f"duplicate key \"interesting_paths\". It is already mapped to the value {result['interesting_paths']}")
        logging.debug(f"Adding standard variable 'interesting_paths'")
        result["interesting_paths"] = self.session_script._interesting_paths

        if "latest_interesting_path" in result:
            raise KeyError(
                f"duplicate key \"latest_interesting_path\". It is already mapped to the value {result['latest_interesting_path']}")
        logging.debug(f"Adding standard variable 'latest_interesting_path'")
        result["latest_interesting_path"] = self.session_script._latest_interesting_path

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
            logging.critical(f"{colorama.Fore.RED}exception occured {e}{colorama.Style.RESET_ALL}")
            raise e

