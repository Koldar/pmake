import abc
import logging
import os
from typing import Iterable, Union, Callable, Tuple, Any

from pmakeup.commons_types import path
from pmakeup.decorators import show_on_help
from pmakeup.exceptions.PMakeupException import PMakeupException


class AbstractPmakeupPlugin(abc.ABC):

    def __init__(self, model: "PMakeupModel.PMakeupModel"):
        self._model = model
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
            result[k] = getattr(self, k)
        yield from result.items()

    def get_plugin_name(self):
        """
        The name of the plugin. Useful to fetch plugin dynamically
        """
        return self.__class__.__name__.split(".")[-1]

    def get_plugins(self) -> Iterable["AbstractPmakeupPlugin"]:
        """
        get all plugins registered up to this point
        """
        return self._model.get_plugins()

    def has_plugin(self, plugin_type: type) -> bool:
        """
        Check if a plugin has been loaded
        """
        return self._model.is_plugin_registered(plugin_type)

    def get_plugin(self, plugin_type: Union[str, type]) -> "AbstractPmakeupPlugin":
        """
        Get a plugin of a prticular type

        :param plugin_type: type of the plugin to find
        :return: instance of the given plugin. Raises an exception if not found
        """
        return self._model.get_plugin(plugin_type)

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
        global PMAKEUP_MODEL
        PMAKEUP_MODEL.register_plugins(cls(PMAKEUP_MODEL))

    # ################################################
    # operating system platform access
    # ################################################

    def platform(self) -> "AbstractOperatingSystemPlugin":
        """
        fetch the plugin repersenting the operating system on this machine
        """
        if os.name == "nt":
            return self.get_plugin("WindowsOSSystem")
        elif os.name == "posix":
            return self.get_plugin("LinuxOSSystem")
        else:
            raise PMakeupException(f"Cannot identify platform!")

    # ################################################
    # variable management
    # ################################################

    @show_on_help.add_command('core')
    def get_variable_or_set_it(self, name: str, otherwise: Any) -> Any:
        """
        Ensure the user has passed a variable.
        If not,  the default variable is stored in the variable sety

        :param name: the variable name to check
        :param otherwise: the value the varible with name will have if the such a variable is not present

        """
        if name not in self._model.variable:
            self._model.variable[name] = otherwise
        return self._model.variable[name]

    @show_on_help.add_command('core')
    def get_variable(self, name: str) -> Any:
        """
        Ensure the user has passed a variable.
        If not, raises an exception

        :param name: the variable name to check
        :param otherwise: the value the varible with name will have if the such a variable is not present
        :raises PMakeupException: if the variable is not found
        """
        if name not in self._model.variable:
            raise PMakeupException(f"Variable {name} not found")
        return self._model.variable[name]

    @show_on_help.add_command('core')
    def set_variable(self, name: str, value: Any) -> None:
        """
        Set the variable in the current model. If the variable did not exist, we create one one.
        Otherwise, the value is overridden

        :param name: name of the variable to programmatically set
        :param value: value to set
        """
        self._model.variable[name] = value

    # ################################################
    # operations avaialble to all plugins: CWD
    # ################################################

    @show_on_help.add_command('paths')
    @property
    def cwd(self) -> path:
        """

        :return: the CWD the current commands operates in
        """
        return os.path.abspath(self.get_variable("cwd"))

    @show_on_help.add_command('paths')
    @cwd.setter
    def cwd(self, value) -> path:
        """

        :return: the CWD the current commands operates in
        """
        self.set_variable("cwd", value)

    @show_on_help.add_command('paths')
    def abs_wrt_cwd(self, *paths) -> path:
        """
        generate a path relative to cwd and generate the absolute path of it

        :param paths: the single elements of a path to join and whose absolute path we need to compute
        :return: absolute path, relative to the current working directory
        """
        return os.path.abspath(os.path.join(self._cwd, *paths))

    # ################################################
    # operations available to all plugins: CWD
    # ################################################

    def _log_command(self, message: str):
        """
        reserved. Useful to log the action performed by the user

        :param message: message to log
        """
        self.get_variable("disable_log_command")
        if not self._disable_log_command:
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
