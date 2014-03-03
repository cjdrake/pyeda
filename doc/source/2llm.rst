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
you may use the ``espresso_tts`` function to find a low-cost, equivalent
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

Espresso Script
===============

Starting with version ``0.20``, PyEDA includes a script that implements some
of the functionality of the original Espresso command-line utility.

.. code-block:: sh

   $ espresso -h
   usage: espresso [-h] [-e {fast,ness,nirr,nunwrap,onset,strong}] [--fast]
                   [--no-ess] [--no-irr] [--no-unwrap] [--onset] [--strong]
                   [file]

   Minimize a PLA file

   positional arguments:
     file                  PLA file (default: stdin)

   optional arguments:
     -h, --help            show this help message and exit
     ...

Here is an example of a simple PLA file that is part of the BOOM benchmark suite.
This function has 50 input variables, 5 output variables, and 50 product terms.
Also, 20% of the literals in the implicants are "don't care".

.. code-block:: sh

   $ cat extension/espresso/test/bb_all/bb_50x5x50_20%_0.pla
   .i 50
   .o 5
   .p 50
   .ilb x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17 x18 x19 x20 x21 x22 x23 x24 x25 x26 x27 x28 x29 x30 x31 x32 x33 x34 x35 x36 x37 x38 x39 x40 x41 x42 x43 x44 x45 x46 x47 x48 x49
   .ob y0 y1 y2 y3 y4
   .type fr
   001011110--00--0100-0010-10-01010101-010--01011111 00011
   0-1-1010-01000100--11011-0110001010-10001010-1-1-0 00100
   0111010111110110110-100101101010010001111----1-011 10000
   01-0010011-001110--000-011--11--1-0100-01101--1000 00001
   001011010-1100000001101--10100-010-001100111110010 00101
   011-01010-10-1101110-00-1-11001-1-0000--1-1-00-000 00011
   0000000011001-0000010-000110-11011001110--100-1-10 00110
   00-111111-00100-100111101000-11101100--0-1110-1-10 10001
   -1-10011011000011--00-0011011101-1-1101110--1-001- 11100
   -0101100-110111-010-01110-0110011-1-1---1001011111 11000
   0-111011101000-11-1--10-0001001101000010-11-111101 11001
   11000000-1-01--1111-10111111----0010--1-0--1--0111 01010
   00-101000011-1-10101101-1101011-0101000-111111011- 11011
   1-00-11111-0010-0---000--0110-0010111--000001-0001 11011
   -1-1100100001--00--00001000-1-1--100-0111-00011011 11000
   0-0000-010-11-1100-101-00101000111-01--11-0010-011 10000
   11-1-0001100101-10-0-1-0-1100010101111-1111000-101 11101
   10-01--10011111-11011-001001101100110010010-000-0- 01110
   1-11010-00011101-010--101010--0111010101-11-101--1 00111
   11--111-111-111-000-11000-101-1-011--1000--1111100 01111
   0---0-10011101000--11001-1100-10-000011-0100011100 11110
   -01--11-010-1001011-0-101000100000--10111---100-1- 11101
   11-1-000010--00110-011101--11-10-1-0000110100-1101 11010
   -0111110-100-11-110001001100001-100011110001001100 11110
   11--00100-01--00-10---11-0001-00011101001011-01110 00000
   1--010011-001-0000--0-11-001010001110-00-01-110-11 01101
   100011--0101--1-1-0-101--001-0-101-1-1011101011-01 00111
   0--0-01-10101-11-0100111111000-1-1011100-111-01111 10100
   0-0110010--11101-0---1001-1001--001-110000---1011- 00100
   0-1000-0--00000010-0--1011-1001011-01-00-011001111 10000
   111-1101111-01001101-111--00-01011111000001-001001 11100
   0--100111-1010001-0111-0-000--00-0111101111-101100 11000
   00001101100-001001-1010010010011-1101-110-10-110-1 01011
   0101-01-0100101000010111--0011-0011011110-111100-0 00100
   000-1--100-00-1001-10-000000100-001100-10101010001 10000
   10001001-0001011-1-1-0-00101110-10100---0010001--- 10111
   01011000000100100000---1--11-0001011111101-01-1011 01111
   1--01--00100110001-110-0-00001011---01001000110--- 10010
   0-0001--01--11101010100000000010011001000-01100001 00011
   0-0100110-00111100-001--11--00-1001-00-0-11-1-0-1- 00100
   101-1-100-001001-010111-01--010-1-1011-01101001001 11000
   0110-111011--1-010101-011-1-00100110-00-1111000-11 11001
   011001011---010011-10-00-11-001000000101101101-0-1 00100
   1001111-1-1111-1001-000111010-100--0111110011000-1 10111
   1-1010-1-100111110010-101011-1001000111-0000--11-1 11000
   -00110001000010000010100010010-0-0-100-1-0111011-1 00101
   1110-01100111111-1-1-110-0-110--011--01-11-0000-01 00000
   -01010101010-1-1-00-1111010100-1001111110110--0-00 11011
   110-10000001--0-0-01001111-0011-0110110100010--111 11111
   101-10111000011110000-1001-001-01111-011-0001-0100 00100
   .e

After running the input file through the ``espresso`` script,
it minimizes the function to 26 implicants with significantly fewer literals.

.. code-block:: sh

   $ espresso extension/espresso/test/bb_all/bb_50x5x50_20%_0.pla
   .i 50
   .o 5
   .ilb x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17 x18 x19 x20 x21 x22 x23 x24 x25 x26 x27 x28 x29 x30 x31 x32 x33 x34 x35 x36 x37 x38 x39 x40 x41 x42 x43 x44 x45 x46 x47 x48 x49
   .ob y0 y1 y2 y3 y4
   .p 26
   ----------------------0-----1---0------0---------- 01110
   ------0-----------------------------1-----1--0--0- 11100
   ---------------------------1--------1---0------0-- 01011
   -------------------------------------11-1--------1 10000
   0-------------------------1---------1-1----------- 00110
   --------0--------1----------0-------0------------- 00010
   -------------0---------0-0-0--------------------1- 10001
   --------------0-00------------------0-------1----- 00101
   --------------------------0-0---0---------0------- 00011
   -----------0----0-------------------------0---0--- 10000
   -------------------------1---0---1---------------1 10000
   -----------01-----------------------------0---1--1 11000
   -------------00------------------------11--------- 11000
   ----------------------------0-1---------0-0---1--- 11110
   --------------------------1----1--0------------1-- 00100
   -----1-----------------------------1-1---1-------- 00111
   ------1---------------0-------1--1---0------------ 11001
   ------0----0------------------------------1-1-0--- 01000
   -1---1--------1----------------------------------0 00001
   -----------------1----------------------0-----0-1- 01010
   --------------------0--------1---------1------0--- 00100
   ---------------------------11-------------1-0-1--- 10010
   --------------------------1-----0----10----------- 00100
   ------0------0---------0---------0-----------0---- 00101
   -------0----------0---1--1--0---0----------------- 11011
   --------------------0-----------0-----------1-0--- 00100
   .e

References
==========

.. [#f1] R. Brayton, G. Hatchel, C. McMullen, and A. Sangiovanni-Vincentelli,
         *Logic Minimization Algorithms for VLSI Synthesis*,
         Kluwer Academic Publishers, Boston, MA, 1984.

