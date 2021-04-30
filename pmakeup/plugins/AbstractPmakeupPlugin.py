import abc
import logging
import os
from typing import Iterable, Union, Callable, Tuple, Any

import pmakeup as pm
import pmakeup.global_variables


class AbstractPmakeupPlugin(abc.ABC):

    def __init__(self, model: "pm.PMakeupModel"):
        self._model: "pm.PMakeupModel" = model
        self._is_setupped: bool = False
        """
        if true, we have already invoke the setup function; false otherwise 
        """

    # ################################################
    # plugin operations
    # ################################################

    def __str__(self) -> str:
        return self.get_plugin_name()

    @property
    def is_setupped(self) -> bool:
        """
        true if the function setup has already been called, false otherwise
        """
        return self._is_setupped

    def get_plugin_functions(self) -> Iterable[Tuple[str, Callable]]:
        """
        Yield all the functions registered by this plugin
        """
        result = dict()
        for k in dir(self):
            if k.startswith("_"):
                continue
            if k in result:
                raise KeyError(f"duplicate key \"{k}\". It is already mapped to the value {result[k]}")
            logging.debug(f"Adding variable {k}")
            try:
                group, function = pm.register_command.add.plugins["call_dictionary"][k]
                # getattr needs to be called only after checking plugins, becuae in this way we support property,
                # not only functions
                result[k] = getattr(self, k)
            except KeyError:
                pass

        yield from result.items()

    def get_plugin_name(self):
        """
        The name of the plugin. Useful to fetch plugin dynamically
        """
        return self.__class__.__name__.split(".")[-1]

    def get_plugins(self) -> Iterable["pm.AbstractPmakeupPlugin"]:
        """
        get all plugins registered up to this point
        """
        return self._model.get_plugins()

    def has_plugin(self, plugin_type: type) -> bool:
        """
        Check if a plugin has been loaded
        """
        return self._model.is_plugin_registered(plugin_type)

    def get_plugin(self, plugin: Union[str, type]) -> "pm.AbstractPmakeupPlugin":
        """
        Get a plugin of a prticular type

        :param plugin: type of the plugin to find or the plugin name
        :return: instance of the given plugin. Raises an exception if not found
        """
        return self._model.get_plugin(plugin)

    # ################################################
    # autoregistering function
    # ################################################

    @classmethod
    def autoregister(cls):
        """
        Function to call from the __init__ file of the plugin that allows the module to automatically be registered.
        If you put it in the __init_ file, as soon as the plugin is imported in your pmakeup script, the plugin will immediately be loaded.
        If you don't put it in the __init__ file, the developer writing the pmakeup script will have to do it herself by explicitly calling
        require_pmakeup_plugins
        """
        pmakeup.global_variables.PMAKEUP_PLUGINS_TO_REGISTER.append(cls)

    # ################################################
    # operating system platform access
    # ################################################

    @property
    def platform(self) -> "pm.IOSSystem":
        """
        fetch the plugin repersenting the operating system on this machine
        """
        return self._model._platform

    # ################################################
    # variable management
    # ################################################

    def get_variable_or_set_it(self, name: str, otherwise: Any) -> Any:
        """
        Ensure the user has passed a variable.
        If not,  the default variable is stored in the variable sety

        :param name: the variable name to check
        :param otherwise: the value the varible with name will have if the such a variable is not present

        """
        if name not in self.get_registry().variables:
            self.get_registry().variables[name] = otherwise
        return self.get_registry().variables[name]

    def get_shared_variables(self) -> "pm.AttrDict":
        return self.get_registry().variables

    def get_registry(self) -> "pm.PMakeupRegistry":
        """
        get the pmakeup registry, where all shared entities available for plugins are located
        """
        return self._model._eval_globals

    def get_variable(self, name: str) -> Any:
        """
        Ensure the user has passed a variable.
        If not, raises an exception

        :param name: the variable name to check
        :raises PMakeupException: if the variable is not found
        """
        if name not in self.get_shared_variables():
            raise pm.PMakeupException(f"Variable {name} not found")
        return self.get_shared_variables()[name]

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set the variable in the current model. If the variable did not exist, we create one one.
        Otherwise, the value is overridden

        :param name: name of the variable to programmatically set
        :param value: value to set
        """
        self.get_shared_variables()[name] = value

    # ################################################
    # operations avaialble to all plugins: CWD
    # ################################################

    def get_cwd(self) -> pm.path:
        """

        :return: the CWD the current commands operates in, as absolute payj
        """
        return os.path.abspath(self.get_shared_variables()["cwd"])

    def set_cwd(self, value):
        """
        set the CWD the current commands operates in
        :param value: new value of the CWD
        """
        self._model._eval_globals.cwd = value

    def _abs_wrt_cwd(self, *paths) -> pm.path:
        """
        generate a path relative to cwd and generate the absolute path of it

        :param paths: the single elements of a path to join and whose absolute path we need to compute
        :return: absolute path, relative to the current working directory
        """
        return os.path.abspath(os.path.join(self.get_cwd(), *paths))

    def _truncate_string(self, string: str, width: int, ndots: int = 3) -> str:
        """
        If a string is too long, we truncate it with "..."
        """
        if len(string) > (width - ndots):
            return string[:(width-ndots)] + "."*ndots
        else:
            return string

    # ###################################################
    # Access to popular plugins, since it is always imported
    # ###################################################

    @property
    def core(self) -> "pm.CorePMakeupPlugin":
        """
        Gain access to the core plugin, which is well populated
        """
        return self.get_plugin("CorePMakeupPlugin")

    @property
    def paths(self) -> "pm.PathsPMakeupPlugin":
        """
        Gain access to the core plugin, which is well populated
        """
        return self.get_plugin("PathsPMakeupPlugin")

    @property
    def files(self) -> "pm.FilesPMakeupPlugin":
        """
        Gain access to the core plugin, which is well populated
        """
        return self.get_plugin("FilesPMakeupPlugin")

    @property
    def logs(self) -> "pm.LoggingPMakeupPlugin":
        """
        Gain access to the core plugin, which is well populated
        """
        return self.get_plugin("LoggingPMakeupPlugin")

    @property
    def operating_system(self) -> "pm.OperatingSystemPMakeupPlugin":
        """
        Gain access to the operating system plugin, which is well populated
        """
        return self.get_plugin("OperatingSystemPMakeupPlugin")

    # ###################################################
    # Logging
    # ###################################################

    def _log_command(self, message: str):
        """
        reserved. Useful to log the action performed by the user

        :param message: message to log
        """
        if not self.get_variable_or_set_it("_disable_log_command", False):
            logging.info(message)

    # ################################################
    # abstract methods
    # ################################################

    @abc.abstractmethod
    def _setup_plugin(self):
        """
        Set of operation to perform to initialize the plugin.
        You should use this method rather than overriding __init__ function
        """
        pass

    @abc.abstractmethod
    def _teardown_plugin(self):
        """
        Set of operation to perform to tear down the plugin.
        """
        pass

    @abc.abstractmethod
    def _get_dependencies(self) -> Iterable[type]:
        """
        The dependencies this plugin requires to be setup before using it.
        Return empty list if you don't want to alter the order this plugin is setup
        """
        pass
