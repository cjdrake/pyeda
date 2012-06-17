# Filename: Makefile

.PHONY: clean init test

PYTHON := python

clean:
	rm -rf build dist

init:
	pip install -r requirements.txt --use-mirrors

test:
	$(PYTHON) test.py
