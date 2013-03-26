.. boolalg.rst

.. |smiley| unicode:: 0x263A

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

We don't even assume you know what Boolean Algebra is;
so let's define it now.

What is Boolean Algebra?
========================

All great stories have a beginning, so let's start with the basics.
You probably took a class called "algebra" in high school.
So when you started reading this document you were already confused.
Algebra is just algebra, right?
You solve for :math:`X`, find the intersection of two lines,
and you're done, right?

As it turns out,
the algebra you are probably already familiar with is just scratching the
surface.
An algebra is the combination of two things:

1. a collection of mathematical objects, and
2. a collection of rules to manipulate those objects

For example, in your familiar algebra, you have numbers such as
:math:`\{1, 3, 5, \frac{1}{2}, .337\}`, and operators such as
:math:`\{+, -, \cdot, \div\}`.
The numbers are the mathematics objects,
and the operators are the rules for how to manipulate them.
Except in very extreme circumstances (division by zero),
whenever you add, subtract, or divide two numbers, you get another number.

Algebras are a big part of the "tools of the trade" for a mathematician.
A plumber has pipes and wrenches, a carpenter has wood and saws,
and a mathematician has algebras.
To each his own. |smiley|

A *Boolean* algebra defines the rules for working with the set :math:`\{0, 1\}`.
So unlike in normal algebra class where you have more numbers than you can
possibly imagine, in Boolean Algebra you only have two.
Only two numbers? This is starting to sound pretty awesome.
Wait, it gets better.

Even though it is possible to define a Boolean Algebra using different
operators,
by far the most common operators are complement, sum, and product.

The complement, denoted with an overline (:math:`\overline{x}`),
the :math:`\neg` symbol, or *NOT*, is defined by:

.. math::

   \overline{0} = 1

   \overline{1} = 0

The sum (or disjunction), denoted with the :math:`+` symbol,
:math:`\vee` symbol, or *OR*,
is defined by:

.. math::

   0 + 0 = 0

   0 + 1 = 1

   1 + 0 = 1

   1 + 1 = 1

The product (or conjunction), denoted with the :math:`\cdot` symbol,
:math:`\wedge`, or *AND*,
is defined by:

.. math::

   0 \cdot 0 = 0

   0 \cdot 1 = 0

   1 \cdot 0 = 0

   1 \cdot 1 = 1

So you are telling me that in Boolean algebra there are only two numbers you
need to know about, and three operators?
And people get paid to do this?

For basic manipulations involving constant values,
the Python interpreter has all the built-in functionality we need.

Built-in Python Boolean Operations
==================================

Python has a built-in Boolean data type, ``bool``.
You can think of the ``False`` keyword as an alias for the number zero,
and the ``True`` keyword as an alias for the number one.

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

Import Symbols from PyEDA
=========================

All examples in this document require that you execute the following statement
in your interpreter::

   >>> from pyeda import *

This is generally frowned upon for Python programming,
but *extremely* convenient for interactive use.
If you want to see all the symbols you import with this statement,
look into ``pyeda/__init__.py``.

Boolean Variables and Functions
===============================

Okay, so we already know what Boolean Algebra is,
and Python can do everything we need already, right?

Just like in your algebra class,
things start to get interesting when we introduce a few *variables*.

A Boolean variable is a numerical quantity that may assume any value in the
set :math:`B = \{0, 1\}`.

Let's create a few Boolean variables using the ``var`` method:

::

   >>> a, b = map(var, 'ab')
   >>> a.name
   a
   >>> b.name
   b

By default, all variables go into a global namespace.
Also, variables are singletons.
That is, only one variable is allowed to exist per name.
Verify this fact with the following::

   >>> a = var('a')
   >>> b = var('a')
   >>> id(a) == id(b)
   True

.. warning::
   We recommend that you never do something crazy like assigning ``a`` and
   ``b`` to the same variable instance.

If you want to create namespaces for your variables,
use the ``namespace`` parameter::

   >>> eggs = var('eggs', namespace='spam')
   >>> str(eggs)
   spam.eggs

Variable Indices
----------------

Sometimes, a variable is part of a related group of variables.
For example, let's say you flip a coin four times.
Instead of using ``a`` to represent the first flip,
``b`` for the second flip, and so on,
we can use a single variable name with an index.
Let the first flip be ``x[0]``
(because in programming we always start with index zero),
second flip ``x[1]``, etc.

::

   >>> x0 = var('x', indices=(0, ))
   >>> x1 = var('x', indices=(1, ))
   >>> x2 = var('x', indices=(2, ))
   >>> x3 = var('x', indices=(3, ))
   >>> (x0, x1, x2, x3)
   (x[0], x[1], x[2], x[3])

As it turns out, we can actually do a lot better with the ``bitvec`` function::

   >>> x = bitvec('x', 4)
   >>> x[0]
   x[0]
   >>> x[1:3]
   [x[1], x[2]]
   >>> x
   [x[0], x[1], x[2], x[3]]

This function is actually much more powerful than this.
It can deftly produce multi-dimensional arrays of variables with few keystrokes,
but we will save the details of that for the section of bit vectors.

Logical Expressions
===================

Let's define a simple Boolean function: :math:`F(x, y, z) = x * y + -z`

::

   # Create three Boolean variables
   >>> x, y, z = map(var, 'xyz')

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
