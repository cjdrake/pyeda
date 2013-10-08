.. _expr:

***********************
  Boolean Expressions
***********************

Expressions are a very powerful and flexible way to represent Boolean functions.
They are the central data type of PyEDA's symbolic Boolean algebra engine.
This chapter will explain how to construct and manipulate Boolean expressions.

The code examples in this chapter assume that you have already prepared your
terminal by importing all interactive symbols from PyEDA::

   >>> from pyeda.inter import *

Expression Constants
====================

You can represent :math:`0` and :math:`1` as expressions::

   >>> zero = expr(0)
   >>> one = expr(1)

We will describe the ``expr`` function in more detail later.
For now, let's just focus on the representation of constant values.

All of the following conversions from :math:`0` have the same effect::

   >>> zeroA = expr(0)
   >>> zeroB = expr(False)
   >>> zeroC = expr("0")
   # All three 'zero' objects are the same
   >>> zeroA == zeroB == zeroC
   True

Similarly for :math:`1`::

   >>> oneA = expr(1)
   >>> oneB = expr(True)
   >>> oneC = expr("1")
   # All three 'one' objects are the same
   >>> oneA == oneB == oneC
   True

However, these results might come as a surprise::

   >>> expr(0) == 0
   False
   >>> expr(1) == True
   False

PyEDA evaluates all zero-like and one-like objects,
and stores them internally using a module-level singleton in
``pyeda.boolalg.expr``::

   >>> type(expr(0))
   pyeda.boolalg.expr._ExprZero
   >>> type(expr(1))
   pyeda.boolalg.expr._ExprOne

Once you have converted zero/one to expressions,
they implement the full Boolean Function API::

   # Constant values have an empty support set
   >>> one.support
   frozenset()
   # Apparently, zero is not satisfiable
   >>> zero.satisfy_one() is None
   True

This fact might seem underwhelming,
but it can have some neat applications.
For example, here is a sneak peak of Shannon expansions::

   >>> a, b = map(exprvar, 'ab')
   >>> zero.expand([a, b], conj=True)
   (a + b) * (a + b') * (a' + b) * (a' + b')
   >>> one.expand([a, b])
   a' * b' + a' * b + a * b' + a * b

Expression Literals: Variables and Complements
==============================================

.. exprvar(name, index=None)
.. exprcomp(exprvar)

.. ordering rules

Constructing Expressions
========================

From Variables and Operators
----------------------------

From Factory Functions
----------------------

.. def Not(arg, simplify=True, factor=False, conj=False)

.. invert

.. def Or(*args, simplify=True, factor=False, conj=False)
   def And(*args, simplify=True, factor=False, conj=False)
   def Xor(*args, simplify=True, factor=False, conj=False)
   def Xnor(*args, simplify=True, factor=False, conj=False)
   def Equal(*args, simplify=True, factor=False, conj=False)
   def Unequal(*args, simplify=True, factor=False, conj=False)

.. def Implies(p, q, simplify=True, factor=False, conj=False)
   def ITE(s, d1, d0, simplify=True, factor=False, conj=False)

.. def Nor(*args, simplify=True, factor=False, conj=False)
   def Nand(*args, simplify=True, factor=False, conj=False)
   def OneHot0(*args, simplify=True, factor=False, conj=False)
   def OneHot(*args, simplify=True, factor=False, conj=False)

From the ``expr`` Function
--------------------------

.. expr(arg, simplify=True, factor=False)

Expression Types
================

* basic (unsimplified)
* simplifed
* factored
* normal form (depth, term_index)
* canonical normal form (reduce)

.. term ordering rules
.. shannon expansions

Tseitin's Encoding
==================

Formal Equivalence
==================
