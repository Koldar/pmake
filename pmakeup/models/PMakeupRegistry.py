import json
from collections import UserDict

from pmakeup.models.AttrDict import AttrDict


class PMakeupRegistry(dict):
    """
    The shared context that will be used when computing "eval" or "exec" function, as a global variables.

    At the root there are all the functions that the developers may use.

    This object holds all the data that is shared among all the pmakeup plugin
    """

    def __init__(self):
        super(PMakeupRegistry, self).__init__()

        self["pmakeup_info"] = AttrDict({})
        self["variables"] = AttrDict({})
        self["commands"] = AttrDict({})

        self.pmakeup_info["pmakeup_cli_variables"] = AttrDict({})
        self.pmakeup_info["pmakeup_plugins"] = AttrDict({})
        self.pmakeup_info["pmakeup_model"] = AttrDict({})
        self.pmakeup_info["pmakeup_requested_target_names"] = AttrDict({})
        self.pmakeup_info["pmakeup_interesting_paths"] = AttrDict({})
        self.pmakeup_info["pmakeup_latest_interesting_paths"] = AttrDict({})

    def __getitem__(self, item):
        return super().__getitem__(item)

    def can_a_function_have_a_name(self, func_name: str) -> bool:
        return func_name not in [
            "pmakeup_cli_variables",
            "pmakeup_plugins",
            "pmakeup_model",
            "pmakeup_info",
            "pmakeup_requested_target_names",
            "pmakeup_interesting_paths",
            "pmakeup_latest_interesting_paths",
            "variables",
            "commands",
        ]

    def dump_registry(self) -> str:
        """
        Fetch a JSON representaiton on the WHJOLE registry
        """
        return json.dumps(self, indent=2)

    @property
    def cwd(self) -> AttrDict:
        """
        Gain access to the CWD variable
        """
        return self.variables.cwd

    @cwd.setter
    def cwd(self, v):
        self.variables.cwd = v

    @property
    def commands(self) -> AttrDict:
        """
        Gain access to the dictionary contianing all the registered functions
        """
        return self["commands"]

    @commands.setter
    def commands(self, v):
        """
        Set commands
        """
        self["commands"] = v

    @property
    def variables(self) -> AttrDict:
        """
        Gain access to the object containing all the variables accessible by any plugin
        """
        return self["variables"]

    @variables.setter
    def variables(self, v):
        self["variables"] = v

    @property
    def pmakeup_latest_interesting_paths(self) -> AttrDict:
        """
        Gain access to the target that the user wanted to process
        """
        return self.pmakeup_info["pmakeup_latest_interesting_paths"]

    @pmakeup_latest_interesting_paths.setter
    def pmakeup_latest_interesting_paths(self, v):
        self.pmakeup_info["pmakeup_latest_interesting_paths"] = v

    @property
    def pmakeup_interesting_paths(self) -> AttrDict:
        """
        Gain access to the target that the user wanted to process
        """
        return self.pmakeup_info["pmakeup_interesting_paths"]

    @pmakeup_interesting_paths.setter
    def pmakeup_interesting_paths(self, v):
        self.pmakeup_info["pmakeup_interesting_paths"] = v

    @property
    def pmakeup_requested_target_names(self) -> AttrDict:
        """
        Gain access to the target that the user wanted to process
        """
        return self.pmakeup_info["pmakeup_requested_target_names"]

    @pmakeup_requested_target_names.setter
    def pmakeup_requested_target_names(self, v):
        self.pmakeup_info["pmakeup_requested_target_names"] = v

    @property
    def pmakeup_info(self) -> AttrDict:
        """
        Gain access to the variables
        """
        return self["pmakeup_info"]

    @pmakeup_info.setter
    def pmakeup_info(self, v):
        self["pmakeup_info"] = v

    @property
    def pmakeup_cli_variables(self) -> AttrDict:
        """
        Gain access to the variables
        """
        print(f"pmakeup_cli_variables is {self.pmakeup_info['pmakeup_cli_variables']}")
        return self.pmakeup_info["pmakeup_cli_variables"]

    @pmakeup_cli_variables.setter
    def pmakeup_cli_variables(self, v):
        self.pmakeup_info["pmakeup_cli_variables"] = v

    @property
    def pmakeup_plugins(self) -> AttrDict:
        """
        Gain access to the set of plugins registered by the pmakeup
        """
        return self.pmakeup_info["pmakeup_plugins"]

    @pmakeup_plugins.setter
    def pmakeup_plugins(self, v):
        self.pmakeup_info["pmakeup_plugins"] = v

    @property
    def pmakeup_model(self) -> AttrDict:
        """
        Gain access to the variables
        """
        return self.pmakeup_info["pmakeup_model"]

    @pmakeup_model.setter
    def pmakeup_model(self, v):
        self.pmakeup_info["pmakeup_model"] = v


