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
they implement the full Boolean Function API.

For example, constants have an empty support set::

   >>> one.support
   frozenset()

Also, apparently zero is not satisfiable::

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

Expression Literals
===================

A Boolean *literal* is defined as a variable or its complement.
The expression variable and complement data types are the primitives of
Boolean expressions.

Variables
---------

To create expression variables, use the ``exprvar`` function.

For example, let's create a variable named :math:`a`,
and assign it to a Python object named "a"::

   >>> a = exprvar('a')
   >>> type(a)
   pyeda.boolalg.expr.ExprVariable

One efficient method for creating multiple variables is to use Python's builtin
``map`` function::

   >>> a, b, c = map(exprvar, 'abc')

The primary benefit of using the ``exprvar`` function rather than a class
constructor is to ensure that variable instances are unique::

   >>> a = exprvar('a')
   >>> a_new = exprvar('a')
   >>> id(a) == id(a_new)
   True

You can name a variable pretty much anything you want,
though we recommend standard identifiers::

   >>> foo = exprvar('foo')
   >>> holy_hand_grenade = exprvar('holy_hand_grenade')

By default, all variables go into a global namespace.
You can assign a variable to a specific namespace by passing a tuple of
strings as the first argument::

   >>> a1 = exprvar('a')
   >>> a3 = exprvar(('a', 'b', 'c'))
   >>> a1.names
   ('a', )
   >>> a3.names
   ('a', 'b', 'c')

Notice that the default representation of a variable will dot all the names
together starting with the most significant index of the tuple on the left::

   >>> str(a3)
   'c.b.a'

Since it is very common to deal with grouped variables,
you may assign indices to variables as well.
Each index is a new dimension.

To create a variable with a single index, use an integer argument::

   >>> a42 = exprvar('a', 42)
   >>> str(a42)
   a[42]

To create a variable with multiple indices, use a tuple argument::

   >>> a_1_2_3 = exprvar('a', (1, 2, 3))
   >>> str(a_1_2_3)
   a[1][2][3]

Finally, you can combine multiple namespaces and dimensions::

   >>> c_b_a_1_2_3 = exprvar(('a', 'b', 'c'), (1, 2, 3))
   >>> str(c_b_a_1_2_3)
   c.b.a[1][2][3]

.. NOTE::
   The previous syntax is starting to get a bit cumbersome.
   For a more powerful method of creating multi-dimensional bit vectors,
   use the ``bitvec`` function.

Complements
-----------

A complement is defined as the inverse of a variable.
That is:

.. math::
   a + \overline{a} = 1

   a \cdot \overline{a} = 0

One way to create a complement from a pre-existing variable is to simply
apply Python's ``-`` unary negate operator.

For example, let's create a variable and its complement::

   >>> a = exprvar('a')
   >>> -a
   a'
   >>> type(-a)
   pyeda.boolalg.expr.ExprComplement

All complements created from the same variable instance are not just identical,
they all refer to the same object::

   >>> id(-a) == id(-a)
   True

Constructing Expressions
========================

Expression are defined recursively as being composed of primitives
(constants, variables),
and expressions joined by Boolean operators.

Now that we are familiar with all of PyEDA's Boolean primitives,
we will learn how to construct more interesting expressions.

From Constants, Variables, and Python Operators
-----------------------------------------------

PyEDA overloads Python's ``-``, ``+`` and ``*`` operators with NOT, OR, and AND,
respectively.

.. note:: `Sympy <http://sympy.org>`_ overloads ``~``, ``|``, and ``&``
   for NOT, OR, and AND.
   PyEDA uses these operators for bit vectors instead.

Let's jump in by creating a full adder::

   >>> a, b, ci = map(exprvar, "a b ci".split())
   >>> s = -a * -b * ci + -a * b * -ci + a * -b * -ci + a * b * ci
   >>> co = a * b + a * ci + b * ci

You can use the ``expr2truthtable`` function to do a quick check that the
sum logic is correct::

   >>> expr2truthtable(s)
   inputs: ci b a
   000 0
   001 1
   010 1
   011 0
   100 1
   101 0
   110 0
   111 1

Similarly for the carry out logic::

   >>> expr2truthtable(co)
   inputs: ci b a
   000 0
   001 0
   010 0
   011 1
   100 0
   101 1
   110 1
   111 1

From Factory Functions
----------------------

Python does not have enough builtin symbols to handle all interesting Boolean
functions we can represent directly as an expression.
Also, binary operators are limited to two operands at a time,
whereas several Boolean operators are N-ary (arbitrary many operands).
This section will describe all the factory functions that can be used to create
arbitrary Boolean expressions.

The general form of these functions is
``OP(arg [, arg], simplify=True, factor=False [, conj=False])``.
The function is an operator name, followed by one or more arguments,
followed by the ``simplify``, and ``factor`` parameters.
Some functions also have a ``conj`` parameter,
which selects between conjunctive (``conj=True``) and disjunctive
(``conj=False``) formats.

One advantage of using these functions is that you do not need to create
variable instances prior to passing them as arguments.
You can just pass string identifiers,
and PyEDA will automatically parse and convert them to variables.

For example, the following two statements are equivalent::

   >>> Not('a[0]')
   a[0]'

and::

   >>> a0 = exprvar('a', 0)
   >>> Not(a0)
   a[0]'

Fundamental Operators
^^^^^^^^^^^^^^^^^^^^^

Since NOT, OR, and AND form a complete basis for a Boolean algebra,
these three operators are *fundamental*.

.. function:: Not(arg, simplify=True, factor=False)

.. function:: Or(\*args, simplify=True, factor=False)

.. function:: And(\*args, simplify=True, factor=False)

Example of full adder logic using ``Not``, ``Or``, and ``And``::

   >>> s = Or(And(Not('a'), Not('b'), 'ci'), And(Not('a'), 'b', Not('ci')),
              And('a', Not('b'), Not('ci')), And('a', 'b', 'ci'))
   >>> co = Or(And('a', 'b'), And('a', 'ci'), And('b', 'ci'))

Secondary Operators
^^^^^^^^^^^^^^^^^^^

A *secondary* operator is a Boolean operator that can be natively represented
as a PyEDA expression,
but contains more information than the fundamental operators.
That is, these expressions always increase in tree size when converted to
fundamental operators.

.. function:: Xor(\*args, simplify=True, factor=False, conj=False)

.. function:: Xnor(\*args, simplify=True, factor=False, conj=False)

The full adder circuit has a more dense representation when you
use the ``Xor`` operator::

   >>> s = Xor('a', 'b', 'ci')
   >>> co = Or(And('a', 'b'), And('a', 'ci'), And('b', 'ci'))

.. function:: Equal(\*args, simplify=True, factor=False, conj=False)

.. function:: Unequal(\*args, simplify=True, factor=False, conj=False)

.. function:: Implies(p, q, simplify=True, factor=False)

.. function:: ITE(s, d1, d0, simplify=True, factor=False)

High Order Operators
^^^^^^^^^^^^^^^^^^^^

A *high order* operator is a Boolean operator that can NOT be natively
represented as a PyEDA expression.
That is, these factory functions will always return expressions composed from
fundamental and/or secondary operators.

.. function:: Nor(\*args, simplify=True, factor=False)

.. function:: Nand(\*args, simplify=True, factor=False)

.. function:: OneHot0(\*args, simplify=True, factor=False, conj=True)

.. function:: OneHot(\*args, simplify=True, factor=False, conj=True)

.. function:: Majority(\*args, simplify=True, factor=False, conj=True)

The full adder circuit has a much more dense representation when you
use both the ``Xor`` and ``Majority`` operators::

   >>> s = Xor('a', 'b', 'ci')
   >>> co = Majority('a', 'b', 'ci')

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
