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
To each his own. |smiley|

A *Boolean* algebra defines the rules for working with the set :math:`\{0, 1\}`.
So unlike in normal algebra class where you have more numbers than you can
possibly imagine, in Boolean Algebra you only have two.

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

Additional Perspective
----------------------

You are probably thinking this is all very nice,
but what can you possibly do with an algebra that only concerns itself with
0, 1, *NOT*, *OR*, and *AND*?

In 1937, `Claude Shannon <http://en.wikipedia.org/wiki/Claude_Shannon>`_
realized that electronic circuits have two-value switches that can be combined
into networks capable of solving any logical or numeric relationship.
A transistor is nothing but an electrical switch.
Similar to a light bulb, it has two states: off (0), and on (1).
Wiring transistors together in serial imitates the *AND* function,
and wiring them together in parallel imitates the *OR* function.
If you wire a few thousand transistors together in interesting ways,
you can build a computer.


Import Symbols from PyEDA
=========================

All examples in this document require that you execute the following statements
in your interpreter::

   >>> from pyeda import *

If you want to see all the symbols you import with this statement,
look into ``pyeda/__init__.py``.

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

Let's create a few Boolean variables using the ``var`` convenience method::

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

Get All Alphabetic Variables
----------------------------

For convenience, you can just import all of the single-letter variable
instances from the ``pyeda.alphas`` module::

   >>> from pyeda.alphas import *
   >>> a, b, c
   (a, b, c)

Indexing Variables
------------------

   "There are only two hard things in Computer Science: cache invalidation and naming things."

   -- Tim Bray

In the coin-flipping example you could start naming your variables by assigning
the first flip to :math:`x`, followed by :math:`y`, and so on.
But there are only twenty-six letters in the English alphabet,
so unless we start resorting to other alphabets,
we will hit some limitations with this system very quickly.

For cases like these, it is convenient to give variables an *index*.
Then, you can name the variable for the first coin flip :math:`x[0]`,
followed by :math:`x[1]`, :math:`x[2]`, and so on.

Here is how to give variables indices using the ``var`` function::

   >>> x_0 = var('x', 0)
   >>> x_1 = var('x', 1)
   >>> x_0, x_1
   (x[0], x[1])

You can even give variables multiple indices by using a tuple::

   >>> x_0_1_2_3 = var('x', (0, 1, 2 ,3))
   >>> x_0_1_2_3
   x[0][1][2][3]

Ordering Variables
------------------

In order to provide a canonical representation, all variables are ordered.

The rules for ordering variables are:

* If both variables have the same name,
  perform a tuple comparison of their indices
* Otherwise, do a string compare of their names

For example::

   >>> a < b
   True
   >>> a < q < w
   True

   # x_0 == x[0]
   # x_1 == x[1]
   # x_10 == x[10]
   >>> a < x_0
   True
   >>> x_0 < x_1
   True
   >>> x_1 < x_10
   True


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
This time we will flip the coin twice.
Create a variable :math:`x` to represent the result of the first flip,
and a variable :math:`y` to represent the result of the second flip.
Use zero (0) to represent "tails", and one (1) to represent "heads".

The number of variables you use is called the "dimension".
All the possible outcomes of this experiment is called the "space".
Each possible outcome is called a "point".

If you flip the coin twice, and the result is "heads", "tails",
that result is point :math:`(1, 0)` in a 2-dimensional Boolean space.

Use the ``iter_points`` generator to iterate through all possible points in an
N-dimensional Boolean space::

   >>> [point for point in iter_points([x, y])]
   [{x: 0, y: 0}, {x: 1, y: 0}, {x: 0, y: 1}, {x: 1, y: 1}]

PyEDA uses a dictionary to represent a point.
The keys of the dictionary are the variable instances,
and the values are numbers in :math:`{0, 1}`.

Try doing the experiment with three coin flips.
Use the variable :math:`z` to represent the result of the third flip.

::

   >>> [point for point in iter_points([z, y, x])]
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

.. autoclass:: pyeda.boolfunc.Function
   :members: __neg__, __add__, __mul__, xor,
             support, inputs, top, degree, cardinality,
             iter_domain, iter_image, iter_relation,
             restrict, urestrict, vrestrict, compose,
             satisfy_one, satisfy_all, satisfy_count,
             iter_cofactors, cofactors,
             smoothing, consensus, derivative,
             is_zero, is_one,
             box, unbox
   :member-order: bysource
