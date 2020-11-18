#!/bin/bash

# Used while dveloping to isntall the software on the system
sudo pip3 uninstall --yes pmake
python3 setup.py bdist sdist bdist_wheel
sudo pip3 install dist/pmake-1.0.0-py3-none-any.whl
