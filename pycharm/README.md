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
