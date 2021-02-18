.. pmakeup documentation master file, created by
   sphinx-quickstart on Wed Nov 18 18:50:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pmakeup's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Important commands
==================

The following are the importan commands that you can immediately use within pmakeup script

.. automodule:: pmakeup
   :members:

.. autoclass:: commands.SessionScript
   :members:

PMakeup cache
======================

.. autoclass:: IPMakeupCache.IPMakeupCache
   :members:

.. autoclass:: JsonPMakeupCache.JsonPMakeupCache
   :members:

Platform interface
==================

.. autoclass:: IOSSystem.IOSSystem
   :members:

.. autoclass:: LinuxOSSystem.LinuxOSSystem
   :members:

.. autoclass:: WindowsOSSystem.WindowsOSSystem
   :members:

Additional commands platform dependent
======================================

.. autoclass:: linux_commands.LinuxSessionScript
   :members:

.. autoclass:: windows_commands.WindowsSessionScript
   :members:

Other classes
=============

.. autoclass:: InterestingPath.InterestingPath
   :members:

.. autoclass:: PMakeupModel.PMakeupModel
   :members:

