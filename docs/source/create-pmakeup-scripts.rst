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

PMakeup makefile-like
---------------------

Albeit ``pmakeup`` is heavily inspired by makefile, its syntax is not very similar to it.
At its base the section of ``pmakeup`` that implements a makefile style is the plugin ``TargetsPMakeupPlugin``.
At high level, we have a directed acyclic graph where each vertex presents a pmakeup target (i.e., a phony makefile target).
Each directed edge represents the fact that in order to execute a target, you first need to execute its successors.
Each vertex has a name, which is the target name, and a python function which takes no input and has no outputs, which
is what pmakeup will execute whenever it is detected that such a function needs to be called.

In order to build the graph, you can code a ``PMakeupfile`` like this:

.. code-block:: python

    core: pm.CorePMakeupPlugin = pmakeup_info.pmakeup_plugins["CorePMakeupPlugin"]
    log: pm.LoggingPMakeupPlugin = pmakeup_info.pmakeup_plugins["LoggingPMakeupPlugin"]
    targets: pm.TargetsPMakeupPlugin = pmakeup_info.pmakeup_plugins["TargetsPMakeupPlugin"]

    core.require_pmakeup_version("2.8.0")

    def sayHello():
        log.print_blue("Hello")

    def sayGoodbye():
        log.print_blue("And goodbye!")

    targets.declare_file_descriptor(f"""
        A string that is used to describe what this script does
    """)
    targets.declare_target(
        target_name="hello",
        description="pmakeup will say hello",
        f=sayHello,
        requires=[],
    )
    targets.declare_target(
        target_name="goodbye",
        description="Say goodbye after saying hello",
        f=sayGoodbye,
        requires=["hello"],
    )

    targets.process_targets()


This ``PMakeupfile`` does nothing and is pretty easy, but basically tells you the fundamentals of ``PMakeupfile`` targets.

You first need to define the functions corresponding to the targets (i.e., ``sayHello`` and ``sayGoodbye``).
Then you can possibly call ``declare_file_descriptor`` to improve the help information of the ``pmakeup`` script.
After that, you need to write several ``declare_target`` function calls, one per graph vertex. The order is not important.
you need to define the string that you need to input in order to call the corresponding function (*target_name*), the function that
``pmakeup`` needs to call whenever the target is requested (*sayHello*), a descrption to automatically build the help information (*description*)
and finally the target dependencies (*requires*). The dependencies are an **ordered list** and there the order matters:
putting a dependency near the head of the list means that the dependency is executeed before the others.

To invoke the help script, you can use ``info``:

.. code-block:: bash

    pmakeup --info

``pmakeup`` will automatically show all the information you need to interact with the script.
TO invoke the script, do the following:

.. code-block:: bash

    pmakeup goodbye

Notice that in this case we will first invoke ``hello`` and only then we execute ``goodbye``: this is due to the fact that
``hello`` is actually a requirements to ``goodbye``.