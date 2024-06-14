#!/bin/sh
set -e

if [ -f "requirements.txt" ]; then
  echo "installing via requirements.txt"
  # if using requirements.txt, might be recommended to use ssh installation
  python3 -m pip install -r requirements.txt
elif [ -f "setup.py" ]; then
  echo "installing via setup.py"
  pip install .
  pip install -e ../../lib
elif [ -f "Pipfile" ]; then
  echo "installing via pipenv"
  export PYPI_PASSWORD=$(cat /run/secrets/PYPI_PASSWORD)
  pipenv install
elif [ -f "pyproject.toml" ]; then
  echo "installing via poetry"
  export POETRY_HTTP_BASIC_NAUTILUS_USERNAME=$(cat /run/secrets/POETRY_HTTP_BASIC_NAUTILUS_USERNAME)
  export POETRY_HTTP_BASIC_NAUTILUS_PASSWORD=$(cat /run/secrets/POETRY_HTTP_BASIC_NAUTILUS_PASSWORD)
  echo "username is: ${POETRY_HTTP_BASIC_NAUTILUS_USERNAME}"
  poetry install
fi
