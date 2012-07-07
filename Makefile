# Filename: Makefile

.PHONY: clean init test

clean:
	rm -rf __pycache__ pyeda/__pycache__
	rm -rf build dist

init:
	pip install -r requirements.txt --use-mirrors

test:
	nosetests
