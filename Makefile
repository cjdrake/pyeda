# Filename: Makefile

.PHONY: clean init html test

NOSETESTS := nosetests
NOSE_FLAGS := --with-doctest

PIP := pip
PIP_INSTALL_FLAGS := -r requirements.txt --use-mirrors

clean:
	rm -f MANIFEST
	rm -rf __pycache__ pyeda/__pycache__
	rm -rf build dist
	rm -rf doc/build

init:
	@$(PIP) install $(PIP_INSTALL_FLAGS)

html:
	@cd doc && $(MAKE) html

test:
	@$(NOSETESTS) $(NOSE_FLAGS)
