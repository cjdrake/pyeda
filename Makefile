# Filename: Makefile

.PHONY: clean init html test

NOSETESTS := nosetests

PIP := pip
PIP_INSTALL_FLAGS := -r requirements.txt --use-mirrors

init:
	@$(PIP) install $(PIP_INSTALL_FLAGS)

html:
	@cd doc && $(MAKE) html

test:
	@$(NOSETESTS) --with-doctest

cover:
	@$(NOSETESTS) --with-doctest --with-coverage --cover-html
