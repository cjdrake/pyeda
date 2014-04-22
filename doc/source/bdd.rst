.. _bdd:

****************************
  Binary Decision Diagrams
****************************

A binary decision diagram is a directed acyclic graph used to represent a
Boolean function.
They were originally introduced by Lee [#f1]_,
and later by Akers [#f2]_.
In 1986, Randal Bryant introduced the reduced, ordered BDD (ROBDD) [#f3]_.

The ROBDD is a *canonical* form,
which means that given an identical ordering of input variables,
equivalent Boolean functions will always reduce to the same ROBDD.
This is a very desirable property for determining formal equivalence.
Also, it means that unsatisfiable functions will be reduced to zero,
making SAT/UNSAT calculations trivial.
Due to these auspicious properties, the term BDD almost always refers to some
minor variation of the ROBDD devised by Bryant.

In this chapter,
we will discuss how to construct and visualize ROBDDs using PyEDA.

The code examples in this chapter assume that you have already prepared your
terminal by importing all interactive symbols from PyEDA::

   >>> from pyeda.inter import *

Constructing BDDs
=================

There are two ways to construct a BDD:

1. Convert an expression
2. Use operators on existing BDDs

Convert an Expression
---------------------

Since the Boolean expression is PyEDA's central data type,
you can use the ``expr2bdd`` function to convert arbitrary expressions to BDDs::

   >>> f = expr("a & b | a & c | b & c")
   >>> f
   Or(And(a, b), And(a, c), And(b, c))
   >>> f = expr2bdd(f)
   >>> f
   BDD(1, <pyeda.boolalg.bdd.BDDNode object at 0x7f543690b128>, <pyeda.boolalg.bdd.BDDNode object at 0x7f543690b198>)

As you can see, the BDD does not have such a useful string representation.
More on this subject later.

Using Operators
---------------

Just like expressions, BDDs have their own ``Variable`` implementation.
You can use the ``bddvar`` function to construct them::

   >>> a, b, c = map(bddvar, 'abc')
   >>> type(a)
   pyeda.boolalg.bdd.BDDVariable
   >>> isinstance(a, BinaryDecisionDiagram)
   True

Creating indexed variables with namespaces always works just like expressions::

   >>> a0 = bddvar('a', 0)
   >>> a0
   a[0]
   >>> b_a_0_1 = bddvar(('a', 'b'), (0, 1))
   b.a[0][1]

Also, the ``bddvars`` function can be used to create multi-dimensional arrays
of indexed variables::

   >>> X = bddvars('x', 4, 4)
   >>> X
   farray([[x[0][0], x[0][1], x[0][2], x[0][3]],
           [x[1][0], x[1][1], x[1][2], x[1][3]],
           [x[2][0], x[2][1], x[2][2], x[2][3]],
           [x[3][0], x[3][1], x[3][2], x[3][3]]])

From variables, you can use Python's ``~|&^`` operators to construct arbitrarily
large BDDs.

Here is the simple majority function again::

   >>> f = a & b | a & c | b & c
   >>> f
   BDD(1, <pyeda.boolalg.bdd.BDDNode object at 0x7f543690b128>, <pyeda.boolalg.bdd.BDDNode object at 0x7f543690b198>)

This time, we can see the benefit of having variables available::

   >>> f.restrict({a: 0})
   BDD(2, <pyeda.boolalg.bdd.BDDNode object at 0x7f5436b7dfd0>, <pyeda.boolalg.bdd.BDDNode object at 0x7f543690b048>)
   >>> f.restrict({a: 1, b: 0})
   c
   >>> f.restrict({a: 1, b: 1})
   1

BDD Visualization with IPython and GraphViz
===========================================

Satisfiability
==============

Formal Equivalence
==================

Variable Ordering
=================

References
==========

.. [#f1] C.Y. Lee,
         *Representation of Switching Circuits by Binary-Decision Programs*,
         Bell System Technical Journal, Vol. 38, July 1959, pp. 985-999.

.. [#f2] S.B. Akers,
         *Binary Decision Diagrams*,
         IEEE Transactions on Computers, Vol. C-27, No. 6, June 1978, pp. 509-516.

.. [#f3] Randal E. Bryant
         *Graph-Based Algorithms for Boolean Function Manipulation*,
         IEEE Transactions on Computers, 1986
         http://www.cs.cmu.edu/~bryant/pubdir/ieeetc86.pdf

