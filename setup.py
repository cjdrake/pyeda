# Filename: setup.py

from setuptools import setup, Extension

import pyeda

NAME = 'pyeda'
VERSION = pyeda.__version__
AUTHOR = "Chris Drake"
AUTHOR_EMAIL = "cjdrake AT gmail DOT com"
DESCRIPTION = "Python Electronic Design Automation"
KEYWORDS = [
    "Boolean algebra",
    "Boolean satisfiability",
    "computer arithmetic",
    "digital arithmetic",
    "digital logic",
    "EDA",
    "electronic design automation",
    "logic",
    "logic synthesis",
    "math",
    "mathematics",
    "satisfiability",
    "SAT",
]

with open('README.rst') as fin:
    README = fin.read()

with open('LICENSE') as fin:
    LICENSE = fin.read()

URL = "https://github.com/cjdrake/pyeda"
DOWNLOAD_URL = "https://pypi.python.org/packages/source/p/pyeda"
CLASSIFIERS = [
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
]

PACKAGES = [
    'pyeda',
    'pyeda.test',
    'pyeda.boolalg',
    'pyeda.boolalg.test',
    'pyeda.logic',
    'pyeda.logic.test',
    'pyeda.parsing',
    'pyeda.parsing.test',
]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    keywords=KEYWORDS,
    long_description=README,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    test_suite='nose.collector',
)
