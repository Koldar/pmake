from collections import UserDict

from pmakeup.PMakeupModel import AttrDict


class PMakeupRegistry(UserDict):
    """
    The shared context that will be used when computing "eval" or "exec" function, as a global variables
    """

    def __init__(self):
        super()

        self["variables"] = AttrDict()

    @property
    def variables(self):
        return self["variables"]

