.. boolalg.rst

*******************
  Boolean Algebra
*******************

Boolean algebra defines the rules for working with the set {0, 1}. It is a
cornerstone of electronic design automation, and fundamental to several other
areas of computer science and engineering. PyEDA has an extensive library for
the creation and analysis of Boolean functions.

This document describes how to explore Boolean algebra using PyEDA.

.. NOTE::
   Technically, there are several Boolean algebras. If you are a mathematician,
   and you care about the distinction, we are referring unambiguously to the
   *two-valued* Boolean algebra or **switching algebra**.

Built-in Python Boolean Operations
==================================

The three operators most commonly used as the basis of Boolean algebra are the
**complement**, **sum**, and **product**. Python already has a built-in Boolean
data type, ``bool``. The keywords for zero, one are ``False``, ``True``. The keywords
for complement, sum, product are ``not``, ``or``, ``and``.

You can use the Python interpreter to evaluate complex expressions::

   >>> (True and False) or not (False or True)
   False

It is worth noting that ``False`` is equivalent to zero, and ``True`` is
equivalent to one. Also, they behave identically::

   >>> False == 0
   True
   >>> True == 1
   True
   >>> False or True, 0 or 1
   (True, 1)

PyEDA allows you to extend this basic capability to define Boolean functions.

Logical Expressions
===================

Let's define a simple Boolean function: ``F(x, y, z) = x * y + -z``

::

   >>> import pyeda

   # Create three Boolean variables
   >>> x, y, z = map(pyeda.var, "xyz")

   # Use '-', '*', '+' connectives to create a formula, and assign it to 'F'
   >>> F = x * y + -z

Work In Progress
----------------

.. autofunction:: pyeda.expr.var

.. autoclass:: pyeda.expr.Expression
   :members: depth

.. autoclass:: pyeda.expr.Not

.. autoclass:: pyeda.expr.Or

.. autofunction:: pyeda.expr.Nor

.. autoclass:: pyeda.expr.And

.. autofunction:: pyeda.expr.Nand

.. autoclass:: pyeda.expr.Xor

.. autoclass:: pyeda.expr.Implies

.. autoclass:: pyeda.expr.Equal
