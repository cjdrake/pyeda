# Filename: Makefile

NOSETESTS := nosetests
PIP := pip
PYLINT := pylint

PIP_INSTALL_FLAGS := -r requirements.txt --use-mirrors

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
	@$(NOSETESTS) --with-doctest

.PHONY: cover
cover:
	@$(NOSETESTS) --with-doctest --with-coverage --cover-html
