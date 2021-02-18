import abc
from typing import Any, Iterable


class IPMakeupCache(abc.ABC):

    @abc.abstractmethod
    def reset(self):
        """
        Completely empty the pmake file. After the operation, the cache is present, but it is empty.
        It is required to persistently update the cache in this method
        """
        pass

    @abc.abstractmethod
    def is_empty(self) -> bool:
        """
        Check if there is at least one variable in cache

        :return: true iff there is no variables in cache
        """
        pass

    @abc.abstractmethod
    def variable_names(self) -> Iterable[str]:
        """
        Set of variable names available in the cache.
        They are only at top level
        """
        pass

    @abc.abstractmethod
    def is_cache_present(self) -> bool:
        """
        Check if the pmake cache is present
        """
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """
        human friendly name of the cache
        """
        pass

    @abc.abstractmethod
    def set_variable_in_cache(self, name: str, value: Any, overwrites_is_exists: bool = True):
        """
        Set a variable in the cache.

        :param name: name of the variable to add
        :param value: value to store
        :param overwrites_is_exists: if true, we will overwrite any previous variable in the cache
        """
        pass

    @abc.abstractmethod
    def get_variable_in_cache(self, name: str) -> Any:
        """
        Obtain the variable value from the cache

        :param name: the name of the varaible to obtain
        :return: the variable obtained
        """
        pass

    @abc.abstractmethod
    def has_variable_in_cache(self, name: str) -> bool:
        """
        Check if the variable is present in the cache

        :param name: the name of the variable to check
        :returns: true if the variable is present inthe cache, false otherwise
        """
        pass

    @abc.abstractmethod
    def update_cache(self):
        """
        Store the cache persistently
        """
        pass