set -xe
isort . --check-only
flake8 . --show-source
pylint .
mypy .
