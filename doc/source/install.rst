.. install.rst

====================
  Installing PyEDA
====================

This page describes how to procure your very own, shiny copy of PyEDA. It is
a primary goal of the PyEDA project to be a mainstream Python package, and
adhere to the majority of conventions observed by the community. Therefore,
hopefully most of the instructions that follow will seem familiar to you.

Distutils / Virtualenv
======================

The latest PyEDA release is hosted at
`PyPI <http://pypi.python.org/pypi/pyeda>`_.

.. highlight:: sh

To get PyEDA with distutils::

   $ easy_install pyeda

To get PyEDA with virtualenv::

   $ pip install pyeda

We *strongly* recommend that you also install an excellent Python tool called
`IPython <http://ipython.org>`_. For interactive use, it is vastly superior to
using the standard Python interpreter. To install ipython into your virtual
environment::

   $ pip install ipython

Getting the Source
==================

The PyEDA repository is hosted at `Github <https://github.com>`_. If you want
the bleeding-edge source code, here is how to get it:

.. parsed-literal::

   $ git clone https://github.com/cjdrake/pyeda.git
   $ cd pyeda
   # $PREFIX is the root of the installation area
   $ python setup.py install --prefix $PREFIX

If you want to build the documentation, you must have excellent Python
documentation system `Sphinx <http://sphinx.pocoo.org>`_ installed.

.. parsed-literal::

   $ make html

If you want to run the tests, you must have the excellent Python
`nose <http://nose.readthedocs.org/en/latest>`_ unit testing framework
installed.

.. parsed-literal::

   $ make test
   ....................................
   ----------------------------------------------------------------------
   Ran 36 tests in 0.990s

   OK
