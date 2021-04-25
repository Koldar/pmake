from typing import Iterable

import pmakeup as pm


class LinuxPMakeupPlugin(pm.AbstractPmakeupPlugin):
    """
    Plugin that specifically offer methods typical of linux
    """

    def __init__(self, model: "pm.PMakeupModel"):
        self._model = model

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("linux")
    def test_linux(self, string: str):
        """
        Test if linux commands is loaded
        :param string: the string to echo'ed
        """
        self._model.get_plugin_by_name("CoreMakeupPlugin").echo(string)

