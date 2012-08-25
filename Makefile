# Filename: Makefile

.PHONY: clean init html test

clean:
	rm -rf `find . -name __pycache__`
	rm -f MANIFEST
	rm -rf build dist
	rm -rf doc/build

html:
	@cd doc && $(MAKE) html

init:
	@pip install -r requirements.txt --use-mirrors

test:
	@nosetests
