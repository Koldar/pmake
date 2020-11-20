#!/bin/bash

# Used while dveloping to isntall the software on the system
sudo pip3 uninstall --yes pmake
source venv/bin/activate
python setup.py bdist sdist bdist_wheel
deactivate
sudo pip3 install dist/pmake-1.0.1-py3-none-any.whl
