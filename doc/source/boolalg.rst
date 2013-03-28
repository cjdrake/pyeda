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

What is Boolean Algebra?
========================

All great stories have a beginning, so let's start with the basics.
You probably took a class called "algebra" in (junior) high school.
So when you started reading this document you were already confused.
Algebra is just algebra, right?
You solve for :math:`x`, find the intersection of two lines,
and you're done, right?

As it turns out,
the algebra you are familiar with just scratches the surface.
There are many algebras with equally many theoretical and practical uses.
An algebra is the combination of two things:

1. a collection of mathematical objects, and
2. a collection of rules to manipulate those objects

For example, in your familiar algebra, you have numbers such as
:math:`\{1, 3, 5, \frac{1}{2}, .337\}`, and operators such as
:math:`\{+, -, \cdot, \div\}`.
The numbers are the mathematical objects,
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

This looks familiar so far except for the :math:`1 + 1 = 1` part.
The Boolean sum is called *OR* because the output of :math:`a` *OR* :math:`b`
equals 1 *if and only if* :math:`a = 1`, or :math:`b = 1`, or both.

The product (or conjunction), denoted with the :math:`\cdot` symbol,
:math:`\wedge`, or *AND*,
is defined by:

.. math::

   0 \cdot 0 = 0

   0 \cdot 1 = 0

   1 \cdot 0 = 0

   1 \cdot 1 = 1

The Boolean product is called *AND* because the output of :math:`a` *AND*
:math:`b` equals 1 *if and only if* both :math:`a = 1`, and :math:`b = 1`.

So you are telling me that in Boolean algebra there are only two numbers you
need to know about, and only three operators?
Not exactly.
There are many other significant operators,
but they may all be reduced to these fundamental three.

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

Import Symbols from PyEDA
=========================

All examples in this document require that you execute the following statement
in your interpreter::

   >>> from pyeda import *

This is generally frowned upon for Python programming,
but *extremely* convenient for interactive use.
If you want to see all the symbols you import with this statement,
look into ``pyeda/__init__.py``.

Boolean Variables
=================

Okay, so we already know what Boolean Algebra is,
and Python can do everything we need already, right?

Just like in your algebra class,
things start to get interesting when we introduce a few *variables*.

A Boolean variable is a numerical quantity that may assume any value in the
set :math:`B = \{0, 1\}`.

To put it another way,
a *variable* is a handy label for a concept in the mind of its author.
For example, if we flip a coin, the result will either be "heads" or "tails".
Let's say we assign "tails" the value 0, and "heads" the value 1.
Before we flip the coin,
the face the coin will ultimately show is unknown.
We could call this idea ``flip_result``,
or just :math:`x` if we are going for brevity.
Before the coin is flipped, its final result may *vary*,
and is therefore referred to as a *variable*.
After the coin is flipped, the result is a constant.

Creating Variable Instances
---------------------------

Let's create a few Boolean variables using the ``var`` convenience method:

::

   >>> a, b, c, d = map(var, 'abcd')
   >>> a.name
   a
   >>> b.name
   b

By default, all variables go into a global namespace.
Also, all variable instances are singletons.
That is, only one variable is allowed to exist per name.
Verify this fact with the following::

   >>> a = var('a')
   >>> b = var('a')
   >>> id(a) == id(b)
   True

.. warning::
   We recommend that you never do something crazy like assigning :math:`a` and
   :math:`b` to the same variable instance.

If you want to put your variables into a separate namespaces,
use the ``namespace`` parameter::

   >>> eggs1 = var('eggs', namespace='ham')
   >>> eggs2 = var('eggs', namespace='spam')
   >>> str(eggs1)
   ham.eggs
   >>> str(eggs2)
   spam.eggs
   >>> id(eggs1) == id(eggs2)
   False

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
In all these cases, that domain is :math:`[-\infty, +\infty]`

Remember that variables in Boolean algebra can only take values of 0 or 1.
So to create interesting functions in Boolean algebra,
you use many variables.

Let's revisit the coin-flipping example from before.
You create a variable :math:`x` to represent the result of the first flip,
and a variable :math:`y` to represent the result of the second flip.
You use 0 to represent a "tails" result, and 1 to represent a "heads" result.

The number of variables you use is called the "dimension".
All the possible outcomes of this experiment is called the "space".
Each possible outcome is called a "point".

So let's put it all together.
If you flip the coin twice, and the result is "heads", "tails",
that result is point :math:`(1, 0)` in a 2-dimensional Boolean space.

Use the ``iter_space`` iterator to iterate through all possible points in an
N-dimensional Boolean space::

   >>> x, y = map(var, 'xy')
   >>> [ p for p in iter_space([x, y]) ]
   [{x: 0, y: 0}, {x: 1, y: 0}, {x: 0, y: 1}, {x: 1, y: 1}]

The return value is a dictionary.
The key is the variable instance, and the value is in :math:`{0, 1}`.

Try doing the experiment with three coin flips.
Use the variable :math:`z` to represent the result of the third flip.

::

   >>> x, y, z = map(var, 'xyz')

   # Put 'z' in the least-significant position
   >>> [ p for p in iter_space([z, y, x]) ]
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

Truth Tables
============

Logical Expressions
===================
