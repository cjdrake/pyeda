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

Minimize Truth Tables
=====================

An expression is a *completely* specified function.
Sometimes, instead of minimizing an existing expression,
you instead start with only a truth table that maps inputs in :math:`{0, 1}`
to outputs in :math:`{0, 1, *}`, where :math:`*` means "don't care".
For this type of *incompletely* specified function,
you may use the ``espresso_tts`` function to find a lost-cost, equivalent
Boolean expression.

Consider the following truth table with four inputs and two outputs:

==== ==== ==== ====  ==== ====
Inputs               Outputs
-------------------  ---------
 x3   x2   x1   x0    f1   f2
==== ==== ==== ====  ==== ====
0    0    0    0     0    0
0    0    0    1     0    0
0    0    1    0     0    0
0    0    1    1     0    1
0    1    0    0     0    1
0    1    0    1     1    1
0    1    1    0     1    1
0    1    1    1     1    1
1    0    0    0     1    0
1    0    0    1     1    0
1    0    1    0     X    X
1    0    1    1     X    X
1    1    0    0     X    X
1    1    0    1     X    X
1    1    1    0     X    X
1    1    1    1     X    X
==== ==== ==== ====  ==== ====

The ``espresso_tts`` function takes a sequence of input truth table functions,
and returns a sequence of DNF expression instances.

::

   >>> X = bitvec('x', 4)
   >>> f1 = truthtable(X, "0000011111------")
   >>> f2 = truthtable(X, "0001111100------")
   >>> f1m, f2m = espresso_tts(f1, f2)
   >>> f1m
   Or(x[3], And(x[0], x[2]), And(x[1], x[2]))
   >>> f2m
   Or(x[2], And(x[0], x[1]))

You can test whether the resulting expressions are equivalent to the original
truth tables by visual inspection (or some smarter method)::

   >>> expr2truthtable(f1m)
   inputs: x[3] x[2] x[1] x[0]
   0000 0
   0001 0
   0010 0
   0011 0
   0100 0
   0101 1
   0110 1
   0111 1
   1000 1
   1001 1
   1010 1
   1011 1
   1100 1
   1101 1
   1110 1
   1111 1
   >>> expr2truthtable(f2m)
   inputs: x[2] x[1] x[0]
   000 0
   001 0
   010 0
   011 1
   100 1
   101 1
   110 1
   111 1

References
==========

.. [#f1] R. Brayton, G. Hatchel, C. McMullen, and A. Sangiovanni-Vincentelli,
         *Logic Minimization Algorithms for VLSI Synthesis*,
         Kluwer Academic Publishers, Boston, MA, 1984.

