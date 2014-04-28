.. _install:

.. _easy_install: http://pythonhosted.org/setuptools/easy_install.html
.. _pip: http://www.pip-installer.org/en/latest

.. _IPython: http://ipython.org
.. _Nose: http://nose.readthedocs.org/en/latest
.. _PyLint: http://www.pylint.org
.. _Sphinx: http://sphinx-doc.org

********************
  Installing PyEDA
********************

This page describes how to procure your very own, shiny copy of PyEDA.
It is a primary goal of the PyEDA project to be a mainstream Python package,
and adhere to the majority of conventions observed by the community.

Supported Platforms
===================

PyEDA supports Windows, and any platform with a C compiler.
The author does most development and testing on Linux Mint.

Supported Python Versions
=========================

Starting with version ``0.15``, PyEDA will only work with Python 3.2+.
Starting with version ``0.23``, PyEDA will only work with Python 3.3+.
There were several reasons to drop support for Python 2:

* Python 3 is the future of the language.
* Almost all scientific software either has already been ported,
  or is in the process of being ported to Python 3.
* Only Python 3 has support for the ``def f(*args, kw1=val1, ...)`` syntax,
  used to great effect by logic expression factory functions.
* It is too arduous to research and support all the C API changes from version
  2 to version 3. Preprocessor is evil.

That said, the source code does not yet utilize several new Python 3 features.
For example, classes are still declared using the Python 2.7 syntax for
"new-style" classes, ie ``class ClassName(object)``.
The primary reason is that `PyLint`_ is a little slow to support some of the
latest and greatest language features.

Distutils / Virtualenv
======================

The latest PyEDA release is hosted on
`PyPI <http://pypi.python.org/pypi/pyeda>`_.

To get PyEDA with `pip`_ (recommended)::

   $ pip3 install pyeda

.. note::
   If you are using the Linux system distribution of pip,
   most likely ``pip`` will be part of Python-2.x, which won't work.
   It's safer to always use ``pip3``.

To get PyEDA with `easy_install`_ (not recommended)::

   $ easy_install pyeda

We *strongly* recommend that you also install an excellent Python tool called
`IPython`_.
For interactive use,
it is vastly superior to using the standard Python interpreter.
To install IPython into your virtual environment::

   $ pip install ipython

Getting the Source
==================

The PyEDA repository is hosted on `GitHub <https://github.com/cjdrake/pyeda>`_.
If you want the bleeding-edge source code, here is how to get it:

.. code-block:: sh

   $ git clone https://github.com/cjdrake/pyeda.git
   $ cd pyeda
   # $PREFIX is the root of the installation area
   $ python setup.py install --prefix $PREFIX

If you want to build the documentation,
you must have the excellent `Sphinx`_ documentaton system installed.

::

   $ make html

If you want to run the tests,
you must have the excellent `Nose`_ unit testing framework installed.

::

   $ make test
   ....................................
   ----------------------------------------------------------------------
   Ran 72 tests in 15.123s

   OK

