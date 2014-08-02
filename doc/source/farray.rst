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
For example, the element-wise XOR of :math:`A` and :math:`B` is also an array 

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

Internally, function arrays are stored in a flat list.
You can retrieve the items by using the *flat* iterator::

   >>> list(F.flat)
   [Nor(a, b, c),
    Nand(a, b, c),
    Xor(a, b, c),
    Xnor(a, b, c),
    Equal(a, b, c),
    Unequal(a, b, c)]

Use the *reshape* method to return a new ``farray`` with the same contents and
size,
but with different dimensions::

   >>> F.reshape(3, 2)
   farray([[Nor(a, b, c), Nand(a, b, c)],
           [Xor(a, b, c), Xnor(a, b, c)],
           [Equal(a, b, c), Unequal(a, b, c)]])

Empty Arrays
^^^^^^^^^^^^

It is possible to create an empty ``farray``,
but only if you supply the *ftype* parameter.
That parameter is not necessary for non-empty arrays,
because it can be automatically determined.

For example::

   >>> empty = farray([], ftype=Expression)
   >>> empty
   farray([])
   >>> empty.shape
   ((0, 0),)
   >>> empty.size
   0

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

   >>> F.shape
   ((7, 9), (13, 16))
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
Only one ellipsis will be recognized per slice.

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

Operators
=========

Function arrays support several operators for algebraic manipulation.
Some of these operators overload Python's operator symbols.
This section will describe how you can use the ``farray`` data type and the
Python interpreter to perform powerful symbolic computations.

Unary Reduction
---------------

A common operation is to reduce the entire contents of an array to a single
function.
This is supported by the OR, AND, and XOR operators because they are
1) variadic, and 2) associative.

Unfortunately, Python has no appropriate symbols available,
so unary operators are supported by the following ``farray`` methods:

* :meth:`pyeda.boolalg.bfarray.farray.uor`
* :meth:`pyeda.boolalg.bfarray.farray.unor`
* :meth:`pyeda.boolalg.bfarray.farray.uand`
* :meth:`pyeda.boolalg.bfarray.farray.unand`
* :meth:`pyeda.boolalg.bfarray.farray.uxor`
* :meth:`pyeda.boolalg.bfarray.farray.uxnor`

For example, to OR the contents of an eight-bit array::

   >>> X = exprvars('x', 8)
   >>> X.uor()
   Or(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])

One well-known usage of unary reduction is conversion from a binary-reflected
gray code (BRGC) back to binary.
In the following example, ``B`` is a 3-bit array that contains logic to convert
the contents of ``G`` from gray code to binary.
See the Wikipedia `Gray Code <http://en.wikipedia.org/wiki/Gray_code>`_
article for background.

::

   >>> G = exprvars('g', 3)
   >>> B = farray([G[i:].uxor() for i, _ in enumerate(G)])
   >>> graycode = ['000', '100', '110', '010', '011', '111', '101', '001']
   >>> for gs in graycode:
   ...     print(B.vrestrict({X: gs}).to_uint())
   0
   1
   2
   3
   4
   5
   6
   7

Bit-wise Logic
--------------

Arrays are an algebraic data type.
They overload several of Python's operators to perform bit-wise logic.

First, let's create a few arrays::

   >>> A = exprvars('a', 4)
   >>> B = exprvars('b', 4)
   >>> C = exprvars('c', 2, 2)
   >>> D = exprvars('d', 2, 2)

To invert the contents of ``A``::

   >>> ~A
   farray([~a[0], ~a[1], ~a[2], ~a[3]])

Inverting a multi-dimensional array will retain its shape::

   >>> ~C
   farray([[~c[0,0], ~c[0,1]],
           [~c[1,0], ~c[1,1]]])

The binary OR, AND, and XOR operators work for arrays with equal size::

   >>> A | B
   farray([Or(a[0], b[0]), Or(a[1], b[1]), Or(a[2], b[2]), Or(a[3], b[3])])
   >>> A & B
   farray([And(a[0], b[0]), And(a[1], b[1]), And(a[2], b[2]), And(a[3], b[3])])
   >>> C ^ D
   farray([[Xor(c[0,0], d[0,0]), Xor(c[0,1], d[0,1])],
           [Xor(c[1,0], d[1,0]), Xor(c[1,1], d[1,1])]])

Mismatched sizes will raise an exception::

   >>> A & B[2:]
   Traceback (most recent call last):
       ...
   ValueError: expected operand sizes to match

For arrays of the same size but different shape,
the resulting shape is ambiguous so by default the result is flattened::

   >>> Y = ~A | C
   >>> Y
   farray([Or(~a[0], c[0,0]), Or(~a[1], c[0,1]), Or(~a[2], c[1,0]), Or(~a[3], c[1,1])])
   >>> Y.size
   4
   >>> Y.shape
   ((0, 4),)

Shifts
------

Function array have three shift methods:

* :meth:`pyeda.boolalg.bfarray.farray.lsh`: logical left shift
* :meth:`pyeda.boolalg.bfarray.farray.rsh`: logical right shift
* :meth:`pyeda.boolalg.bfarray.farray.arsh`: arithmetic right shift

The logical left/right shift operators shift out *num* items from the array,
and optionally shift in values from a *cin* (carry-in) parameter.
The output is a two-tuple of the shifted array, and the "carry-out".

The "left" direction in ``lsh`` shifts towards the most significant bit.
For example::

   >>> X = exprvars('x', 8)
   >>> X.lsh(4)
   (farray([0, 0, 0, 0, x[0], x[1], x[2], x[3]]),
    farray([x[4], x[5], x[6], x[7]]))
   >>> X.lsh(4, exprvars('y', 4))
   (farray([y[0], y[1], y[2], y[3], x[0], x[1], x[2], x[3]]),
    farray([x[4], x[5], x[6], x[7]]))

Similarly,
the "right" direction in ``rsh`` shifts towards the least significant bit.
For example::

   >>> X.rsh(4)
   (farray([x[4], x[5], x[6], x[7], 0, 0, 0, 0]),
    farray([x[0], x[1], x[2], x[3]]))
   >>> X.rsh(4, exprvars('y', 4))
   (farray([x[4], x[5], x[6], x[7], y[0], y[1], y[2], y[3]]),
    farray([x[0], x[1], x[2], x[3]]))

You can use the Python overloaded ``<<`` and ``>>`` operators for ``lsh``,
and ``rsh``, respectively.
The only difference is that they do not produce a carry-out.
For example::

   >>> X << 4
   farray([0, 0, 0, 0, x[0], x[1], x[2], x[3]])
   >>> X >> 4
   farray([x[4], x[5], x[6], x[7], 0, 0, 0, 0])

Using a somewhat awkward ``(num, farray)`` syntax,
you can use these operators with a carry-in.
For example::

   >>> X << (4, exprvars('y', 4))
   farray([y[0], y[1], y[2], y[3], x[0], x[1], x[2], x[3]])
   >>> X >> (4, exprvars('y', 4))
   farray([x[4], x[5], x[6], x[7], y[0], y[1], y[2], y[3]])

An *arithmetic* right shift automatically sign-extends the array.
Therefore, it does not take a carry-in.
For example::

   >>> X.arsh(4)
   (farray([x[4], x[5], x[6], x[7], x[7], x[7], x[7], x[7]]),
    farray([x[0], x[1], x[2], x[3]]))

Due to its importance in digital design,
Verilog has a special ``>>>`` operator for an arithmetic right shift.
Sadly, Python has no such indulgence.
If you really want to use a symbol,
you can use the *cin* parameter to achieve the same effect with ``>>``::

   >>> num = 4
   >>> X >> (num, num * X[-1])
   farray([x[4], x[5], x[6], x[7], x[7], x[7], x[7], x[7]])

Concatenation and Repetition
----------------------------

Two very important operators in hardware description languages are
concatenation and repetition of logic vectors.
For example,
in this implementation of the ``xtime`` function from the AES standard,
``xtime[6:0]`` is concatenated with ``1'b0``,
and ``xtime[7]`` is repeated eight times before being AND'ed with ``8'h1b``.

.. code-block:: verilog

   function automatic logic [7:0]
   xtime(logic [7:0] b, int n);
       xtime = b;
       for (int i = 0; i < n; i++)
           xtime = {xtime[6:0], 1'b0}       // concatenation
                 ^ (8'h1b & {8{xtime[7]}}); // repetition
   endfunction

The ``farray`` data type resembles the Python ``tuple`` for these operations.

To concatenate two arrays, use the ``+`` operator::

   >>> X = exprvars('x', 4)
   >>> Y = exprvars('y', 4)
   >>> X + Y
   farray([x[0], x[1], x[2], x[3], y[0], y[1], y[2], y[3]])

It is also possible to prepend or append single functions::

   >>> a, b = map(exprvar, 'ab')
   >>> a + X
   farray([a, x[0], x[1], x[2], x[3]])
   >>> X + b
   farray([x[0], x[1], x[2], x[3], b])
   >>> a + X + b
   farray([a, x[0], x[1], x[2], x[3], b])
   >>> a + b
   farray([a, b])

Even ``0`` (or ``False``) and ``1`` (or ``True``) work::

   >>> 0 + X
   farray([0, x[0], x[1], x[2], x[3]])
   >>> X + True
   farray([x[0], x[1], x[2], x[3], 1])

To repeat arrays, use the ``*`` operator::

   >>> X * 2
   farray([x[0], x[1], x[2], x[3], x[0], x[1], x[2], x[3]])
   >>> 0 * X
   farray([])

Similarly, this works for single functions as well::

   >>> a * 3
   farray([a, a, a])
   >>> 2 * a + b * 3
   farray([a, a, b, b, b])

Multi-dimensional arrays are automatically flattened during either
concatenation or repetition::

   >>> Z = exprvars('z', 2, 2)
   >>> X + Z
   farray([x[0], x[1], x[2], x[3], z[0,0], z[0,1], z[1,0], z[1,1]])
   >>> Z * 2
   farray([z[0,0], z[0,1], z[1,0], z[1,1], z[0,0], z[0,1], z[1,0], z[1,1]])

If you require a more subtle treatment of the shapes,
use the ``reshape`` method to unflatten things::

   >>> (Z*2).reshape(2, 4)
   farray([[z[0,0], z[0,1], z[1,0], z[1,1]],
           [z[0,0], z[0,1], z[1,0], z[1,1]]])

Function arrays also support the "in-place" ``+=`` and ``*=`` operators.
The ``farray`` behaves like an immutable object.
That is, it behaves more like the Python ``tuple`` than a ``list``.

For example, when you concatenate/repeat an ``farray``,
it returns a new ``farray``::

   >>> A = exprvars('a', 4)
   >>> B = exprvars('b', 4)
   >>> id(A)
   3050928972
   >>> id(B)
   3050939660
   >>> A += B
   >>> id(A)
   3050939948
   >>> B *= 2
   >>> id(B)
   3050940716

The ``A += B`` implementation is just syntactic sugar for::

   >>> A = A + B

And the ``A *= 2`` implementation is just syntactic sugar for::

   >>> A = A * 2

To wrap up,
let's re-write the ``xtime`` function using PyEDA function arrays.

.. code-block:: python

   def xtime(b, n):
       """Return b^n using polynomial multiplication in GF(2^8)."""
       for _ in range(n):
           b = exprzeros(1) + b[:7] ^ uint2exprs(0x1b, 8) & b[7]*8
       return b

