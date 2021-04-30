# Ensure that in you pip it is installed the package "archive-pmakeup-plugin", as shown:
# pip install archive-pmakeup-plugin

# ###################### START CONTENT ASSIST ############################

import pmakeup as pm
from archive_pmakeup_plugin import ArchivePMakeupPlugin

core: pm.CorePMakeupPlugin = pmakeup_info.pmakeup_plugins["CorePMakeupPlugin"]
files: pm.FilesPMakeupPlugin = pmakeup_info.pmakeup_plugins["FilesPMakeupPlugin"]
log: pm.LoggingPMakeupPlugin = pmakeup_info.pmakeup_plugins["LoggingPMakeupPlugin"]
operating_system: pm.OperatingSystemPMakeupPlugin = pmakeup_info.pmakeup_plugins["OperatingSystemPMakeupPlugin"]
paths: pm.PathsPMakeupPlugin = pmakeup_info.pmakeup_plugins["PathsPMakeupPlugin"]
targets: pm.TargetsPMakeupPlugin = pmakeup_info.pmakeup_plugins["TargetsPMakeupPlugin"]

# third party plugin (use only for IDE content assist, not needed). This requires that is installed in your pip
archive: ArchivePMakeupPlugin = pmakeup_info.pmakeup_plugins["ArchivePMakeupPlugin"]

# ###################### END CONTENT ASSIST ############################

core.require_pmakeup_version("2.7.0")

archive.zip_files(files=["file_to_compress.txt"], zip_name="compressed.zip", zip_format="zip")
log.print_blue("DONE!")