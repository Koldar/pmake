import abc
import datetime
import importlib
import inspect
import itertools
import logging
import math
import os
import platform
import re
import networkx as nx
import textwrap
import traceback
from typing import Any, Dict, Optional, List, Iterable, Union

import colorama
import typing
import importlib.util

import pkg_resources
from pkg_resources import EggInfoDistribution

import pmakeup as pm


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
        self.cli_variables: Dict[str, Any] = {}
        """
        Variables that the user can inject from the command line. Read only
        """
        self.info_description: str = ""
        """
        Description to show whenever the user wants to know what a given Pmakeupfile does
        """
        self.target_network: nx.DiGraph = nx.DiGraph(name="targets")
        self.available_targets: Dict[str, pm.TargetDescriptor] = {}
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
        self.starting_cwd: pm.path = os.path.abspath(os.curdir)
        """
        current working directory when pamke was executed
        """
        self.pmake_cache: Optional["pm.IPMakeupCache"] = None
        """
        Cache containing data that the user wants t persist between different pmakeup runs
        """
        self._pmakefiles_include_stack: List[pm.path] = []
        """
        Represents the PMakefile pmakeup is handling. Each time we include something, the code within it is executed.
        If an error occurs, we must know where the error is. Hence this variable is pretty useful to detect that.
        This list acts as a stack
        """
        self._eval_globals: "pm.PMakeupRegistry" = pm.PMakeupRegistry()
        self._platform: "pm.IOSSystem" = self._get_platform()
        """
        Object that allows you to interact in a system dependent way w.r.t the operating system
        """

        # initialize the container that holds all the functions that can be used inside pmakeup
        self._plugin_graph: nx.DiGraph = nx.DiGraph(name="Plugin graph")

    def is_plugin_registered(self, plugin: Union[str, "pm.AbstractPmakeupPlugin"]) -> bool:
        """
        At least one plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :return: true if the plugin is already been registered in the model, false otheriwse
        """
        if isinstance(plugin, str):
            plugin = plugin
        elif isinstance(plugin, pm.AbstractPmakeupPlugin):
            plugin = plugin.get_plugin_name()
        else:
            raise TypeError(f"is_plugin_registered: only str or object is allowed")

        return plugin in set(map(lambda n: n.get_plugin_name(), self._plugin_graph.nodes))

    def _ensure_plugin_is_registered(self, plugin: Union[str, "pm.AbstractPmakeupPlugin"]):
        """
        Ensure that at least one plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :raises ValueError: if the plugin is not registered at all
        """
        if not self.is_plugin_registered(plugin):
            raise ValueError(f"Plugin \"{plugin}\" not registered at all!")

    def _ensure_plugin_is_not_registered(self, plugin: Union[str, "pm.AbstractPmakeupPlugin"]):
        """
        Ensure that no plugin instance has been initialized in the plugin graph

        :param plugin: plugin to check (or plugin name)
        :raises ValueError: if the plugin is registered
        """
        if self.is_plugin_registered(plugin):
            raise ValueError(f"Plugin \"{plugin}\" has already been registered!")

    def get_plugin(self, plugin: Union[str, type]) -> "pm.AbstractPmakeupPlugin":
        """
        Fetch a plugin with the given type

        :param plugin. type of the plugin to look for
        :return: an instance of the given plugin
        """

        if isinstance(plugin, str):
            plugin_name = plugin
        elif isinstance(plugin, type):
            plugin_name = plugin(self).get_plugin_name()
        else:
            raise TypeError(f"Invalid type when computing get_plugin. plugin is {plugin}")

        for aplugin in self._plugin_graph.nodes:
            if aplugin.get_plugin_name() == plugin_name:
                return aplugin
        else:
            raise ValueError(f"Cannot find a plugin named \"{plugin_name}\"")

    def get_plugin_by_name(self, name: str) -> "pm.AbstractPmakeupPlugin":
        """
        Fetch a plugin with the given type

        :param name: name of the plugin to look for
        :return: an instance of the given plugin
        """
        return self.get_plugin(name)

    def get_plugins(self) -> Iterable["pm.AbstractPmakeupPlugin"]:
        """
        get all the registered plugin up to this point
        """
        return list(self._plugin_graph.nodes)

    def _add_plugin(self, plugin: "pm.AbstractPmakeupPlugin", ignore_if_already_registered: bool) -> bool:
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

    def _has_edge_with_label(self, source: "pm.AbstractPmakeupPlugin", sink: "pm.AbstractPmakeupPlugin", label: str) -> bool:
        """
        Check if the plugin graph cojntains an edge from "source" to "sink" labelled as "label"

        :param source: the source plugin instance
        :param sink: the sink plugin instance
        :param label: label to check
        """
        return self._plugin_graph.edges[source, sink]['weight'] == label

    def _add_setup_dependency(self, plugin: "pm.AbstractPmakeupPlugin", depends_on: "pm.AbstractPmakeupPlugin"):
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
            self._setup_plugin_graph()
            self._update_eval_global()

    def __fetch_pmakeup_plugins_installed(self) -> Iterable[type]:

        for apackage in map(lambda p: p, pkg_resources.working_set):
            package: "EggInfoDistribution" = apackage

            if re.search(r"^pmakeup-plugin(s)?-.+", package.project_name) is None and re.search(
                    r".+-pmakeup-plugin(s)?$", package.key) is None:
                continue
            logging.info(
                f"Detected installed package {package.project_name} which should contains pmakeup plugins. Importing it")

            # get top level file
            top_level_file = os.path.join(package.egg_info, "top_level.txt")
            with open(top_level_file, encoding="utf8", mode="r") as f:
                main_package = f.read().strip()

            # get module init
            module_path = os.path.join(package.location, main_package, "__init__.py")
            logging.info(f"Main package = {main_package} Module path = {module_path}")
            spec = importlib.util.spec_from_file_location(main_package, module_path)

            # import
            module_instance = importlib.util.module_from_spec(spec)
            logging.info(f"Module {package.project_name} has been correctly imported")
            spec.loader.exec_module(module_instance)

            # fetch plugins
            for candidate_classname in dir(module_instance):
                candidate_class = getattr(module_instance, candidate_classname)
                if not inspect.isclass(candidate_class):
                    # consider only classes
                    continue
                if issubclass(candidate_class, pm.AbstractPmakeupPlugin):
                    yield candidate_class

    def _setup_plugin_graph(self):
        """
        Populate the plugin graph manager

        """

        plugin_class_to_instantiates = [
            pm.CorePMakeupPlugin,
            pm.PathsPMakeupPlugin,
            pm.FilesPMakeupPlugin,
            pm.LoggingPMakeupPlugin,
            pm.OperatingSystemPMakeupPlugin
        ]

        # specific operating system
        if platform.system() == "Windows":
            logging.info(f"Registering operating system plugin {pm.WindowsPMakeupPlugin}")
            plugin_class_to_instantiates.append(pm.WindowsPMakeupPlugin)
        elif platform.system() == "Linux":
            logging.info(f"Registering operating system plugin {pm.LinuxPMakeupPlugin}")
            plugin_class_to_instantiates.append(pm.LinuxPMakeupPlugin)
        else:
            raise ValueError(f"Invlaid platform {platform.system()}")

        # we need to scan all the install packages, fetch hte one insteresting for pmakeup. Then we need to create a plugin per class
        for plugin_class_to_instantiate in self.__fetch_pmakeup_plugins_installed():
            logging.info(f"Registering pip installed plugin {plugin_class_to_instantiate}")
            plugin_class_to_instantiates.append(plugin_class_to_instantiate)



        # at the init, PMAKEUP_PLUGINS_TO_REGISTER contains all plugins to setup

        for plugin_class_to_instantiate in pm.global_variables.PMAKEUP_PLUGINS_TO_REGISTER:
            logging.info(f"Registering PMAKEUP_PLUGINS_TO_REGISTER plugin {plugin_class_to_instantiate}")
            plugin_class_to_instantiates.append(plugin_class_to_instantiate)

        for plugin_class in plugin_class_to_instantiates:
            logging.debug(f"Registering plugin {type(plugin_class)}")
            self._add_plugin(plugin_class(self), ignore_if_already_registered=True)

        # add setup dependencies
        for plugin in self._plugin_graph.nodes:
            if not plugin.is_setupped:
                try:
                    for plugin_dependency in plugin._get_dependencies():
                        logging.debug(f"Add dependency between {plugin} -> {plugin_dependency}...")
                        self._add_setup_dependency(plugin, plugin_dependency)
                except Exception as e:
                    raise ValueError(f"Failed setupping the dependencies of plugin \"{plugin.get_plugin_name()}\"",e)

        # ok, now setup the graph
        for plugin in nx.algorithms.dfs_preorder_nodes(self._plugin_graph):
            logging.debug(f"Setupping plugin {plugin}...")
            if not plugin.is_setupped:
                plugin._setup_plugin()
            plugin._is_setupped = True

        logging.info(f"All plugins have been successfully setupped!")

    def _get_platform(self) -> pm.IOSSystem:
        """
        get the current operating system type

        :return: structure providing you specific operating system methods
        """
        if os.name == "nt":
            return pm.WindowsOSSystem(self)
        elif os.name == "posix":
            return pm.LinuxOSSystem(self)
        else:
            raise pm.PMakeupException(f"Cannot identify platform!")

    def _get_standard_module(self):
        """
        get the modules to always load into the developer
        """
        return [
            ("math", math),
            ("datetime", datetime),
            ("itertools", itertools),
            ("os", os),
            ("typing", typing)
        ]

    def _get_constants_to_add_in_registry(self):
        """
        get the variables that need to be loaded in the pmakeup registry
        """
        return [
            ("VERSION", pm.version.VERSION, "Version of the program"),
            ("UTCDATE", datetime.datetime.utcnow(), "time when the program started (in UTC)"),
            ("DATE", datetime.datetime.now(), "time when the program started (in user timezone)"),
        ]

    def _update_eval_global(self):
        """
        Collect all the functions that are readibly usable from pmakefile scripts
        """

        # dump all the functions inside the global_eval. Don't set global_eval by itself,
        # since it may be used by a runnign execute statement

        # ####################################################################################
        # ########################### CONSTANTS ##############################################
        # ####################################################################################

        # Standard constatns
        logging.debug(f"Adding standard constants in the pmakeup registry...")
        for variable_name, value, description in self._get_constants_to_add_in_registry():
            if not self._eval_globals.can_a_function_have_a_name(variable_name):
                raise ValueError(f"The standard variable cannot have the name {variable_name}!")
            if variable_name not in self._eval_globals.variables:
                self._eval_globals.variables[variable_name] = value

        logging.debug(f"Adding CWD in the pmakeup registry...")
        self._eval_globals.variables.cwd = os.path.abspath(os.curdir)
        # user specific variables: copy both in original_variables and in the actual variables
        logging.debug(f"Adding user injected variables from CLI in the pmakeup registry '{', '.join(self.cli_variables.keys())}'...")
        self._eval_globals.pmakeup_original_variables = pm.AttrDict({})
        logging.debug(f"Adding standard variable 'model'...")
        self._eval_globals.pmakeup_models = self
        logging.debug(f"Adding standard variable 'requested_target_names'...")
        self._eval_globals.pmakeup_requested_target_names = self.requested_target_names

        # ####################################################################################
        # ########################### PLUGINS ################################################
        # ####################################################################################

        logging.debug(f"Adding plugin in the pmakeup registry...")
        for plugin in self.get_plugins():
            # register the plugin in the eval: in this way the user can call a specific plugin function
            # if she really wants to
            logging.debug(f"trying to register {plugin.get_plugin_name()}....")
            if plugin.get_plugin_name() not in self._eval_globals:
                logging.debug(f"registering {plugin.get_plugin_name()}....")
                self._eval_globals.pmakeup_plugins[plugin.get_plugin_name()] = plugin
            # register all the plugin functions in eval
            for name, function in plugin.get_plugin_functions():
                if not self._eval_globals.can_a_function_have_a_name(name):
                    raise ValueError(f"The function available to the plugin \"{plugin.get_plugin_name()}\" cannot have the name \"{name}\"!")
                # register command in the root of globals
                if name not in self._eval_globals:
                    self._eval_globals[name] = function
                # register command in the "commands" section
                if name not in self._eval_globals.commands:
                    self._eval_globals.commands[name] = function

        # ####################################################################################
        # ########################### STANDARD MODULES #######################################
        # ####################################################################################

        logging.debug(f"Adding standard modules in the pmakeup registry...")
        for module_name, v in self._get_standard_module():
            if not self._eval_globals.can_a_function_have_a_name(module_name):
                raise ValueError(f"The standard module cannot have the name {module_name}!")
            if module_name not in self._eval_globals:
                logging.debug(f"Adding python standard module {module_name}")
                self._eval_globals[module_name] = v

        # ####################################################################################
        # ########################### VARIABLES PASSED BY CLI  ###############################
        # ####################################################################################

        # copy the variable dict inside the registry and put it in the pmakeup_original_variables
        for variable_name, variable_value in self.cli_variables.items():
            if not self._eval_globals.can_a_function_have_a_name(variable_name):
                raise ValueError(f"User injected variable cannot have the name {variable_name}!")
            self._eval_globals.pmakeup_original_variables[variable_name] = self.cli_variables[variable_name]

        # copy the variables from the CLI and put in in the root of the registry
        for variable_name, variable_value in self.cli_variables.items():
            if not self._eval_globals.can_a_function_have_a_name(variable_name):
                raise ValueError(f"User injected variable cannot have the name {variable_name}!")
            logging.debug(f"Adding variable {variable_name} in the registry under \"vars\"")
            self._eval_globals.variables[variable_name] = self.cli_variables[variable_name]

        # logging.info(f"VARIABLES PASSED FROM CLI")
        # for i, (k, v) in enumerate(self.variable.items()):
        #    logging.info(f' {i}. {k} = {v}')

        # we add the interesting paths at the very last moment:
        # this because if we need some data, we probably already have it

        logging.debug(f"Adding standard variable 'interesting_paths'...")
        self._eval_globals.pmakeup_interesting_paths = self._platform.fetch_interesting_paths(model=self)

        logging.debug(f"Adding standard variable 'latest_interesting_paths'...")
        self._eval_globals.pmakeup_latest_interesting_paths = self._platform.fetch_latest_interesting_paths(
            interesting_paths=self._eval_globals.pmakeup_interesting_paths,
            model=self
        )

        # DISPLAY SOME INFORMATION

        logging.info(f"INTERESTING PATHS")
        for i, (k, values) in enumerate(self._eval_globals.pmakeup_interesting_paths.items()):
            logging.info(f" - {i + 1}. {k}: {', '.join(map(str, values))}")

        logging.info(f"LATEST INTERESTING PATHS")
        for i, (k, v) in enumerate(self._eval_globals.pmakeup_interesting_paths.items()):
            logging.info(f" - {i+1}. {k}: {v}")

        logging.info(f"USER REQUESTED TARGETS")
        for i, t in enumerate(self.requested_target_names):
            logging.info(f" - {i+1}. {t}")

        return self._eval_globals

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

    def get_core_plugin(self) -> "pm.CorePMakeupPlugin":
        return self.get_plugin_by_name("CorePMakeupPlugin")

    def get_files_plugin(self) -> "pm.FilesPMakeupPlugin":
        return self.get_plugin_by_name("FilesPMakeupPlugin")

    def get_paths_plugin(self) -> "pm.PathsPMakeupPlugin":
        return self.get_plugin_by_name("PathsPMakeupPlugin")

    def execute(self):
        """
        Read the Pmakefile instructions from a configured option.
        For example, if "input_string" is set, invoke from it.
        If "input_file" is set, invoke from it
        :return:
        """

        self._setup_plugin_graph()
        self._update_eval_global()
        if self.input_string is not None:
            self.execute_string(self.input_string)
        else:
            self.execute_file(self.input_file)

    def execute_file(self, input_file: pm.path):
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
                self.pmake_cache = pm.JsonPMakeupCache("pmakeup-cache.json")
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

