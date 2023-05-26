# Filename: Makefile

PYLINT := pylint
PYTHON := python3

PIP_INSTALL_FLAGS := -r requirements.txt

.PHONY: help
help:
	@printf "Usage: make [options] [target] ...\n"
	@printf "\n"
	@printf "Valid targets:\n"
	@printf "\n"
	@printf "    help            Display this help message\n"
	@printf "    test            Run unit test suite\n"
	@printf "    lint            Run lint checks\n"
	@printf "    cover           Collect coverage\n"
	@printf "    html            Build Sphinx documentation\n"

.PHONY: test
test:
	@pytest --doctest-modules --ignore=doc

.PHONY: lint
lint:
	@$(PYLINT) pyeda --rcfile .pylintrc

.PHONY: cover
cover:
	@pytest --doctest-modules --ignore=doc --cov=pyeda --cov-report=html

.PHONY: html
html:
	@$(PYTHON) setup.py build_sphinx

