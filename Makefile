# Filename: Makefile

NOSETESTS := nosetests

PIP := pip
PIP_INSTALL_FLAGS := -r requirements.txt --use-mirrors

.PHONY: init
init:
	@$(PIP) install $(PIP_INSTALL_FLAGS)

.PHONY: html
html:
	@cd doc && $(MAKE) html

.PHONY: cover
test:
	@$(NOSETESTS) --with-doctest

.PHONY: cover
cover:
	@$(NOSETESTS) --with-doctest --with-coverage --cover-html
