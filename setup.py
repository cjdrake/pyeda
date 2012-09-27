# -*- coding: utf-8 -*-

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# standard library
from distutils.core import setup

# pyeda
import pyeda

with open("README.rst") as fin:
    README = fin.read()

with open("LICENSE") as fin:
    LICENSE = fin.read()

PACKAGES = ["pyeda"]

CLASSIFIERS = [
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
]

setup(
    name="pyeda",
    version=pyeda.__version__,
    description="Python Electronic Design Automation",
    long_description=README,
    author="Chris Drake",
    author_email="cjdrake AT gmail DOT com",
    url="https://github.com/cjdrake/pyeda",
    license=LICENSE,
    packages=PACKAGES,
    classifiers=CLASSIFIERS
)
