.. index.rst

Python EDA Documentation
========================

:Release: |version|
:Date: |today|

PyEDA is a Python library for electronic design automation.

Fork PyEDA: https://github.com/cjdrake/pyeda

Features:

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

Contents:

.. toctree::
   :maxdepth: 2

   overview.rst
   install.rst
   boolalg.rst
   sudoku.rst
   relnotes.rst


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
