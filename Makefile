# Filename: Makefile

PIP := pip
PYLINT := pylint
PYTHON := python

PIP_INSTALL_FLAGS := -r requirements.txt

default: test

.PHONY: init
init:
	@$(PIP) install $(PIP_INSTALL_FLAGS)

.PHONY: html
html:
	@cd doc && $(MAKE) html

.PHONY: lint
lint:
	@$(PYLINT) pyeda --rcfile .pylintrc

.PHONY: test
test:
	@$(PYTHON) setup.py nosetests --with-doctest

.PHONY: cover
cover:
	@$(PYTHON) setup.py nosetests --with-doctest --with-coverage --cover-html
