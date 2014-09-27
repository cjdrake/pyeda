***************************************
  Python Electronic Design Automation
***************************************

PyEDA is a Python library for electronic design automation.

`Read the docs! <http://pyeda.rtfd.org>`_

.. image:: https://travis-ci.org/cjdrake/pyeda.png?branch=master
   :target: https://travis-ci.org/cjdrake/pyeda

Features
========

* Symbolic Boolean algebra with a selection of function representations:

  * Logic expressions
  * Truth tables, with three output states (0, 1, "don't care")
  * Reduced, ordered binary decision diagrams (ROBDDs)

* SAT solvers:

  * Backtracking
  * `PicoSAT <http://fmv.jku.at/picosat>`_

* `Espresso <http://embedded.eecs.berkeley.edu/pubs/downloads/espresso/index.htm>`_ logic minimization
* Formal equivalence
* Multi-dimensional bit vectors
* DIMACS CNF/SAT parsers
* Logic expression parser

Download
========

Bleeding edge code::

   $ git clone git://github.com/cjdrake/pyeda.git

For release tarballs and zipfiles,
visit PyEDA's page at the
`Cheese Shop <https://pypi.python.org/pypi/pyeda>`_.

Installation
============

Latest release version using
`pip <http://www.pip-installer.org/en/latest>`_::

   $ pip3 install pyeda

Installation from the repository::

   $ python3 setup.py install

Logic Expressions
=================

Invoke your favorite Python terminal,
and invoke an interactive ``pyeda`` session::

   >>> from pyeda.inter import *

Create some Boolean expression variables::

   >>> a, b, c, d = map(exprvar, "abcd")

Construct Boolean functions using overloaded Python operators:
``~`` (NOT), ``|`` (OR), ``^`` (XOR), ``&`` (AND), ``>>`` (IMPLIES)::

   >>> f0 = ~a & b | c & ~d
   >>> f1 = a >> b
   >>> f2 = ~a & b | a & ~b
   >>> f3 = ~a & ~b | a & b
   >>> f4 = ~a & ~b & ~c | a & b & c
   >>> f5 = a & b | ~a & c

Construct Boolean functions using standard function syntax::

   >>> f10 = Or(And(Not(a), b), And(c, Not(d)))
   >>> f11 = Implies(a, b)
   >>> f12 = Xor(a, b)
   >>> f13 = Xnor(a, b)
   >>> f14 = Equal(a, b, c)
   >>> f15 = ITE(a, b, c)
   >>> f16 = Nor(a, b, c)
   >>> f17 = Nand(a, b, c)

Construct Boolean functions using higher order operators::

   >>> OneHot(a, b, c)
   And(Or(~a, ~b), Or(~a, ~c), Or(~b, ~c), Or(a, b, c))
   >>> OneHot0(a, b, c)
   And(Or(~a, ~b), Or(~a, ~c), Or(~b, ~c))
   >>> Majority(a, b, c)
   Or(And(a, b), And(a, c), And(b, c))
   >>> AchillesHeel(a, b, c, d)
   And(Or(a, b), Or(c, d))

Investigate a function's properties::

   >>> f0.support
   frozenset({a, b, c, d})
   >>> f0.inputs
   (a, b, c, d)
   >>> f0.top
   a
   >>> f0.degree
   4
   >>> f0.cardinality
   16
   >>> f0.depth
   2

Factor complex expressions into only OR/AND and literals::

   >>> f11.factor()
   Or(~a, b)
   >>> f12.factor()
   Or(And(~a, b), And(a, ~b))
   >>> f13.factor()
   Or(And(~a, ~b), And(a, b))
   >>> f14.factor()
   Or(And(~a, ~b, ~c), And(a, b, c))
   >>> f15.factor()
   Or(And(a, b), And(~a, c))
   >>> f16.factor()
   And(~a, ~b, ~c)
   >>> f17.factor()
   Or(~a, ~b, ~c)

Restrict a function's input variables to fixed values,
and perform function composition::

   >>> f0.restrict({a: 0, c: 1})
   Or(b, ~d)
   >>> f0.compose({a: c, b: ~d})
   Or(And(~c, ~d), And(c, ~d))

Test function formal equivalence::

   >>> f2.equivalent(f12)
   True
   >>> f4.equivalent(f14)
   True

Investigate Boolean identities::

   # Double complement
   >>> ~~a
   a

   # Idempotence
   >>> a | a
   a
   >>> a & a
   a

   # Identity
   >>> a | 0
   a
   >>> a & 1
   a

   # Dominance
   >>> a | 1
   1
   >>> a & 0
   0

   # Commutativity
   >>> (a | b).equivalent(b | a)
   True
   >>> (a & b).equivalent(b & a)
   True

   # Associativity
   >>> a | (b | c)
   Or(a, b, c)
   >>> a & (b & c)
   And(a, b, c)

   # Distributive
   >>> (a | (b & c)).to_cnf()
   And(Or(a, b), Or(a, c))
   >>> (a & (b | c)).to_dnf()
   Or(And(a, b), And(a, c))

   # De Morgan's
   >>> Not(a | b).factor()
   And(~a, ~b)
   >>> Not(a & b).factor()
   Or(~a, ~b)

   # Absorption
   >>> (a | (a & b)).absorb()
   a
   >>> (a & (a | b)).absorb()
   a

Perform Shannon expansions::

   >>> a.expand(b)
   Or(And(a, ~b), And(a, b))
   >>> (a & b).expand([c, d])
   Or(And(a, b, ~c, ~d), And(a, b, ~c, d), And(a, b, c, ~d), And(a, b, c, d))

Convert a nested expression to disjunctive normal form::

   >>> f = a & (b | (c & d))
   >>> f.depth
   3
   >>> g = f.to_dnf()
   >>> g
   Or(And(a, b), And(a, c, d))
   >>> g.depth
   2
   >>> f.equivalent(g)
   True

Convert between disjunctive and conjunctive normal forms::

   >>> f = ~a & ~b & c | ~a & b & ~c | a & ~b & ~c | a & b & c
   >>> g = f.to_cnf()
   >>> h = g.to_dnf()
   >>> g
   And(Or(a, b, c), Or(a, ~b, ~c), Or(~a, b, ~c), Or(~a, ~b, c))
   >>> h
   Or(And(~a, ~b, c), And(~a, b, ~c), And(a, ~b, ~c), And(a, b, c))

Multi-Dimensional Bit Vectors
=============================

Create some four-bit vectors, and use slice operators::

   >>> A = exprvars('a', 4)
   >>> B = exprvars('b', 4)
   >>> A
   farray([a[0], a[1], a[2], a[3]])
   >>> A[2:]
   farray([a[2], a[3]])
   >>> A[-3:-1]
   farray([a[1], a[2]])

Perform bitwise operations using Python overloaded operators:
``~`` (NOT), ``|`` (OR), ``&`` (AND), ``^`` (XOR)::

   >>> ~A
   farray([~a[0], ~a[1], ~a[2], ~a[3]])
   >>> A | B
   farray([Or(a[0], b[0]), Or(a[1], b[1]), Or(a[2], b[2]), Or(a[3], b[3])])
   >>> A & B
   farray([And(a[0], b[0]), And(a[1], b[1]), And(a[2], b[2]), And(a[3], b[3])])
   >>> A ^ B
   farray([Xor(a[0], b[0]), Xor(a[1], b[1]), Xor(a[2], b[2]), Xor(a[3], b[3])])

Reduce bit vectors using unary OR, AND, XOR::

   >>> A.uor()
   Or(a[0], a[1], a[2], a[3])
   >>> A.uand()
   And(a[0], a[1], a[2], a[3])
   >>> A.uxor()
   Xor(a[0], a[1], a[2], a[3])

Create and test functions that implement non-trivial logic such as arithmetic::

   >>> from pyeda.logic.addition import *
   >>> S, C = ripple_carry_add(A, B)
   # Note "1110" is LSB first. This says: "7 + 1 = 8".
   >>> S.vrestrict({A: "1110", B: "1000"}).to_uint()
   8

Other Function Representations
==============================

Consult the `documentation <http://pyeda.rtfd.org>`_ for information about
truth tables, and binary decision diagrams.
Each function representation has different trade-offs,
so always use the right one for the job.

PicoSAT SAT Solver C Extension
==============================

PyEDA includes an extension to the industrial-strength
`PicoSAT <http://fmv.jku.at/picosat>`_ SAT solving engine.

Use the ``satisfy_one`` method to finding a single satisfying input point::

   >>> f = OneHot(a, b, c)
   >>> f.satisfy_one()
   {a: 0, b: 0, c: 1}

Use the ``satisfy_all`` method to iterate through all satisfying input points::

   >>> list(f.satisfy_all())
   [{a: 0, b: 0, c: 1}, {a: 0, b: 1, c: 0}, {a: 1, b: 0, c: 0}]

For more interesting examples, see the following documentation chapters:

* `Solving Sudoku <http://pyeda.readthedocs.org/en/latest/sudoku.html>`_
* `All Solutions to the Eight Queens Puzzle <http://pyeda.readthedocs.org/en/latest/queens.html>`_

Espresso Logic Minimization C Extension
=======================================

PyEDA includes an extension to the famous Espresso library for the minimization
of two-level covers of Boolean functions.

Use the ``espresso_exprs`` function to minimize multiple expressions::

   >>> f1 = ~a & ~b & ~c | ~a & ~b & c | a & ~b & c | a & b & c | a & b & ~c
   >>> f2 = ~a & ~b & c | a & ~b & c
   >>> f1m, f2m = espresso_exprs(f1, f2)
   >>> f1m
   Or(And(~a, ~b), And(a, b), And(~b, c))
   >>> f2m
   And(~b, c)

Use the ``espresso_tts`` function to minimize multiple truth tables::

   >>> X = exprvars('x', 4)
   >>> f1 = truthtable(X, "0000011111------")
   >>> f2 = truthtable(X, "0001111100------")
   >>> f1m, f2m = espresso_tts(f1, f2)
   >>> f1m
   Or(x[3], And(x[0], x[2]), And(x[1], x[2]))
   >>> f2m
   Or(x[2], And(x[0], x[1]))

Execute Unit Test Suite
=======================

If you have `Nose <http://nose.readthedocs.org/en/latest>`_ installed,
run the unit test suite with the following command::

   $ make test

If you have `Coverage <https://pypi.python.org/pypi/coverage>`_ installed,
generate a coverage report (including HTML) with the following command::

   $ make cover

Perform Static Lint Checks
==========================

If you have `Pylint <http://www.pylint.org>`_ installed,
perform static lint checks with the following command::

   $ make lint

Build the Documentation
=======================

If you have `Sphinx <http://sphinx-doc.org>`_ installed,
build the HTML documentation with the following command::

   $ make html

Python Versions Supported
=========================

PyEDA is developed using Python 3.3+.
It is **NOT** compatible with Python 2.7, or Python 3.2.

Contact the Authors
===================

* Chris Drake (cjdrake AT gmail DOT com), http://cjdrake.github.io

