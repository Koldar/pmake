import os
from typing import Iterable

from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin
from pmakeup.commons_types import path
from pmakeup.decorators import show_on_help


class PathsPMakeupPlugin(AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        pass

    @show_on_help.add_command('paths')
    def path(self, *p: str) -> path:
        """
        Generate a path compliant wit the underlying operating system path scheme.

        If the path is relative, we will **not** join it with cwd

        :param p: the path to build
        """

        return os.path.join(*p)

    @show_on_help.add_command('paths')
    def abs_path(self, *p: path) -> path:
        """
        Generate a path compliant with the underlying operating system path scheme.

        If the path is relative, it is relative to the cwd

        :param p: the path to build
        """
        actual_path = os.path.join(*p)
        if os.path.isabs(actual_path):
            return os.path.abspath(actual_path)
        else:
            return os.path.abspath(os.path.join(self.cwd, actual_path))

PathsPMakeupPlugin.autoregister()