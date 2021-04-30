
# Call this script in 02-use-cli-variables as follows:
# pmakeup --variable "name" "Mario"

# ###################### START CONTENT ASSIST ############################

import pmakeup as pm

core: pm.CorePMakeupPlugin = pmakeup_info.pmakeup_plugins["CorePMakeupPlugin"]
files: pm.FilesPMakeupPlugin = pmakeup_info.pmakeup_plugins["FilesPMakeupPlugin"]
log: pm.LoggingPMakeupPlugin = pmakeup_info.pmakeup_plugins["LoggingPMakeupPlugin"]
operating_system: pm.OperatingSystemPMakeupPlugin = pmakeup_info.pmakeup_plugins["OperatingSystemPMakeupPlugin"]
paths: pm.PathsPMakeupPlugin = pmakeup_info.pmakeup_plugins["PathsPMakeupPlugin"]
targets: pm.TargetsPMakeupPlugin = pmakeup_info.pmakeup_plugins["TargetsPMakeupPlugin"]

# ###################### END CONTENT ASSIST ############################

core.require_pmakeup_version("2.7.0")

log.echo_variables()

core.ensure_has_cli_variable("name")

# pmakeup should print "Hello Mario!"
log.echo(f"Hello {variables.name}!")
# OR
log.echo(f"Hello {vars().name}!")
