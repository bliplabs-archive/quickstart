#!/bin/sh

set -e
set -x

black main.py # autoformats main.py
isort main.py # sorts imports in main.py
flake8 main.py # linting
pylint main.py # more linting

# mypy provides type checking and more in-depth code analysis, may ask to
# install packages that provide type annotations
MYPYPATH=.venv mypy \
    --install-types \
    --python-executable \
    .venv/bin/python3 main.py
