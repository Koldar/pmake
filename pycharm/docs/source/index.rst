.. pmake documentation master file, created by
   sphinx-quickstart on Wed Nov 18 18:50:51 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pmake's documentation!
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

The following are the importan commands that you can immediately use within pmake script

.. automodule:: pmake
   :members:

.. autoclass:: commands.SessionScript
   :members:

PMake cache
======================

.. autoclass:: IPMakeCache.IPMakeCache
   :members:

.. autoclass:: JsonPMakeCache.JsonPMakeCache
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

.. autoclass:: PMakeModel.PMakeModel
   :members:

