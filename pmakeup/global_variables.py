from typing import List

PMAKEUP_MODEL = None
"""
The model used by the running pmakeup program. Accessible anywhere
"""
PMAKEUP_PLUGINS_TO_REGISTER: List[type] = []
"""
Plugins that needs to be registered by pmakeup before starting a script. Each cell repersent sa plugin classs to instantiate 
"""