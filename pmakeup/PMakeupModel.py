import abc
import logging
import os
import re
import networkx as nx
import textwrap
import traceback
from typing import Any, Dict, Optional, List, Iterable, Union

import colorama

from pmakeup.PMakeupRegistry import PMakeupRegistry
from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin
from pmakeup.IPMakeupCache import IPMakeupCache
from pmakeup.cache.JsonPMakeupCache import JsonPMakeupCache
from pmakeup.TargetDescriptor import TargetDescriptor
from pmakeup.SessionScript import SessionScript, AbstractSessionScript
from pmakeup.commons_types import path
from pmakeup.constants import STANDARD_MODULES, STANDARD_VARIABLES
from pmakeup.LinuxSessionScript import LinuxSessionScript
from pmakeup.WindowsSessionScript import WindowsSessionScript


class AttrDict(object):

    def __init__(self, d):
        self.__d = d

    def __getattr__(self, item: str) -> Any:
        return self.__d[item]

    def __getitem__(self, item: str) -> Any:
        return self.__d[item]

    def __contains__(self, item) -> bool:
        return item in self.__d

    def has_key(self, item: str) -> bool:
        return item in self


class PMakeupModel(abc.ABC):
    """
    The application model of pmakeup progam
    """

    def __init__(self):
        self.input_file: Optional[str] = None
        """
        File representing the "Makefile" of pmakeup
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
        Variables that the user can inject from the command line
        """
        self.info_description: str = ""
        """
        Description to show whenever the user wants to know what a given Pmakeupfile does
        """
        self.target_network: nx.DiGraph = nx.DiGraph(name="targets")
        """
        Variables passed by the user from the command line via "--variable" argument
        """
        self.available_targets: Dict[str, TargetDescriptor] = {}
        """
        List of available targets the given pmakeupfile provides
        """
        self.requested_target_names: List[str] = []
        """
        List of targets that the user wants to perform. This
        list of targets are mpretty mch like the make one's (e.g., all, clean, install, uninstall)
        """
        self.should_show_target_help: bool = False
        """
        If true, we will print the information on how to use the given PMakefile
        """
        self.starting_cwd: path = os.path.abspath(os.curdir)
        """
        current working directory when pamke was executed
        """
        self.pmake_cache: Optional["IPMakeupCache"] = None
        """
        Cache containing data that the user wants t persist between different pmakeup runs
        """
        self._pmakefiles_include_stack: List[path] = []
        """
        Represents the PMakefile pmakeup is handling. Each time we include something, the code within it is executed.
        If an error occurs, we must know where the error is. Hence this variable is pretty useful to detect that.
        This list acts as a stack
        """
        self._eval_globals: PMakeupRegistry = PMakeupRegistry()

        # initialize the container that holds all the functions that can be used inside pmakeup
        self._plugin_graph: nx.DiGraph = nx.DiGraph(name="Plugin graph")

        self._setup_plugin_graph()

    def is_plugin_registered(self, plugin: Union[str, "AbstractPmakeupPlugin"]) -> bool:
        """
        At least one plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :return: true if the plugin is already been registered in the model, false otheriwse
        """
        if isinstance(plugin, str):
            plugin = plugin
        elif isinstance(plugin, AbstractPmakeupPlugin):
            plugin = plugin.get_plugin_name()
        else:
            raise TypeError(f"is_plugin_registered: only str or object is allowed")

        return plugin in set(map(lambda n: n.get_plugin_name(), self._plugin_graph.nodes))

    def _ensure_plugin_is_registered(self, plugin: Union[str, "AbstractPmakeupPlugin"]):
        """
        Ensure that at least one plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :raises ValueError: if the plugin is not registered at all
        """
        if not self.is_plugin_registered(plugin):
            raise ValueError(f"Plugin \"{plugin}\" not registered at all!")

    def _ensure_plugin_is_not_registered(self, plugin: Union[str, "AbstractPmakeupPlugin"]):
        """
        Ensure that no plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :raises ValueError: if the plugin is registered
        """
        if self.is_plugin_registered(plugin):
            raise ValueError(f"Plugin \"{plugin}\" has already been registered!")

    def get_plugin_by_name(self, name: str) -> "AbstractPmakeupPlugin":
        """
        Fetch a plugin with the given type

        :param plugin. type of the plugin to look for
        :return: an instance of the given plugin
        """

        for aplugin in self._plugin_graph.nodes:
            if aplugin.get_plugin_name() == name:
                return aplugin
        else:
            raise ValueError(f"Cannot find a plugin named \"{name}\"")

    def get_plugins(self) -> Iterable[AbstractPmakeupPlugin]:
        """
        get all the registered plugin up to this point
        """
        return list(self._plugin_graph.nodes)

    def _add_plugin(self, plugin: "AbstractPmakeupPlugin", ignore_if_already_registered: bool) -> bool:
        """
        Add a new instance of a plugin in the plugin dependency graph

        :param plugin: plugin to add
        :param ignore_if_already_registered: if true, we will not generate an exception if the plugin was already registered
        :return: true if the plugin was registered
        """
        if ignore_if_already_registered:
            if not self.is_plugin_registered(plugin):
                self._plugin_graph.add_node(plugin)
                return True
            return False
        else:
            self._ensure_plugin_is_not_registered(plugin)
            self._plugin_graph.add_node(plugin)
            return True

    def _has_edge_with_label(self, source: AbstractPmakeupPlugin, sink: AbstractSessionScript, label: str) -> bool:
        """
        Check if the plugin graph cojntains an edge from "source" to "sink" labelled as "label"

        :param source: the source plugin instance
        :param sink: the sink plugin instance
        :param label: label to check
        """
        return self._plugin_graph.edges[source, sink]['weight'] == label

    def _add_setup_dependency(self, plugin: AbstractPmakeupPlugin, depends_on: AbstractPmakeupPlugin):
        if not self.is_plugin_registered(depends_on):
            # the plugin we depend upon is not registered at all. We need to register it
            raise ValueError(f"Cannot find a dependency of the plugin {plugin}: plugin {depends_on} not found. Can you install it and add it to require_pmakeup_plugins please?")
        if self._plugin_graph.has_edge(plugin, depends_on, "setup"):
            raise ValueError(f"plugins {plugin} -> {depends_on} already has a dependency")
        self._plugin_graph.add_edge(plugin, depends_on, "setup")
        # now check for cycles (there cannot be cycles in the graph)
        if not nx.algorithms.is_directed_acyclic_graph(self._plugin_graph):
            raise ValueError(f"Cycle depetected within plugin dependencies!")

    def register_plugins(self, *plugin: Union[str]):
        updated = False
        for p in plugin:
            updated = updated or self._add_plugin(p, ignore_if_already_registered=True)
        if updated:
            self._setup_plugin_graph_and_update_eval_globals()

    def _setup_plugin_graph_and_update_eval_globals(self):
        """
        Populate the plugin graph manager

        """

        self._add_plugin(SessionScript(self), ignore_if_already_registered=True)

        if os.name == "nt":
            self._add_plugin(WindowsSessionScript(self), ignore_if_already_registered=True)
        elif os.name == "posix":
            self._add_plugin(LinuxSessionScript(self), ignore_if_already_registered=True)
        else:
            raise ValueError(f"Cannot identify current operating system! os.name = {os.name}")

        # add setup dependencies
        for plugin in self._plugin_graph.nodes:
            if not plugin.is_setupped:
                for plugin_dependency in plugin._get_dependencies():
                    logging.debug(f"Add dependency between {plugin} -> {plugin_dependency}...")
                    self._add_setup_dependency(plugin, plugin_dependency)

        # ok, now setup the graph
        for plugin in nx.algorithms.dfs_preorder_nodes(self._plugin_graph):
            logging.debug(f"Setupping pligun {plugin}...")
            if not plugin.is_setupped:
                plugin.setup_plugin()
            plugin._is_setupped = True

        logging.info(f"All plugins have been successfully setupped!")

        self._update_eval_global()

    def _update_eval_global(self):
        """
        Collect all the functions that are readibly usable from pmakefile scripts
        """

        # dump all the functions inside the global_eval. Don't set global_eval by itself,
        # since it may be used by a runnign execute statement

        for plugin in self.get_plugins():
            # register the plugin in the eval: in this way the user can call a specific plugin function
            # if she really wants to
            if plugin.get_plugin_name() not in self._eval_globals:
                self._eval_globals[plugin.get_plugin_name()] = plugin
            # register all the plugin functions in eval
            for name, function in plugin.get_plugin_functions():
                if name not in self._eval_globals:
                    self._eval_globals[name] = function

        # Standard modules
        for k, v in STANDARD_MODULES:
            if k not in self._eval_globals:
                logging.debug(f"Adding standard variable {k}")
                self._eval_globals[k] = v

        # Standard variables
        for name, value, description in STANDARD_VARIABLES:
            if name not in self._eval_globals:
                self._eval_globals[name] = value

        # user specific variables
        if "variables" in self._eval_globals:
            raise KeyError(f"duplicate key \"variables\". It is already mapped to the value {global_eval['variables']}")
        logging.debug(f"Adding standard variable 'variable'")
        attr_dict = {}
        for k, v in self.variable.items():
            attr_dict[k] = self.variable[k]
        self.variable = attr_dict
        self._eval_globals.variables = AttrDict(attr_dict)
        logging.info(f"VARIABLES PASSED FROM CLI")
        for i, (k, v) in enumerate(self.variable.items()):
            logging.info(f' {i}. {k} = {v}')

        if "model" in global_eval:
            raise KeyError(f"duplicate key \"model\". It is already mapped to the value {global_eval['model']}")
        logging.debug(f"Adding standard variable 'model'")
        global_eval["model"] = self

        if "requested_target_names" in global_eval:
            raise KeyError(f"duplicate key \"requested_target_names\". It is already mapped to the value {global_eval['targets']}")
        logging.debug(f"Adding standard variable 'requested_target_names'")
        global_eval["requested_target_names"] = self.requested_target_names

        if "interesting_paths" in result:
            raise KeyError(f"duplicate key \"interesting_paths\". It is already mapped to the value {result['interesting_paths']}")
        logging.debug(f"Adding standard variable 'interesting_paths'")
        result["interesting_paths"] = self.session_script._interesting_paths

        logging.info(f"INTERESTING PATHS")
        for i, (k, values) in enumerate(self.session_script._interesting_paths.items()):
            logging.info(f" - {i+1}. {k}: {', '.join(map(str, values))}")

        if "latest_interesting_path" in result:
            raise KeyError(
                f"duplicate key \"latest_interesting_path\". It is already mapped to the value {result['latest_interesting_path']}")
        logging.debug(f"Adding standard variable 'latest_interesting_path'")
        result["latest_interesting_path"] = self.session_script._latest_interesting_path

        logging.info(f"LATEST INTERESTING PATHS")
        for i, (k, v) in enumerate(self.session_script._latest_interesting_path.items()):
            logging.info(f" - {i+1}. {k}: {v}")

        logging.info(f"USER REQUESTED TARGETS")
        for i, t in enumerate(self.requested_target_names):
            logging.info(f" - {i+1}. {t}")

        return global_eval

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
        Read the Pmakefile instructions from a configured option.
        For example, if "input_string" is set, invoke from it.
        If "input_file" is set, invoke from it
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

        try:
            # add a new level in the stack
            self._pmakefiles_include_stack.append(input_file)
            # execute the file
            self.execute_string(input_str)
        finally:
            self._pmakefiles_include_stack.pop()

    def execute_string(self, string: str):
        """
        Execute the content of a string
        :param string: string to execute
        :return:
        """

        try:
            # remove the first line if it is empty
            string = textwrap.dedent(string)
            logging.debug("input string:")
            logging.debug(string)
            self._update_eval_global()
            if self.pmake_cache is None:
                # set tjhe pmakeup cache
                self.pmake_cache = JsonPMakeupCache("pmakeup-cache.json")
            # now execute the string
            exec(
                string,
                self._eval_globals,
                self._eval_globals
            )
        except Exception as e:
            print(f"{colorama.Fore.RED}Exception occured:{colorama.Style.RESET_ALL}")
            trace = traceback.format_exc()
            # Example of "trace"
            # Traceback (most recent call last):
            #   File "pmake/PMakeupModel.py", line 197, in execute_string
            #   File "<string>", line 43, in <module>
            #   File "<string>", line 43, in <lambda>
            # NameError: name 'ARDUINO_LIBRARY_LOCATION' is not defined
            lines = trace.splitlines()
            print(f"{colorama.Fore.RED}{traceback.format_exc()}{colorama.Style.RESET_ALL}")
            lines = lines[1:-1]
            last_line = lines[-1]

            # fetch line number
            try:
                line_no = last_line.split(", ")[1]
                m = re.match(r"^\s*line\s*([\d]+)$", line_no)
                line_no = m.group(1)
                line_no = int(line_no)
            except:
                line_no = "unknown"

            # fetch file name
            try:
                file_path = last_line.split(", ")[0]
                m = re.match(r"^\s*File\s*\"([^\"]+)\"$", file_path)
                file_path = m.group(1)
                if file_path == "<string>":
                    # this occurs when the problem is inside a PMakefile. We poll the stack
                    file_path = self._pmakefiles_include_stack[-1]
            except:
                file_path = "unknown"

            # logging.critical(f"{colorama.Fore.RED}{trace}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}Cause = {e}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}File = {file_path}{colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED}Line = {line_no}{colorama.Style.RESET_ALL}")
            raise e

