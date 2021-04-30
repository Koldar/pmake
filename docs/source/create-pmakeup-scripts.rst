Create PMakeup Scripts
======================

One of the main uses of ``pmakeup`` is to basically execute a python script, usually called ``PMakeupfile.py`` using an automatically generated *context*:
this context, called **pmakeup registry** allows you to use some useful python functions and variables in your python script, without
having to write anything. You don't need to import anything in your script.

If you need a function that is not available in the ``pmakeup`` project, you can either use or write a ``pmakeup`` plugin.
If another developer has written a ``pmakeup`` plugin, you can just use the plugin by simply installing the package in
your ``pip`` environment (``venv`` are supported as well).

You can find some example of usage of ``pmakeup`` plugin in the ``example/`` folder  (see `here https://github.com/Koldar/pmakeup/tree/main/examples>`)

Integrate pycharm in PMakeupfile
--------------------------------

This step is completely optional. If you use an IDE, like Pycharm, you might want to use a content assist to help you
writing the script.

To do so, import pmakeup file and then get the plugin instances you want to use. For instance:

.. code-block:: python

    import pmakeup as pm

    core: pm.CorePMakeupPlugin = pmakeup_info.pmakeup_plugins["CorePMakeupPlugin"]
    files: pm.FilesPMakeupPlugin = pmakeup_info.pmakeup_plugins["FilesPMakeupPlugin"]
    log: pm.LoggingPMakeupPlugin = pmakeup_info.pmakeup_plugins["LoggingPMakeupPlugin"]
    operating_system: pm.OperatingSystemPMakeupPlugin = pmakeup_info.pmakeup_plugins["OperatingSystemPMakeupPlugin"]
    paths: pm.PathsPMakeupPlugin = pmakeup_info.pmakeup_plugins["PathsPMakeupPlugin"]
    targets: pm.TargetsPMakeupPlugin = pmakeup_info.pmakeup_plugins["TargetsPMakeupPlugin"]

The strings in the dictionary ``pmakeup_plugins`` is called **plugin name** and is customizable in the plugin class definition by overriding the method ``get_plugin_name(self)``
After this, you can write, for instance, ``paths.`` and the content assist should show all the available commands.

Simple PMakeup script
---------------------

Usually the first thing you should write in your ``PMakeupfile.py`` is the `require_pmakeup_version`: in this way pmakeup
can check if the currently installed version of pmakeup supports your script.

.. code-block:: python

    require_pmakeup_version("2.5.24")

After that, you can write basically anything you want by exploiting python.