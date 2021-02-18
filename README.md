# Introduction

This package tries to provide a solution for build softwares in a platform independent manner.
It tries to loosely mimick the objective of Makefile, but with a python syntax.
Makefiles are known to have complex syntax a several pitfalls. They are also clunky to work with,
Pmakeup tries to provide a pythonic environment (which is much easier to work with).
To help the devloper in commons tasks, Pmakeup provides several built-in commands
to perform common tasks (like copying files, read content and execute system commands).

# An important Security disclaimer

I want to empathize this: `pamkeup` is **not a build system you can use to puppeteer remove systems**: 
its use is intended to build software locally, or to setup your workstation. In no means `pmakeup` project
provides adequate level of security to support remote puppeteering. In order to avoid being in you way, you can
actually call script by injecting you password as plain text. This is by design, since on **your** worksation, it is
assumed you have full control (as a developer anyway). However, transmitting password in plain text is a **huge**
security hole. Hence this project shoudl not be used for that objective.

# For the user

You can install the software via:

```
pip install pmakeup
```

Admin privileges may be required. To show all the options you can exploit, use

```
pmakeup --help
```

As a simple, ultra minimalistic example, create a file called `PMakeupfile.py` and past the following:

```
echo("Hello world!", foreground="blue")
```

The `PMakeupfile` is actually just a python script, so you can do anything in it!
This is by design, since in several build systems (`make`, `cmake`, `jenkins`) a lot of time you are
constrained by the declarative syntax or by the huge pitfalls the build system provides.
`pmakeup` tries not to be in your way: it gives you freedom.

You can use targets, pretty much as in the Makefile, albeit the syntax is quite different:

```
def clean():
    echo(f"Cleaning!!!!", foreground="blue")


def build():
    echo(f"Build!", foreground="blue")


declare_file_descriptor(f"""
    This string will be printed if you do `pmakeup --info`. Use this
    to give to the enduser information about how to use this makefile! :) 
""")
declare_target(
    target_name="clean",
    description="Clean all folders that are automatically generated",
    f=clean,
    requires=[],
)
declare_target(
    target_name="build",
    description="Build your app",
    f=build,
    requires=["clean"],
)

# necessary
process_targets()
```

Then, call in the same directory:

```
pmakeup build
```

The application will first invoke `clean` and then `build` functions.

# For the developer

This section is useful for the contributors.

## Installing with setuptools

You can build the pacakge via:

```
sudo pip install pyinstaller wheel setupttols sphinx
git clone https://github.com/Koldar/pmakeup
cd pmakeup
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py bdist_wheel
deactivate
```

To installing on a system (ensure you are not in `venv`!):

```
source venv/bin/activate
python setup.py bdist_wheel
deactivate
# get latest wheel file in dist\
pip install dist\*.whl

```

Note that after installation, `pmakeup.exe` (or `pmakeup`) will be automatically installed in `%PYTHONPATH%/Scripts` (or available in the `PATH`)

to show a comprehensive help, with all the commands available to you.

# Using pmakeup to build pmakeup

Assuming you have a version of pmakeup installed on your system, you can use `pmakeup` to build `pmakeup`.

```
pmakeup --variable "NEW_VERSION" "1.2.1" update-version build install upload-to-pypi
```

You will need to create `TWINE_PYPI_PASSWORD` containig your twine password to upload 

# Documentation

I have installed `miktex` as latex

```
pip install sphinx
cd docs/
sphinx-quickstart
make html latexpdf
```

For latex, the packages needs to be installed (may be superset):

```
anyfontsize, auxhook, beamer, bigintcalc, bitset, capt-of, changepage, 
cmap, courier, datatool, dvips, etexcmds, fancyhdr, fancyvrb, fncychap, 
fontawesome, fontspec, fp, framed, geometry, gettitlestring, glossaries, 
hycolor, hyperref, intcalc, jknappen, koma-script, kvoptions, 
latexmk, letltxmacro, listings, lm, luatex85, mdframed, mfirstuc, 
miktex-lualatex, moresize, needspace, oberdiek, parskip, pdfescape, 
psnfss, refcount, rerunfilecheck, rsfs, sansmathaccent, substr, 
supetabular, tabulary, tex-ini-files, textcase, titlesec, tocbibind, 
translator, uniquecounter, upquote, url, wrapfig, xfor, xkeyval, 
zapfding, zref
```

 
