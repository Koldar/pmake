#!/bin/bash

source venv/bin/activate
python setup.py bdist sdist bdist_wheel
deactivate
twine upload --repository testpypi dist/*
