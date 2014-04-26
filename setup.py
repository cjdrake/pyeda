# Filename: setup.py

import os
import sys
from os.path import join as pjoin

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
    "binary decision diagram",
    "Boolean algebra",
    "Boolean satisfiability",
    "combinational logic",
    "combinatorial logic",
    "computer arithmetic",
    "digital arithmetic",
    "digital logic",
    "EDA",
    "electronic design automation",
    "Espresso",
    "Espresso-exact",
    "Espresso-signature",
    "logic",
    "logic minimization",
    "logic optimization",
    "logic synthesis",
    "math",
    "mathematics",
    "PicoSAT",
    "SAT",
    "satisfiability",
    "truth table",
    "Two-level logic minimization",
    "Two-level logic optimization",
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
    "Programming Language :: Python :: 3.4",
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

with open(pjoin('extension', 'picosat', 'VERSION')) as fin:
    PICOSAT_VERSION = '"' + fin.read().strip() + '"'

# PicoSAT extension
PICOSAT = dict(
    define_macros = [
        ('NDEBUG', None),
    ],
    include_dirs = [
        pjoin('extension', 'picosat'),
    ],
    sources = [
        pjoin('extension', 'picosat', 'picosat.c'),
        pjoin('pyeda', 'boolalg', 'picosatmodule.c'),
    ],
)

if sys.platform == 'win32':
    PICOSAT['define_macros'] += [
        ('NGETRUSAGE', None),
        ('inline', '__inline'),
    ]

ESPRESSO = dict(
    define_macros = [],
    include_dirs = [
        pjoin('extension', 'espresso', 'src'),
    ],
    sources = [
        pjoin('extension', 'espresso', 'src', 'cofactor.c'),
        pjoin('extension', 'espresso', 'src', 'cols.c'),
        pjoin('extension', 'espresso', 'src', 'compl.c'),
        pjoin('extension', 'espresso', 'src', 'contain.c'),
        pjoin('extension', 'espresso', 'src', 'cubestr.c'),
        pjoin('extension', 'espresso', 'src', 'cvrin.c'),
        pjoin('extension', 'espresso', 'src', 'cvrm.c'),
        pjoin('extension', 'espresso', 'src', 'cvrmisc.c'),
        pjoin('extension', 'espresso', 'src', 'cvrout.c'),
        pjoin('extension', 'espresso', 'src', 'dominate.c'),
        pjoin('extension', 'espresso', 'src', 'espresso.c'),
        pjoin('extension', 'espresso', 'src', 'essen.c'),
        pjoin('extension', 'espresso', 'src', 'exact.c'),
        pjoin('extension', 'espresso', 'src', 'expand.c'),
        pjoin('extension', 'espresso', 'src', 'gasp.c'),
        pjoin('extension', 'espresso', 'src', 'gimpel.c'),
        pjoin('extension', 'espresso', 'src', 'globals.c'),
        pjoin('extension', 'espresso', 'src', 'hack.c'),
        pjoin('extension', 'espresso', 'src', 'indep.c'),
        pjoin('extension', 'espresso', 'src', 'irred.c'),
        pjoin('extension', 'espresso', 'src', 'matrix.c'),
        pjoin('extension', 'espresso', 'src', 'mincov.c'),
        pjoin('extension', 'espresso', 'src', 'opo.c'),
        pjoin('extension', 'espresso', 'src', 'pair.c'),
        pjoin('extension', 'espresso', 'src', 'part.c'),
        pjoin('extension', 'espresso', 'src', 'primes.c'),
        pjoin('extension', 'espresso', 'src', 'reduce.c'),
        pjoin('extension', 'espresso', 'src', 'rows.c'),
        pjoin('extension', 'espresso', 'src', 'set.c'),
        pjoin('extension', 'espresso', 'src', 'setc.c'),
        pjoin('extension', 'espresso', 'src', 'sharp.c'),
        pjoin('extension', 'espresso', 'src', 'sminterf.c'),
        pjoin('extension', 'espresso', 'src', 'solution.c'),
        pjoin('extension', 'espresso', 'src', 'sparse.c'),
        pjoin('extension', 'espresso', 'src', 'unate.c'),
        pjoin('extension', 'espresso', 'src', 'verify.c'),
        pjoin('pyeda', 'boolalg', 'espressomodule.c'),
    ],
)

EXT_MODULES = [
    Extension('pyeda.boolalg.picosat', **PICOSAT),
    Extension('pyeda.boolalg.espresso', **ESPRESSO),
]

SCRIPTS = [
    pjoin('script', 'espresso'),
    pjoin('script', 'picosat'),
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
    scripts=SCRIPTS,

    test_suite='nose.collector',
)

