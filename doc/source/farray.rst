.. _farray:

*******************
  Function Arrays
*******************

When dealing with several related Boolean functions,
it is usually convenient to index the inputs and outputs.
For this purpose, PyEDA includes a multi-dimensional array (MDA) data type,
called an ``farray`` (function array).

The most pervasive example is computation involving any numeric data type.
For example, let's say you want to add two numbers :math:`A`, and :math:`B`.
If these numbers are 32-bit integers,
there are 64 total inputs, not including a carry-in.
The conventional way of labeling the input variables is
:math:`a_0, a_1, a_2, \ldots`, and :math:`b_0, b_1, b_2, \ldots`.

Furthermore, you can extend the symbolic algebra of Boolean functions to arrays.
For example, the element-wise XOR or :math:`A` and :math:`B` is also an array 

This chapter will explain how to construct and manipulate arrays of Boolean
functions.
Typical examples will be one-dimensional vectors,
but you can shape your data into several dimensions if you like.
We have purposefully adopted many of the conventions used by the
`numpy.array <http://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html>`_ module.

The code examples in this chapter assume that you have already prepared your
terminal by importing all interactive symbols from PyEDA::

   >>> from pyeda.inter import *

Construction
============

There are three ways to construct ``farray`` instances:

1. Use the ``farray`` class constructor.
2. Use one of the zeros/ones/vars factory functions.
3. Use the unsigned/signed integer conversion functions.

Constructor
-----------

First, create a few expression variables::

   >>> a, b, c, d = map(exprvar, 'abcd')

To store these variables in an array,
invoke the ``farray`` constructor on a sequence::

   >>> vs = farray([a, b, c, d])
   >>> vs
   farray([a, b, c, d])
   >>> vs[2]
   c

Now let's store some arbitrary functions into an array.
Create six expressions using the secondary operators::

   >>> f0 = Nor(a, b, c)
   >>> f1 = Nand(a, b, c)
   >>> f2 = Xor(a, b, c)
   >>> f3 = Xnor(a, b, c)
   >>> f4 = Equal(a, b, c)
   >>> f5 = Unequal(a, b, c)

To neatly store these six functions in an ``farray``,
invoke the constructor like we did before::

   >>> F = farray([f0, f1, f2, f3, f4, f5])
   >>> F
   farray([Nor(a, b, c), Nand(a, b, c), Xor(a, b, c), Xnor(a, b, c), Equal(a, b, c), Unequal(a, b, c)])

This is sufficient for 1-D arrays,
but the ``farray`` constructor can create mult-dimensional arrays as well.
You can apply shape to the input array by either using a nested sequence,
or manually using the *shape* parameter.

To create a 2x3 array using a nested sequence::

   >>> F = farray([[f0, f2, f4], [f1, f3, f5]])
   >>> F
   farray([[Nor(a, b, c), Xor(a, b, c), Equal(a, b, c)],
           [Nand(a, b, c), Xnor(a, b, c), Unequal(a, b, c)]])
   >>> F.shape
   ((0, 2), (0, 3))
   >>> F.size
   6
   >>> F[0,1]
   Xor(a, b, c)

Similarly for a 3x2 array::

   >>> F = farray([[f0, f1], [f2, f3], [f4, f5]])
   >>> F
   farray([[Nor(a, b, c), Nand(a, b, c)],
           [Xor(a, b, c), Xnor(a, b, c)],
           [Equal(a, b, c), Unequal(a, b, c)]])
   >>> F.shape
   ((0, 3), (0, 2))
   >>> F.size
   6
   >>> F[0,1]
   Nand(a, b, c)

Use the *shape* parameter to manually impose a shape.
It takes a tuple of *dimension* specs, which are ``(start, stop)`` tuples.

::

   >>> F = farray([f0, f1, f2, f3, f4, f5], shape=((0, 2), (0, 3)))
   >>> F
   farray([[Nor(a, b, c), Xor(a, b, c), Equal(a, b, c)],
           [Nand(a, b, c), Xnor(a, b, c), Unequal(a, b, c)]])

Irregular Shapes
^^^^^^^^^^^^^^^^

Without the *shape* parameter,
array dimensions will be created with start index zero.
This is fine for most applications,
but in digital design it is sometimes useful to create arrays with irregular
starting points.

For example,
let's say you are designing the load/store unit of a CPU.
A computer's memory is addressed in *bytes*,
but data is accessed from memory in *cache lines*.
If the size of your machine's cache line is 64 bits,
data will be retrieved from memory eight bytes at a time.
The lower 3 bits of the address bus going from the load/store unit to main
memory are not necessary.
Therefore, your load/store unit will output an address with one dimension
bounded by ``(3, 32)``,
i.e. all address bits starting from 3, up to but not including 32.

Going back to the previous example,
let's say for some reason we wanted a shape of ``((7, 9), (13, 16))``.
Just change the *shape* parameter::

   >>> F = farray([f0, f1, f2, f3, f4, f5], shape=((7, 9), (13, 16)))
   >>> F
   farray([[Nor(a, b, c), Xor(a, b, c), Equal(a, b, c)],
           [Nand(a, b, c), Xnor(a, b, c), Unequal(a, b, c)]])

The *size* property is still the same::

   >>> F.size
   6

However, the slices now have different bounds::

   >>> F[7,14]
   Nand(a, b, c)

Factory Functions
-----------------

For convenience,
PyEDA provides factory functions for producing arrays with arbitrary shape
initialized to all zeros, all ones, or all variables with incremental indices.

The functions for creating arrays of zeros are:

* :func:`pyeda.boolalg.bfarray.bddzeros`
* :func:`pyeda.boolalg.bfarray.exprzeros`
* :func:`pyeda.boolalg.bfarray.ttzeros`

For example, to create a 4x4 farray of expression zeros::

   >>> zeros = exprzeros(4, 4)
   >>> zeros
   farray([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]])

The variadic *dims* input is a sequence of dimension specs.
A dimension spec is a two-tuple: (start index, stop index).
If a dimension is given as a single ``int``,
it will be converted to ``(0, stop)``.

For example::

   >>> zeros = bddzeros((1, 3), (2, 4), 2)
   >>> zeros
   farray([[[0, 0],
            [0, 0]],

           [[0, 0],
            [0, 0]]])

Similarly for creating arrays of ones:

* :func:`pyeda.boolalg.bfarray.bddones`
* :func:`pyeda.boolalg.bfarray.exprones`
* :func:`pyeda.boolalg.bfarray.ttones`

The functions for creating arrays of variables are:

* :func:`pyeda.boolalg.bfarray.bddvars`
* :func:`pyeda.boolalg.bfarray.exprvars`
* :func:`pyeda.boolalg.bfarray.ttvars`

These functions behave similarly to the zeros/ones functions,
but take a *name* argument as well.

For example, to create a 4x4 farray of expression variables::

   >>> A = exprvars('a', 4, 4)
   >>> A
   farray([[a[0,0], a[0,1], a[0,2], a[0,3]],
           [a[1,0], a[1,1], a[1,2], a[1,3]],
           [a[2,0], a[2,1], a[2,2], a[2,3]],
           [a[3,0], a[3,1], a[3,2], a[3,3]]])

The *name* argument accepts a tuple of names,
just like the ``exprvar`` function,
and the variadic *dims* input also supports irregular shapes::

   >>> A = exprvars(('a', 'b', 'c'), (1, 3), (2, 4), 2)
   >>> A
   farray([[[c.b.a[1,2,0], c.b.a[1,2,1]],
            [c.b.a[1,3,0], c.b.a[1,3,1]]],

           [[c.b.a[2,2,0], c.b.a[2,2,1]],
            [c.b.a[2,3,0], c.b.a[2,3,1]]]])

Integer Conversion
------------------

The previous section discussed ways to initialize arrays to all zeros or ones.
It is also possible to create one-dimensional arrays that represent integers
using either the unsigned or twos-complement notations.

The following functions convert an unsigned integer to a 1-D ``farray``:

* :func:`pyeda.boolalg.bfarray.uint2bdds`
* :func:`pyeda.boolalg.bfarray.uint2exprs`
* :func:`pyeda.boolalg.bfarray.uint2tts`

The following functions convert a signed integer to a 1-D ``farray``:

* :func:`pyeda.boolalg.bfarray.int2bdds`
* :func:`pyeda.boolalg.bfarray.int2exprs`
* :func:`pyeda.boolalg.bfarray.int2tts`

The signature for these functions are all identical.
The *num* argument is the ``int`` to convert,
and the *length* parameter is optional.
Unsigned conversion will always zero-extend to the provided length,
and signed conversion will always sign-extend.

Here are a few examples of converting integers to expressions::

   >>> uint2exprs(42, 8)
   farray([0, 1, 0, 1, 0, 1, 0, 0])
   >>> int2exprs(42, 8)
   farray([0, 1, 0, 1, 0, 1, 0, 0])
   # A nifty one-liner to verify the previous conversions
   >>> bin(42)[2:].zfill(8)[::-1]
   '01010100'
   >>> int2exprs(-42, 8)
   farray([0, 1, 1, 0, 1, 0, 1, 1])

Function arrays also have ``to_uint`` and ``to_int`` methods to perform the
reverse computation.
They do not, however, have any property to indicate whether the array
represents signed data.
So always know what the encoding is ahead of time.
For example::

   >>> int2exprs(-42, 8).to_int()
   -42
   >>> int2exprs(-42, 8).to_uint()
   214

Slicing
=======

The ``farray`` type accepts two types of slice arguments:

* Integral indices
* Muliplexor selects

Integral Indices
----------------

Function arrays support a slice syntax that mostly follows the numpy ndarray
data type.
The primary difference is that ``farray`` supports nonzero start indices.

To demonstrate the various capabilities, let's create some arrays.
For simplicity, we will only use zero indexing.

::

   >>> A = exprvars('a', 4)
   >>> B = exprvars('b', 4, 4, 4)

Using a single integer index will *collapse* an array dimension.
For 1-D arrays, this means returning an item.

::

   >>> A[2]
   a[2]
   >>> B[2]
   farray([[b[2,0,0], b[2,0,1], b[2,0,2], b[2,0,3]],
           [b[2,1,0], b[2,1,1], b[2,1,2], b[2,1,3]],
           [b[2,2,0], b[2,2,1], b[2,2,2], b[2,2,3]],
           [b[2,3,0], b[2,3,1], b[2,3,2], b[2,3,3]]])
   >>> B[2].shape
   ((0, 4), (0, 4))

The colon ``:`` slice syntax *shrinks* a dimension::

   >>> A[:]
   farray([a[0], a[1], a[2], a[3]])
   >>> A[1:]
   farray([a[1], a[2], a[3]])
   >>> A[:3]
   farray([a[0], a[1], a[2]])
   >>> B[1:3]
   farray([[[b[1,0,0], b[1,0,1], b[1,0,2], b[1,0,3]],
            [b[1,1,0], b[1,1,1], b[1,1,2], b[1,1,3]],
            [b[1,2,0], b[1,2,1], b[1,2,2], b[1,2,3]],
            [b[1,3,0], b[1,3,1], b[1,3,2], b[1,3,3]]],

           [[b[2,0,0], b[2,0,1], b[2,0,2], b[2,0,3]],
            [b[2,1,0], b[2,1,1], b[2,1,2], b[2,1,3]],
            [b[2,2,0], b[2,2,1], b[2,2,2], b[2,2,3]],
            [b[2,3,0], b[2,3,1], b[2,3,2], b[2,3,3]]]])

For N-dimensional arrays,
the slice accepts up to N indices separated by a comma.
Unspecified slices at the end will default to ``:``.

::

   >>> B[1,2,3]
   b[1,2,3]
   >>> B[:,2,3]
   farray([b[0,2,3], b[1,2,3], b[2,2,3], b[3,2,3]])
   >>> B[1,:,3]
   farray([b[1,0,3], b[1,1,3], b[1,2,3], b[1,3,3]])
   >>> B[1,2,:]
   farray([b[1,2,0], b[1,2,1], b[1,2,2], b[1,2,3]])
   >>> B[1,2]
   farray([b[1,2,0], b[1,2,1], b[1,2,2], b[1,2,3]])

The ``...`` syntax will fill available indices left to right with ``:``.
One one ellipsis will be recognized per slice.

::

   >>> B[...,1]
   farray([[b[0,0,1], b[0,1,1], b[0,2,1], b[0,3,1]],
           [b[1,0,1], b[1,1,1], b[1,2,1], b[1,3,1]],
           [b[2,0,1], b[2,1,1], b[2,2,1], b[2,3,1]],
           [b[3,0,1], b[3,1,1], b[3,2,1], b[3,3,1]]])
   >>> B[1,...]
   farray([[b[1,0,0], b[1,0,1], b[1,0,2], b[1,0,3]],
           [b[1,1,0], b[1,1,1], b[1,1,2], b[1,1,3]],
           [b[1,2,0], b[1,2,1], b[1,2,2], b[1,2,3]],
           [b[1,3,0], b[1,3,1], b[1,3,2], b[1,3,3]]])

Function arrays support negative indices.
Arrays with a zero start index follow Python's usual conventions.

For example, here is the index guide for ``A[0:4]``::

    +------+------+------+------+
    | a[0] | a[1] | a[2] | a[3] |
    +------+------+------+------+
    0      1      2      3      4
   -4     -3     -2     -1

And example usage::

   >>> A[-1]
   a[3]
   >>> A[-3:-1]
   farray([a[1], a[2]])

Arrays with non-zero start indices also support negative indices.
For example, here is the index guide for ``A[3:7]``::

    +------+------+------+------+
    | a[3] | a[4] | a[5] | a[6] |
    +------+------+------+------+
    3      4      5      6      7
   -4     -3     -2     -1

Multiplexor Selects
-------------------

A special feature of array slicing is the ability to multiplex array
items over a select input.
For a 2:1 mux, the *select* may be a single function.
Otherwise, it must be an ``farray`` with enough bits.

For example, to create a simple 8:1 mux::

   >>> X = exprvars('x', 8)
   >>> sel = exprvars('s', 3)
   >>> X[sel]
   Or(And(~s[0], ~s[1], ~s[2], x[0]),
      And( s[0], ~s[1], ~s[2], x[1]),
      And(~s[0],  s[1], ~s[2], x[2]),
      And( s[0],  s[1], ~s[2], x[3]),
      And(~s[0], ~s[1],  s[2], x[4]),
      And( s[0], ~s[1],  s[2], x[5]),
      And(~s[0],  s[1],  s[2], x[6]),
      And( s[0],  s[1],  s[2], x[7]))

This works for multi-dimensional arrays as well::

   >>> s = exprvar('s')
   >>> Y = exprvars('y', 2, 2, 2)
   >>> Y[:,s,:]
   farray([[Or(And(~s, y[0,0,0]),
               And( s, y[0,1,0])),
            Or(And(~s, y[0,0,1]),
               And( s, y[0,1,1]))],

           [Or(And(~s, y[1,0,0]),
               And( s, y[1,1,0])),
            Or(And(~s, y[1,0,1]),
               And( s, y[1,1,1]))]])

Unary Operators
===============

uor, unor, uand, unand, uxor, uxnor

Bit-wise Operators
==================

invert, or, and, xor, lsh, rsh, arsh

Concatenation and Repetition
============================

todo

