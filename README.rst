Python Electronic Design Automation Repository
==============================================

PyEDA is a Python library for electronic design automation.

`Read the docs! <http://pyeda.rtfd.org>`_

Features
========

* Symbolic Boolean algebra with a selection of function representations:

  * Logic expressions
  * Fast, disjunctive/conjunctive normal form logic expressions
  * Reduced, ordered binary decision diagrams (ROBDDs)
  * Truth tables, with three output states (0, 1, "don't care")

* SAT solvers:

  * Backtracking
  * DPLL

* Formal equivalence
* Multi-dimensional bit vectors
* DIMACS CNF/SAT parsers

Download
========

Bleeding edge code::

    $ git clone git://github.com/cjdrake/pyeda.git

For release tarballs and zipfiles,
visit PyEDA's page at the
`Cheese Shop <https://pypi.python.org/pypi/pyeda>`_.

Installation
============

Latest released version using distutils::

    $ easy_install pyeda

Latest release version using virtualenv::

    $ pip install pyeda

Installation from the repository::

    $ python setup.py install

Contact the Author
==================

* Chris Drake (cjdrake AT gmail DOT com), http://cjdrake.blogspot.com
