.. _boolalg:

*******************
  Boolean Algebra
*******************

Boolean Algebra is a cornerstone of electronic design automation,
and fundamental to several other areas of computer science and engineering.
PyEDA has an extensive library for the creation and analysis of Boolean
functions.

This document describes how to explore Boolean algebra using PyEDA.
We will be using some mathematical language here and there,
but please do not run away screaming in fear.
This document assumes very little background knowledge.

What is Boolean Algebra?
========================

All great stories have a beginning, so let's start with the basics.
You probably took a class called "algebra" in (junior) high school.
So when you started reading this document you were already confused.
Algebra is just algebra, right?
You solve for :math:`x`, find the intersection of two lines,
and you're done, right?

As it turns out,
the high school algebra you are familiar with just scratches the surface.
There are many algebras with equally many theoretical and practical uses.
An algebra is the combination of two things:

1. a collection of mathematical objects, and
2. a collection of rules to manipulate those objects

For example, in high school algebra, you have numbers such as
:math:`\{1, 3, 5, \frac{1}{2}, .337\}`, and operators such as
:math:`\{+, -, \cdot, \div\}`.
The numbers are the mathematical objects,
and the operators are the rules for how to manipulate them.
Except in very extreme circumstances (division by zero),
whenever you add, subtract, or divide two numbers, you get another number.

Algebras are a big part of the "tools of the trade" for a mathematician.
A plumber has a wrench, a carpenter has a saw,
and a mathematician has algebras.
To each his own.

A *Boolean* algebra defines the rules for working with the set :math:`\{0, 1\}`.
So unlike in normal algebra class where you have more numbers than you can
possibly imagine, in Boolean Algebra you only have two.

Even though it is possible to define a Boolean Algebra using different
operators,
by far the most common operators are complement, sum, and product.

Complement Operator
-------------------

The complement operator is a *unary* operator,
which means it acts on a single Boolean input: :math:`x`.
The Boolean complement of :math:`x` is usually written as
:math:`x^{\prime}`, :math:`\overline{x}`, or :math:`\lnot x`.

The output of the Boolean complement is defined by:

.. math::

   \overline{0} = 1

   \overline{1} = 0

Sum Operator
------------

The sum (or disjunction) operator is a *binary* operator,
which means it acts on two Boolean inputs: :math:`(x, y)`.
The Boolean sum of :math:`x` and :math:`y` is usually written as
:math:`x + y`, or :math:`x \vee y`.

The output of the Boolean sum is defined by:

.. math::

   0 + 0 = 0

   0 + 1 = 1

   1 + 0 = 1

   1 + 1 = 1

This looks familiar so far except for the :math:`1 + 1 = 1` part.
The Boolean sum operator is also called **OR** because the output of
:math:`x` *or* :math:`y` equals 1 *if and only if*
:math:`x = 1`, *or* :math:`y = 1`, *or* both.

Product Operator
----------------

The product (or conjunction) operator is also a *binary* operator.
The Boolean product of :math:`x` and :math:`y` is usually written as
:math:`x \cdot y`, or :math:`x \wedge y`.

The output of the Boolean product is defined by:

.. math::

   0 \cdot 0 = 0

   0 \cdot 1 = 0

   1 \cdot 0 = 0

   1 \cdot 1 = 1

As you can see, the product operator looks exactly like normal multiplication.
The Boolean product is also called **AND** because the output of
:math:`x` *and* :math:`y` equals 1 *if and only if*
both :math:`x = 1`, *and* :math:`y = 1`.

Other Binary Operators
----------------------

For reference, here is a table of all binary Boolean operators:

.. csv-table::
   :header: :math:`f`, :math:`g`, 0, :math:`f \\downarrow g`, :math:`f \\lt g`, :math:`\\overline{f}`, :math:`f \\gt g`, :math:`\\overline{g}`, :math:`f \\ne g`, :math:`f \\uparrow g`, :math:`f \\cdot g`, :math:`f = g`, :math:`g`, :math:`f \\le g`, :math:`f`, :math:`f \\ge g`, :math:`f + g`, 1
   :widths: 4, 4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8
   :stub-columns: 2

   0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1
   0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1
   1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1
   1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1

Some additional notes:

* :math:`f \downarrow g` is the binary **NOR** (not or) operator.
* :math:`f \uparrow g` is the binary **NAND** (not and) operator.
* :math:`f \leq g` is commonly written using the binary implication operator
  :math:`f \implies g`.
* :math:`f = g` is commonly written using either the binary equivalence
  operator :math:`f \iff g`,
  or the binary **XNOR** (exclusive nor) operator :math:`f \odot g`.
* :math:`f \ne g` is commonly written using the binary **XOR** (exclusive or)
  operator :math:`f \oplus g`.

Additional Perspective
----------------------

You are probably thinking this is all very nice,
but what can you possibly do with an algebra that only concerns itself with
0, 1, **NOT**, **OR**, and **AND**?

In 1937, `Claude Shannon <http://en.wikipedia.org/wiki/Claude_Shannon>`_
realized that electronic circuits have two-value switches that can be combined
into networks capable of solving any logical or numeric relationship.
A transistor is nothing but an electrical switch.
Similar to a light bulb, it has two states: off (0), and on (1).
Wiring transistors together in serial imitates the **AND** operator,
and wiring them together in parallel imitates the **OR** operator.
If you wire a few thousand transistors together in interesting ways,
you can build a computer.

Import Symbols from PyEDA
=========================

All examples in this document require that you execute the following statements
in your interpreter::

   >>> from pyeda.inter import *

If you want to see all the symbols you import with this statement,
look into ``pyeda/inter.py``.

.. note::
   Using the ``from ... import *`` syntax is generally frowned upon for Python
   programming, but is *extremely* convenient for interactive use.

Built-in Python Boolean Operations
==================================

Python has a built-in Boolean data type, ``bool``.
You can think of the ``False`` keyword as an alias for the number 0,
and the ``True`` keyword as an alias for the number 1.

::

   >>> int(False)
   0
   >>> int(True)
   1
   >>> bool(0)
   False
   >>> bool(1)
   True

The keywords for complement, sum, and product are ``not``, ``or``, ``and``.

::

   >>> not True
   False
   >>> True or False
   True
   >>> True and False
   False

You can use the Python interpreter to evaluate complex expressions::

   >>> (True and False) or not (False or True)
   False

PyEDA recognizes ``False``, ``0``, and ``'0'`` as Boolean zero (0),
and ``True``, ``1``, and ``'1'`` as Boolean one (1).
You can use the ``boolify`` function to manually convert the ``bool`` and
``str`` data types to integers::

   >>> boolify(True)
   1
   >>> boolify('0')
   0

Boolean Variables
=================

Okay, so we already know what Boolean Algebra is,
and Python can already do everything we need, right?

Just like in high school algebra,
things start to get interesting when we introduce a few *variables*.

A Boolean variable is an abstract numerical quantity that may assume any value
in the set :math:`B = \{0, 1\}`.

For example, if we flip a coin, the result will either be "heads" or "tails".
Let's say we assign tails the value :math:`0`,
and heads the value :math:`1`.
Now divide all of time into two periods: 1) before the flip, and 2) after the flip.

Before you flip the coin,
imagine the possibility of either "tails" (0) or "heads" (1).
The abstract concept in your mind about a coin that may land in one of two ways
is the *variable*.
Normally, we will give the abstract quantity a name to distinguish it from
other abstract quantities we might be simultaneously considering.
The most familiar name for an arbitrary algebraic variable is :math:`x`.

After you flip the coin,
you can see the result in front of you.
The coin flip is no longer an imaginary variable; it is a known constant.

Creating Variable Instances
---------------------------

Let's create a few Boolean expression variables using the ``exprvar`` method::

   >>> a, b, c, d = map(exprvar, 'abcd')
   >>> a.name
   a
   >>> b.name
   b

By default, all variables go into a global namespace.
Also, all variable instances are singletons.
That is, only one variable is allowed to exist per name.
Verify this fact with the following::

   >>> a = exprvar('a')
   >>> _a = exprvar('a')
   >>> id(a) == id(_a)
   True

.. warning::
   We recommend that you never do something crazy like assigning
   ``a`` and ``_a`` to the same variable instance.

Indexing Variables
------------------

   "There are only two hard things in Computer Science: cache invalidation and naming things."

   -- Tim Bray

Consider the coin-flipping example from before.
But this time, instead of flipping one coin, we want to flip a hundred coins.
You could start naming your variables by assigning the first flip to :math:`x`,
followed by :math:`y`, and so on.
But there are only twenty-six letters in the English alphabet,
so unless we start resorting to other alphabets,
we will hit some limitations with this system very quickly.

For cases like these, it is convenient to give variables an *index*.
Then, you can name the variable for the first coin flip :math:`x[0]`,
followed by :math:`x[1]`, :math:`x[2]`, and so on.

Here is how to give variables indices using the ``exprvar`` function::

   >>> x_0 = exprvar('x', 0)
   >>> x_1 = exprvar('x', 1)
   >>> x_0, x_1
   (x[0], x[1])

You can even give variables multiple indices by using a tuple::

   >>> x_0_1_2_3 = exprvar('x', (0, 1, 2 ,3))
   >>> x_0_1_2_3
   x[0][1][2][3]

Assigning individual variables names like this is a bit cumbersome.
It is much easier to just use the ``bitvec`` factory function::

   >>> X = bitvec('x', 8)
   >>> X
   [x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]]
   >>> X[3]
   x[3]
   >>> X[2:5]
   [x[2], x[3], x[4]]
   >>> X[:5]
   [x[0], x[1], x[2], x[3], x[4]]
   >>> X[5:]
   [x[5], x[6], x[7]]
   >>> X[-1]
   x[7]

Similary for multi-dimensional bit vectors::

   >>> X = bitvec('x', 4, 4)
   >>> X.items
   [[x[0][0], x[0][1], x[0][2], x[0][3]],
    [x[1][0], x[1][1], x[1][2], x[1][3]],
    [x[2][0], x[2][1], x[2][2], x[2][3]],
    [x[3][0], x[3][1], x[3][2], x[3][3]]]
   >>> X[2]
   [x[2][0], x[2][1], x[2][2], x[2][3]]
   >>> X[2][2]
   x[2][2]
   >>> X[1:3].items
   [[x[1][0], x[1][1], x[1][2], x[1][3]], [x[2][0], x[2][1], x[2][2], x[2][3]]]
   >>> X[1:3][2]
   [x[2][0], x[2][1], x[2][2], x[2][3]]
   >>> X[2][1:3]
   [x[2][1], x[2][2]]
   >>> X[-1][-1]
   x[3][3]

Points in Boolean Space
=======================

Before we talk about Boolean functions,
it will be useful to discuss the nature of Boolean space.

In high school algebra,
you started with functions that looked like :math:`f(x) = 2x + 3`.
Later, you probably investigated slightly more interesting functions such as
:math:`f(x) = x^2`, :math:`f(x) = sin(x)`, and :math:`f(x) = e^x`.
All of these are functions of a single variable.
That is, the domain of these functions is the set of all values the variable
:math:`x` can take.
In all these cases, that domain is :math:`[-\infty, +\infty]`.

Remember that variables in Boolean algebra can only take values of 0 or 1.
So to create interesting functions in Boolean algebra,
you use many variables.

Let's revisit the coin-flipping example again.
This time we will flip the coin exactly twice.
Create a variable :math:`x` to represent the result of the first flip,
and a variable :math:`y` to represent the result of the second flip.
Use zero (0) to represent "tails", and one (1) to represent "heads".

The number of variables you use is called the "dimension".
All the possible outcomes of this experiment is called the "space".
Each possible outcome is called a "point".

If you flip the coin twice, and the result is (heads, tails),
that result is point :math:`(1, 0)` in a 2-dimensional Boolean space.

Use the ``iter_points`` generator to iterate through all possible points in an
N-dimensional Boolean space::

   >>> list(iter_points([x, y]))
   [{x: 0, y: 0}, {x: 1, y: 0}, {x: 0, y: 1}, {x: 1, y: 1}]

PyEDA uses a dictionary to represent a point.
The keys of the dictionary are the variable instances,
and the values are numbers in :math:`{0, 1}`.

Try doing the experiment with three coin flips.
Use the variable :math:`z` to represent the result of the third flip.

::

   >>> list(iter_points([z, y, x]))
   [{x: 0, y: 0, z: 0},
    {x: 0, y: 0, z: 1},
    {x: 0, y: 1, z: 0},
    {x: 0, y: 1, z: 1},
    {x: 1, y: 0, z: 0},
    {x: 1, y: 0, z: 1},
    {x: 1, y: 1, z: 0},
    {x: 1, y: 1, z: 1}]

The observant reader will notice that this is equivalent to:

* generating all bit-strings of length :math:`N`
* counting from 0 to 7 in the binary number system

Boolean Functions
=================

A Boolean function is a rule that maps every point in an :math:`N`-dimensional
Boolean space to an element in :math:`\{0, 1\}`.

Boolean Function Interface
--------------------------

.. autoclass:: pyeda.boolalg.boolfunc.Function
   :members: __neg__, __add__, __mul__, xor,
             support, usupport, inputs, top, degree, cardinality,
             iter_domain, iter_image, iter_relation,
             restrict, vrestrict, compose,
             satisfy_one, satisfy_all, satisfy_count,
             iter_cofactors, cofactors,
             is_neg_unate, is_pos_unate, is_binate,
             smoothing, consensus, derivative,
             is_zero, is_one,
             box, unbox
   :member-order: bysource

