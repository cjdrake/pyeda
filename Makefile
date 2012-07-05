# Filename: Makefile

.PHONY: clean init test

clean:
	rm -rf build dist

init:
	pip install -r requirements.txt --use-mirrors

test:
	nosetests
