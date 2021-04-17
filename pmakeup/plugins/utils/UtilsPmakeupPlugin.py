from typing import Any, Iterable

from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin
from pmakeup.decorators import show_on_help


class UtilsPmakeupPlugin(AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        pass

    @show_on_help.add_command('utils')
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


UtilsPmakeupPlugin.autoregister()
