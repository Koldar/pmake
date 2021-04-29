Create a new plugin
===================

This is a tutorial to create a `pmakeup` plugin.

For an example of a plugin, you can view the `archive-pmakeup-plugin`, available `here <https://github.com/Koldar/pmakeup/tree/main/plugins/archive-pmakeup-plugin>`.

Determine the name of the plugin
--------------------------------

`pmakeup` can automatically load plugins only if they are named in either one of the following pattern:

* r"^pmakeup-plugin(s)?-.+";
* r".+-pmakeup-plugin(s)?$";

At the beginning of the run of `pmakeup`, the software will first scan all the installed packages. When it finds a plugin
with the specified name, it will further explores it. So, if you want to develop a plugin is **required to follow that patterns**.

Structure of a `pmakeup` plugin
-------------------------------

Generally speaking, a pmakeup plugin should have the specified structure:

.. code-block:: json

    myfoobar-pmakeup-plugin/ (<-- this is just the plugin root folder)
        myfoobar_pmakeup_plugin/
            __init__.py
            MyFoobarPMakeupPlugin.py
            version.py
        tests/
            test.py
        README.md
        LICENSE.md
        requirements.txt
        setup.py

You can also use ``pmakeup`` to automatically build and deploy your plugin on pypi, but this is another story. The example here
specifies a ``setuptools`` installation way. ``pmakeup`` relies on egg-infos. We first look at the file ``top_level.txt``
in order to fetch the main package name. Then we gain access to such a package and read the ``__init__.py``.
Finally, we scan whatever ``__init__.py`` has loaded. If it finds a class which derives from ``pm.AbstractPMakeupPlugin``
it is autoamtically added in the ``pmakeup`` graph.

.. code-block:: python

        for apackage in map(lambda p: p, pkg_resources.working_set):
            package: "EggInfoDistribution" = apackage

            if not is_package_name_compliant_with_pmakeup_plugin_name(package.project_name):
                continue

            # get top level file
            top_level_file = os.path.join(package.egg_info, "top_level.txt")
            main_package = read_top_level_file(top_level_file)
            module_path = os.path.join(package.location, main_package, "__init__.py")
            module = import_module(module_path, main_package)

            # fetch plugins
            for candidate_classname in dir(module):
                candidate_class = getattr(module_instance, candidate_classname)
                if not inspect.isclass(candidate_class):
                    continue
                if issubclass(candidate_class, pm.AbstractPmakeupPlugin):
                    result.append(candidate_class)

Now let's see what the files should contain.

version.py
----------

This file is easy, it is the version of the package. It should contain one line with a variable set to a semantic version 2 compliant string:

.. code-block:: python

    VERSION = "1.0.4"

__init__.py
-----------

This file is very easy as well. It should import all the ``pmakeup`` plugin classes that you want to export to ``pmakeup``.
For instance, we will export just one plugin:

.. code-block:: python

    from myfoobar_pmakeup_plugin.MyFoobarPMakeupPlugin import MyFoobarPMakeupPlugin


MyFoobarPMakeupPlugin.py
------------------------

This file should contain a class that implements ``pm.AbstractPMakeupPlugin``:

.. code-block:: python

    import pmakeup as pm

    class MyFoobarPMakeupPlugin(pm.AbstractPMakeupPlugin):

        def _setup_plugin(self):
            pass

        def _teardown_plugin(self):
            pass

        def _get_dependencies(self) -> Iterable[type]:
            return []

        @pm.register_command.add("really_important")
        def say_hello(self, name: str) -> bool:
            """
            Say hello to everyone
            """

            self.logs.echo(f"Hello {name}!")
            return True


If you don't need that another plugin ``_setup_plugin`` method is called before this one, you can leave ``_get_dependencies`` to ``[]``.
setup and teardown methods are called whenever the plugin is initialized and finalized.

Any function that you want to call in a ``pmakeup`` script needs to be decorated with ``@pm.register_command.add`` decorator:
the string can be whatever you want, it is used only for grouping the functions together.

If you need to gain access to other plugins, you can use ``self.get_plugin(<plugin_name>)`` to gain access to the corresponding
plugin instance. ``pmakeup`` automatically loads some **really** core plugnis and it provides a property in ``AbstractPMakeupPlugin``:
for example ``self.logs`` is used to print something to the console.

setup.py
--------

Just for completeness, this is the ``setup.py`` that I use to build a plugin:

.. code-block:: python

    import os
    from typing import Iterable

    import setuptools
    from archive_pmakeup_plugin import version

    PACKAGE_NAME = "archive-pmakeup-plugin"
    PACKAGE_VERSION = version.VERSION
    PACKAGE_DESCRIPTION = "A Pmakeup plugin for handling zip and unzip operations"
    PACKAGE_URL = "https://github.com/Koldar/pmakeup.git"
    PACKAGE_PYTHON_COMPLIANCE = ">=3.6"
    PACKAGE_CLASSIFIERS = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
    AUTHOR_NAME = "Massimo Bono"
    AUTHOR_EMAIL = "massimobono1@gmail.com"

    #########################################################
    # INTERNALS
    #########################################################

    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()


    def get_dependencies(domain: str = None) -> Iterable[str]:
        if domain is None:
            filename = "requirements.txt"
        else:
            filename = f"requirements-{domain}.txt"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as fh:
                dep = fh.readline()
                dep_name = dep.split("==")[0]
                yield dep_name + ">=" + dep.split("==")[1]


    setuptools.setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        author=AUTHOR_NAME,
        author_email=AUTHOR_EMAIL,
        description=PACKAGE_DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        license_files="LICEN[SC]E*",
        url=PACKAGE_URL,
        packages=setuptools.find_packages(),
        classifiers=PACKAGE_CLASSIFIERS,
        install_requires=list(get_dependencies()),
        extras_require={
            "test": list(get_dependencies("test")),
            "doc": list(get_dependencies("doc")),
        },
        include_package_data=True,
        package_data={
            "": ["package_data/*.*"],
        },
        python_requires=PACKAGE_PYTHON_COMPLIANCE,
    )
