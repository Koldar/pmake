# ######################################################
# type alias
# ######################################################
from pmakeup.models.commons_types import path

# ############################################
# decorators
# ############################################
from pmakeup.decorators import show_on_help
from pmakeup.decorators import register_command

# ############################################
# module loading
# ############################################
from pmakeup import version

# ############################################
# fix order class
# ############################################

# utils (low priority)
from pmakeup.models.AttrDict import AttrDict
from pmakeup.plugins.git.CommitEntry import CommitEntry
from pmakeup.TargetDescriptor import TargetDescriptor
from pmakeup.platforms.InterestingPath import InterestingPath

# main core (order here is REALLY sensitive!)

from pmakeup.plugins.AbstractPmakeupPlugin import AbstractPmakeupPlugin

import pmakeup.plugins.core.CorePMakeupPlugin
from pmakeup.plugins.core.CorePMakeupPlugin import CorePMakeupPlugin

import pmakeup.plugins.paths.PathsPMakeupPlugin
from pmakeup.plugins.paths.PathsPMakeupPlugin import PathsPMakeupPlugin

import pmakeup.plugins.files.FilesPMakeupPlugin
from pmakeup.plugins.files.FilesPMakeupPlugin import FilesPMakeupPlugin

import pmakeup.plugins.log.LoggingPMakeupPlugin
from pmakeup.plugins.log.LoggingPMakeupPlugin import LoggingPMakeupPlugin

import pmakeup.plugins.web.WebPMakeupPlugin
from pmakeup.plugins.web.WebPMakeupPlugin import WebPMakeupPlugin

import pmakeup.plugins.operating_system.OperatingSystemPMakeupPlugin
from pmakeup.plugins.operating_system.OperatingSystemPMakeupPlugin import OperatingSystemPMakeupPlugin

import pmakeup.plugins.targets.TargetsPMakeupPlugin
from pmakeup.plugins.targets.TargetsPMakeupPlugin import TargetsPMakeupPlugin

import pmakeup.plugins.strings.StringsPMakeupPlugin
from pmakeup.plugins.strings.StringsPMakeupPlugin import StringsPMakeupPlugin

import pmakeup.plugins.git.GitPMakeupPlugin
from pmakeup.plugins.git.GitPMakeupPlugin import GitPMakeupPlugin

import pmakeup.plugins.tempfiles.TempFilesPMakeupPlugin
from pmakeup.plugins.tempfiles.TempFilesPMakeupPlugin import TempFilesPMakeupPlugin

import pmakeup.plugins.utils.UtilsPmakeupPlugin
from pmakeup.plugins.utils.UtilsPmakeupPlugin import UtilsPmakeupPlugin

import pmakeup.plugins.windows.WindowsPMakeupPlugin
from pmakeup.plugins.windows.WindowsPMakeupPlugin import WindowsPMakeupPlugin

import pmakeup.plugins.linux.LinuxPMakeupPlugin
from pmakeup.plugins.linux.LinuxPMakeupPlugin import LinuxPMakeupPlugin


from pmakeup.platforms.IOSSystem import IOSSystem

import pmakeup.models.PMakeupRegistry
import pmakeup.platforms.WindowsOSSystem

from pmakeup.models.PMakeupModel import PMakeupModel


# import pmakeup.platforms.LinuxOSSystem


# # exceptions
from pmakeup.exceptions.PMakeupException import PMakeupException
from pmakeup.exceptions.AssertionPMakeupException import AssertionPMakeupException
from pmakeup.exceptions.InvalidScenarioPMakeupException import InvalidScenarioPMakeupException

from pmakeup.models.PMakeupRegistry import PMakeupRegistry
from pmakeup.platforms.WindowsOSSystem import WindowsOSSystem
from pmakeup.platforms.LinuxOSSystem import LinuxOSSystem

# from pmakeup.plugins.windows import WindowsPMakeupPlugin
# from pmakeup.plugins.windows.WindowsPMakeupPlugin import WindowsPMakeupPlugin
#
# from pmakeup.plugins.linux import LinuxPMakeupPlugin
# from pmakeup.plugins.linux.LinuxPMakeupPlugin import LinuxPMakeupPlugin

# cache
import pmakeup.cache.IPMakeupCache
from pmakeup.cache.IPMakeupCache import IPMakeupCache

import pmakeup.cache.JsonPMakeupCache
from pmakeup.cache.JsonPMakeupCache import JsonPMakeupCache

#
# # standard plugins
# import pmakeup.StandardPMakeupPlugin
# import pmakeup.LinuxSessionScript
# import pmakeup.WindowsSessionScript
#
#
#
#
# # ######################################################
# # now import classes (order here is irrelevant)
# # ######################################################
#
#from pmakeup.models.AttrDict import AttrDict

# from pmakeup.platforms.InterestingPath import InterestingPath

#from pmakeup.plugins import AbstractPmakeupPlugin
#from pmakeup.models.PMakeupModel import PMakeupModel


# from pmakeup.platforms.InterestingPath import InterestingPath
# from pmakeup.models.PMakeupModel import PMakeupModel
# from pmakeup.TargetDescriptor import TargetDescriptor
# from pmakeup.exceptions.PMakeupException import PMakeupException
# from pmakeup.exceptions.AssertionPMakeupException import AssertionPMakeupException
# from pmakeup.plugins.git.CommitEntry import CommitEntry
# from pmakeup.cache.IPMakeupCache import IPMakeupCache
# from pmakeup.cache.JsonPMakeupCache import JsonPMakeupCache
# from pmakeup.StandardPMakeupPlugin import StandardPMakeupPlugin
# from pmakeup.LinuxSessionScript import LinuxSessionScript
# from pmakeup.WindowsSessionScript import WindowsSessionScript
from pmakeup.models.PMakeupRegistry import PMakeupRegistry

