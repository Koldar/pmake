# Introduction

This package tries to provide a solution for build softwares in a platform independent manner.
It tries to loosely mimick the objective of Makefile, but with a python syntax.
Makefiles are known to have complex syntax a several pitfalls. They are also clunky to work with,
Pmake tries to provide a pythonic environment (which is much easier to work with).
To help the devloper in commons tasks, Pmake provides several built-in commands
to perform common tasks (like copying files, read content and execute system commands).

# For the user

You can install the software via:

```
pip install pmake
```

Admin privileges may be required. To show all the options you can exploit, use

```
pmake --help
```

As a simple, minimalistic example, create a file caleld `PMakefile.py` and past the following:

```
echo("Hello world!", foreground="blue")
```

Then, call in the same directory:

```
pmake
```

The file you have just created will be executed.

# For the developer

This section is useful for the contributors.

## Installing with setuptools

You can build the pacakge via:

```
git clone https://github.com/Koldar/pmake
cd pmake
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py bdist sdist bdist_wheel
deactivate
```

To installing on a system (ensure you are not in `venv`!):

```
pip install dist\*.whl
```

Note that after installation, `pmake.exe` (or `pmake`) will be automatically installed in `%PYTHONPATH%/Scripts` (or available in the `PATH`)

to show a comprehensive help, with all the commands available to you.

# Pyinstaller (optional)

You can build an executable via

```
pyinstaller --hidden-import "colorama" --noconfirm --onefile --name "pmake" --icon "images\icon.ico" "pmake\pmake.py"
```

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

 
