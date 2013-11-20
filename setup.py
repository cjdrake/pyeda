# Filename: setup.py

import os
import sys

import pyeda

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

NAME = pyeda.__name__

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
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
]

PYEDA_PKGS = [
    'pyeda',
    'pyeda.boolalg',
    'pyeda.logic',
    'pyeda.parsing',
]

TEST_PKGS = [
    'pyeda.test',
    'pyeda.boolalg.test',
    'pyeda.logic.test',
    'pyeda.parsing.test',
]

PACKAGES = PYEDA_PKGS + TEST_PKGS

with open(os.path.join('extension', 'picosat', 'VERSION')) as fin:
    PICOSAT_VERSION = '"' + fin.read().strip() + '"'

# PicoSAT extension
PICOSAT = dict(
    define_macros = [
        ('NDEBUG', None),
    ],
    include_dirs = [
        os.path.join('extension', 'picosat'),
    ],
    sources = [
        os.path.join('extension', 'picosat', 'picosat.c'),
        os.path.join('pyeda', 'boolalg', 'picosatmodule.c'),
    ],
)

if sys.platform == 'win32':
    PICOSAT['define_macros'] += [
        ('NGETRUSAGE', None),
        ('inline', '__inline'),
    ]

EXT_MODULES = [
    Extension('pyeda.boolalg.picosat', **PICOSAT),
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
    ext_modules=EXT_MODULES,

    test_suite='nose.collector',
)
