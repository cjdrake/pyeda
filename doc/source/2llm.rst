.. _2llm:

********************************
  Two-level Logic Minimization
********************************

This chapter will explain how to use PyEDA to minimize two-level
"sum-of-products" forms of Boolean functions.

Logic minimization is known to be an NP-complete problem.
It is equivalent to finding a minimal-cost set of subsets of a set :math:`S`
that *covers* :math:`S`.
This is sometimes called the "paving problem",
because it is conceptually similar to finding the cheapest configuration of
tiles that cover a floor.
Due to the complexity of this operation,
PyEDA uses a C extension to the famous Berkeley Espresso library [#f1]_.

All examples in this chapter assume you have interactive symbols imported::

   >>> from pyeda.inter import *

Minimize Boolean Expressions
============================

Consider the three-input function
:math:`f_{1} = a \cdot b' \cdot c' + a' \cdot b' \cdot c + a \cdot b' \cdot c + a \cdot b \cdot c + a \cdot b \cdot c'`

::

   >>> a, b, c = map(exprvar, 'abc')
   >>> f1 = ~a & ~b & ~c | ~a & ~b & c | a & ~b & c | a & b & c | a & b & ~c

To use Espresso to perform minimization::

   >>> f1m, = espresso_exprs(f1)
   >>> f1m
   Or(And(~a, ~b), And(a, b), And(~b, c))

Notice that the ``espresso_exprs`` function returns a tuple.
The reason is that this function can minimize multiple input functions
simultaneously.
To demonstrate, let's create a second function
:math:`f_{2} = a' \cdot b' \cdot c + a \cdot b' \cdot c`.

::

   >>> f2 = ~a & ~b & c | a & ~b & c
   >>> f1m, f2m = espresso_exprs(f1, f2)
   >>> f1m
   Or(And(~a, ~b), And(a, b), And(~b, c))
   >>> f2m
   And(~b, c)

It's easy to verify that the minimal functions are equivalent to the originals::

   >>> f1.equivalent(f1m)
   True
   >>> f2.equivalent(f2m)
   True

.. [#f1] R. Brayton, G. Hatchel, C. McMullen, and A. Sangiovanni-Vincentelli,
         *Logic Minimization Algorithms for VLSI Synthesis*,
         Kluwer Academic Publishers, Boston, MA, 1984.

