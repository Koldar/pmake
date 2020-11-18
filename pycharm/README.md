# Introduction

The package allows you to quickly script batch commands that are platform independent.
You can write python files containing useful functions. 

# Installing with setuptools

You can build the pacakge via:

```
python setup.py bdist sdist bdist_wheel
```

To installing on a system (ensure you are not in `venv`!):

```
pip install dist\*.whl
```

Note that after installation, `pmake.exe` will be automatically installed in `%PYTHONPATH%/Scripts`

# Help

You can use

```
.\pmake.exe --help
```

to show a comprehensive help

# Pyinstaller (optional)

You can build an executable via

```
pyinstaller --hidden-import "colorama" --noconfirm --onefile --name "pmake" --icon "images\icon.ico" "pmake\pmake.py"
```

# Documentation

```
pip install sphinx
cd docs/
sphinx-quickstart
make html latexpdf
```

For latex, the packages needs to be installed (may be superset):

 * `anyfontsize`;
 * `auxhook`;
 * `beamer`;
 * `bigintcalc`;
 * `bitset`;
 * `capt-of`;
 * `changepage`;
 * `cmap`;
 * `courier`;
 * `datatool`;
 * `dvips`;
 * `etexcmds`;
 * `fancyhdr`;
 * `fancyvrb`;
 * `fncychap`;
 * `fontawesome`;
 * `fontspec`;
 * `fp`;
 * `framed`;
 * `geometry`;
 * `gettitlestring`;
 * `glossaries`;
 * `hycolor`;
 * `hyperref`;
 * `intcalc`;
 * `jknappen`;
 * `koma-script`;
 * `kvoptions`;
 * `latexmk`;
 * `letltxmacro`;
 * `listings`;
 * `lm`;
 * `luatex85`;
 * `mdframed`;
 * `mfirstuc`;
 * `miktex-lualatex`;
 * `moresize`;
 * `needspace`;
 * `oberdiek`;
 * `parskip`;
 * `pdfescape`;
 * `psnfss`;
 * `refcount`;
 * `rerunfilecheck`;
 * `rsfs`;
 * `sansmathaccent`;
 * `substr`;
 * `supetabular`;
 * `tabulary`;
 * `tex-ini-files`;
 * `textcase`;
 * `titlesec`;
 * `tocbibind`;
 * `translator`;
 * `uniquecounter`;
 * `upquote`;
 * `url`;
 * `wrapfig`;
 * `xfor`;
 * `xkeyval`;
 * `zapfding`;
 * `zref`;
 
