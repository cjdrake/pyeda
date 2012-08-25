# -*- coding: utf-8 -*-

__copyright__ = "Copyright (c) 2012, Chris Drake"
__license__ = "All rights reserved."

# standard library
from distutils.core import setup

# pyeda
from pyeda import __version__

with open("README.rst") as fin:
    README = fin.read()

with open("LICENSE") as fin:
    LICENSE = fin.read()

PACKAGES = ["pyeda"]

setup(
    name="pyeda",
    version=__version__,
    description="Python Electronic Design Automation",
    long_description=README,
    author="Chris Drake",
    author_email="cjdrake AT gmail DOT com",
    url="https://github.com/cjdrake/pyeda",
    license=LICENSE,
    packages=PACKAGES
)
