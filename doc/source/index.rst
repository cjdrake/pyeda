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
  * Truth tables, with three output states (0, 1, "don't care")
  * Reduced, ordered binary decision diagrams (ROBDDs)

* SAT solvers:

  * Backtracking
  * DPLL
  * `PicoSAT <http://fmv.jku.at/picosat>`_

* Formal equivalence
* Multi-dimensional bit vectors
* DIMACS CNF/SAT parsers
* Logic expression parser

Contents:

.. toctree::
   :maxdepth: 2

   overview.rst
   install.rst
   boolalg.rst
   expr.rst
   sudoku.rst
   queens.rst
   relnotes.rst

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

