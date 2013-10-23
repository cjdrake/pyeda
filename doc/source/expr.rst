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

All three "zero" objects are the same::

   >>> zeroA == zeroB == zeroC
   True

Similarly for :math:`1`::

   >>> oneA = expr(1)
   >>> oneB = expr(True)
   >>> oneC = expr("1")

All three "one" objects are the same::

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
and assign it to a Python object named ``a``::

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

   >>> a = exprvar('a')
   >>> c_b_a = exprvar(('a', 'b', 'c'))
   >>> a.names
   ('a', )
   >>> c_b_a.names
   ('a', 'b', 'c')

Notice that the default representation of a variable will dot all the names
together starting with the most significant index of the tuple on the left::

   >>> str(c_b_a)
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

Expressions are defined recursively as being composed of primitives
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

Python does not have enough builtin operators to handle all interesting Boolean
functions we can represent directly as an expression.
Also, binary operators are limited to two operands at a time,
whereas several Boolean operators are N-ary (arbitrary many operands).
This section will describe all the factory functions that can be used to create
arbitrary Boolean expressions.

The general form of these functions is
``OP(arg [, arg], simplify=True, factor=False)``.
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

Primary Operators
^^^^^^^^^^^^^^^^^

Since NOT, OR, and AND form a complete basis for a Boolean algebra,
these three operators are *primary*.

.. function:: Not(arg, simplify=True, factor=False)

   Return an expression that is the inverse of the input.

.. function:: Or(\*args, simplify=True, factor=False)

   Return an expression that evaluates to :math:`1` if and only if *any* inputs
   are :math:`1`.

.. function:: And(\*args, simplify=True, factor=False)

   Return an expression that evaluates to :math:`1` if and only if *all* inputs
   are :math:`1`.

Example of full adder logic using ``Not``, ``Or``, and ``And``::

   >>> s = Or(And(Not('a'), Not('b'), 'ci'), And(Not('a'), 'b', Not('ci')), And('a', Not('b'), Not('ci')), And('a', 'b', 'ci'))
   >>> co = Or(And('a', 'b'), And('a', 'ci'), And('b', 'ci'))

Secondary Operators
^^^^^^^^^^^^^^^^^^^

A *secondary* operator is a Boolean operator that can be natively represented
as a PyEDA expression,
but contains more information than the primary operators.
That is, these expressions always increase in tree size when converted to
primary operators.

.. function:: Xor(\*args, simplify=True, factor=False, conj=False)

   Return an expression that evaluates to :math:`1` if and only if the input
   parity is odd.

The full adder circuit has a more dense representation when you
use the ``Xor`` operator::

   >>> s = Xor('a', 'b', 'ci')
   >>> co = Or(And('a', 'b'), And('a', 'ci'), And('b', 'ci'))

.. function:: Xnor(\*args, simplify=True, factor=False, conj=False)

   Return an expression that evaluates to :math:`1` if and only if the input
   parity is even.

.. function:: Equal(\*args, simplify=True, factor=False, conj=False)

   Return an expression that evaluates to :math:`1` if and only if all inputs
   are equivalent.

.. function:: Unequal(\*args, simplify=True, factor=False, conj=False)

   Return an expression that evaluates to :math:`1` if and only if *not* all
   inputs are equivalent.

.. function:: Implies(p, q, simplify=True, factor=False)

   Return an expression that implements Boolean implication
   (:math:`p \rightarrow q`).

+-----------+-----------+-------------------------+
| :math:`f` | :math:`g` | :math:`f \rightarrow g` |
+===========+===========+=========================+
|         0 |         0 |                       1 |
+-----------+-----------+-------------------------+
|         0 |         1 |                       1 |
+-----------+-----------+-------------------------+
|         1 |         0 |                       0 |
+-----------+-----------+-------------------------+
|         1 |         1 |                       1 |
+-----------+-----------+-------------------------+

.. function:: ITE(s, d1, d0, simplify=True, factor=False)

   Return an expression that implements the Boolean "if, then, else" operator.
   If :math:`s = 1`, then the output equals :math:`d_{0}`.
   Otherwise (:math:`s = 0`), the output equals :math:`d_{1}`.

+-----------+---------------+---------------+------------------------------+
| :math:`s` | :math:`d_{1}` | :math:`d_{0}` | :math:`ite(s, d_{1}, d_{0})` |
+===========+===============+===============+==============================+
|         0 |             0 |             0 |                            0 |
+-----------+---------------+---------------+------------------------------+
|         0 |             0 |             1 |                            1 |
+-----------+---------------+---------------+------------------------------+
|         0 |             1 |             0 |                            0 |
+-----------+---------------+---------------+------------------------------+
|         0 |             1 |             1 |                            1 |
+-----------+---------------+---------------+------------------------------+
|         1 |             0 |             0 |                            0 |
+-----------+---------------+---------------+------------------------------+
|         1 |             0 |             1 |                            0 |
+-----------+---------------+---------------+------------------------------+
|         1 |             1 |             0 |                            1 |
+-----------+---------------+---------------+------------------------------+
|         1 |             1 |             1 |                            1 |
+-----------+---------------+---------------+------------------------------+

High Order Operators
^^^^^^^^^^^^^^^^^^^^

A *high order* operator is a Boolean operator that can NOT be natively
represented as a PyEDA expression.
That is, these factory functions will always return expressions composed from
primary and/or secondary operators.

.. function:: Nor(\*args, simplify=True, factor=False)

   Return ``Not(Or(*args, ...))``.

.. function:: Nand(\*args, simplify=True, factor=False)

   Return ``Not(And(*args, ...))``.

.. function:: OneHot0(\*args, simplify=True, factor=False, conj=True)

   Return an expression that evaluates to :math:`1` if and only if the number
   of inputs equal to :math:`1` is at most :math:`1`.
   That is, return true when at most one input is "hot".

.. function:: OneHot(\*args, simplify=True, factor=False, conj=True)

   Return an expression that evaluates to :math:`1` if and only if exactly one
   input is equal to :math:`1`.
   That is, return true when exactly one input is "hot".

.. function:: Majority(\*args, simplify=True, factor=False, conj=False)

   Return an expression that evaluates to :math:`1` if and only if the majority
   of inputs equal :math:`1`.

The full adder circuit has a much more dense representation when you
use both the ``Xor`` and ``Majority`` operators::

   >>> s = Xor('a', 'b', 'ci')
   >>> co = Majority('a', 'b', 'ci')

From the ``expr`` Function
--------------------------

.. function:: expr(arg, simplify=True, factor=False)

The ``expr`` function is very special.
It will attempt to convert the input argument to an ``Expression`` object.

We have already seen how the ``expr`` function converts a Python ``bool``
input to a constant expression::

   >>> expr(False)
   0

Now let's pass a ``str`` as the input argument::

   >>> expr('0')
   0

If given an input string, the ``expr`` function will attempt to parse the input
string and return an expression.

Examples of input expressions::

   >>> expr("-a * b + -c * d")
   a' * b + c' * d
   >>> expr("p => q")
   p => q
   >>> expr("p <=> q")
   Equal(p, q)
   >>> expr("s ? d[1] : d[0]")
   s ? d[1] : d[0]
   >>> expr("Or(a, b, Not(c))")
   a + b + c'
   >>> expr("Majority(a, b, c)")
   a * b + a * c + b * c

Operator Precedence Table (lowest to highest):

+--------------------------------------+---------------------------------------+
| Operator                             | Description                           |
+======================================+=======================================+
| ``s ? d1 : d0``                      | If Then Else                          |
+--------------------------------------+---------------------------------------+
| ``=>``                               | Binary Implies,                       |
| ``<=>``                              | Binary Equal                          |
+--------------------------------------+---------------------------------------+
| ``+``                                | Binary OR                             |
+--------------------------------------+---------------------------------------+
| ``*``                                | Binary AND                            |
+--------------------------------------+---------------------------------------+
| ``-x``                               | Unary NOT                             |
+--------------------------------------+---------------------------------------+
| ``(expr ...)``                       | Parenthesis,                          |
| ``OP(expr ...)``                     | Explicit operators                    |
+--------------------------------------+---------------------------------------+

The full list of valid operators accepted by the expression parser:

* ``Or(...)``
* ``And(...)``
* ``Xor(...)``
* ``Xnor(...)``
* ``Equal(...)``
* ``Unequal(...)``
* ``Nor(...)``
* ``Nand(...)``
* ``OneHot0(...)``
* ``OneHot(...)``
* ``Majority(...)``
* ``ITE(s, d1, d0)``
* ``Implies(p, q)``
* ``Not(a)``

Expression Types
================

This section will cover the hierarchy of Boolean expression types.

Unsimplified
------------

An unsimplified expression consists of the following components:

* Constants
* Expressions that can *easily* be converted to constants (eg :math:`x + -x = 1`)
* Literals
* Primary operators: ``Not``, ``Or``, ``And``
* Secondary operators

Also, an unsimplified expression does not automatically join adjacent,
associative operators.
For example, :math:`a + (b + c)` is equivalent to :math:`a + b + c`.
The depth of the unsimplified expression is two::

   >>> f = Or('a', Or('b', 'c'), simplify=False)
   >>> f.args
   frozenset({a, b + c})
   >>> f.depth
   2

The depth of the simplified expression is one::

   >>> g = f.simplify()
   >>> g.args
   frozenset({a, b, c})
   >>> g.depth
   1

Simplifed
---------

A simplified expression consists of the following components:

* Literals
* Primary operators: ``Not``, ``Or``, ``And``
* Secondary operators

Also, :math:`0` and :math:`1` are considered simplified by themselves.

That is, the act of *simplifying* an expression eliminates constants,
and all sub-expressions that can be easily converted to constants.

All expressions constructed using overloaded operatiors are automatically
simplified::

   >>> a + 0
   a
   >>> a + 1
   1
   >>> a + b * -b
   a

Unsimplified expressions are not very useful,
so the factory functions also simplify by default::

   >>> Or(a, And(b, -b))
   a

To simplify an expression, use the ``simplify`` method::

   >>> f = Or(a, 0, simplify=False)
   >>> f
   0 + a
   >>> g = f.simplify()
   >>> g
   a

You can check whether an expression is simplified using the ``simplified``
attribute::

   >>> f.simplified
   False
   >>> g.simplified
   True

Factored
--------

A factored expression consists of the following components:

* Literals
* Primary operators: ``Or``, ``And``

That is, the act of *factoring* an expression converts all secondary operators
to primary operators,
and uses DeMorgan's transform to eliminate ``Not`` operators.

You can factor all secondary operators::

   >>> Xor(a, b, c).factor()
   a' * b' * c + a' * b * c' + a * b' * c' + a * b * c
   >>> Implies(p, q).factor()
   p' + q
   >>> Equal(a, b, c).factor()
   a' * b' * c' + a * b * c
   >>> ITE(s, a, b).factor()
   a * s + b * s'

Factoring also eliminates all ``Not`` operators,
by using DeMorgan's law::

   >>> Not(a + b).factor()
   a' * b'
   >>> Not(a * b).factor()
   a' + b'

Normal Form
-----------

A normal form expression is a factored expression with depth less than or
equal to two.

That is, a normal form expression has been factored, and *flattened*.

There are two types of normal forms:

* disjunctive normal form (SOP: sum of products)
* conjunctive normal form (POS: product of sums)

The preferred method for creating normal form expressions is to use the
``to_dnf`` and ``to_cnf`` methods::

   >>> f = Xor(a, Implies(b, c))
   >>> f.to_dnf()
   a' * b' + a' * c + a * b * c'
   >>> f.to_cnf()
   (a' + b) * (a' + c') * (a + b' + c)

Canonical Normal Form
---------------------

A canonical normal form expression is a normal form expression with the
additional property that all terms in the expression have the same degree as
the expression itself.

That is, a canonical normal form expression has been factored, flattened,
and *reduced*.

The preferred method for creating canonical normal form expressions is to use
the ``to_cdnf`` and ``to_ccnf`` methods.

Using the same function from the previous section as an example::

   >>> f = Xor(a, Implies(b, c))
   >>> f.to_cdnf()
   a' * b' * c' + a' * b' * c + a' * b * c + a * b * c'
   >>> f.to_ccnf()
   (a + b' + c) * (a' + b + c) * (a' + b + c') * (a' + b' + c')

Satisfiability
==============

Expressions have smart support for Boolean satisfiability.

They inherit both the ``satisfy_one`` and ``satisfy_all`` methods from the
``Function`` interface.

For example::

   >>> f = Xor('a', Implies('b', 'c'))
   >>> f.satisfy_one()
   {a: 0, b: 0}
   >>> list(f.satisfy_all())
   [{a: 0, b: 0}, {a: 0, b: 1, c: 1}, {a: 1, b: 1, c: 0}]

By default, Boolean expressions use a very naive "backtracking" algorithm to
solve for satisfying input points.
Since SAT is an NP-complete algorithm,
you should always use care when preparing your inputs.

A conjunctive normal form expression will automatically use the
`PicoSAT <http://fmv.jku.at/picosat>`_ C extension.
This is an industrial-strength SAT solver,
and can be used to solve very non-trivial problems.

   >>> g = f.to_cnf()
   >>> g.satisfy_one()
   {a: 0, b: 0, c: 1}
   >>> list(g.satisfy_all())
   [{a: 0, b: 0}, {a: 0, b: 1, c: 1}, {a: 1, b: 1, c: 0}]

.. note:: Future versions of PyEDA might support additional C/C++ extensions
          for SAT solving. This is an active area of research, and no single
          solver is ideal for all cases.

Tseitin's Encoding
==================

To take advantage of the PicoSAT solver,
you need an expression that is in conjunctive normal form.
Some expressions (especially Xor) have exponentially large size when you
expand them to a CNF.

One way to work around this limitation is to use Tseitin's encoding.
To convert an expression to Tseitin's encoding, use the ``tseitin`` method::

   >>> f = Xor('a', Implies('b', 'c'))
   >>> tf = f.tseitin()
   >>> tf
   (a + aux[0]') * (a' + aux[0] + b' + c) * (a' + aux[2]') * (a + aux[1]' + aux[2]) * (aux[0] + aux[2]) * (aux[0]' + b) * (aux[0]' + c') * (aux[1] + aux[2]') * (aux[1] + b) * (aux[1] + c') * (aux[1]' + b' + c)

As you can see, Tseitin's encoding introduces several "auxiliary" variables
into the expression.

You can change the name of the auxiliary variable by using the ``auxvarname``
parameter::

   >>> f = Xor('a', Implies('b', 'c'))
   >>> f.tseitin(auxvarname='z')
   (a + z[0]') * (a' + b' + c + z[0]) * (a' + z[2]') * (z[1] + z[2]') * (a + z[1]' + z[2]) * (b + z[1]) * (c' + z[1]) * (b' + c + z[1]') * (b + z[0]') * (c' + z[0]') * (z[0] + z[2])

You will see the auxiliary variables in the satisfying points::

   >>> tf.satisfy_one()
   {a: 0, aux[0]: 0, aux[1]: 1, aux[2]: 1, b: 0, c: 1}
   >>> list(tf.satisfy_all())
   [{a: 0, aux[0]: 0, aux[1]: 1, aux[2]: 1, b: 0},
    {a: 0, aux[0]: 0, aux[1]: 1, aux[2]: 1, b: 1, c: 1},
    {a: 1, aux[0]: 1, aux[1]: 0, aux[2]: 0, b: 1, c: 0}]

Just filter them out to get the answer you're looking for::

   >>> [{v: val for v, val in point.items() if v.name != 'aux'} for point in tf.satisfy_all()]
   [{a: 0, b: 0}, {a: 0, b: 1, c: 1}, {a: 1, b: 1, c: 0}]

Formal Equivalence
==================

Two Boolean expressions :math:`f` and :math:`g` are formally equivalent if
:math:`f \oplus g` is not satisfiable.

Boolean expressions have an ``equivalent`` method that implements this basic
functionality.
It uses the naive backtracking SAT,
because it is difficult to determine whether any particular expression can
be converted efficiently to a CNF.

Let's test whether bit 6 of a ripple carry adder is equivalent to bit 6 of a
Kogge Stone adder::

   >>> from pyeda.logic.addition import ripple_carry_add, kogge_stone_add
   >>> A = bitvec('a', 16)
   >>> B = bitvec('b', 16)
   >>> S1, C1 = ripple_carry_add(A, B)
   >>> S2, C2 = kogge_stone_add(A, B)
   >>> S1[6].equivalent(S2[6])
   True

Note that this is the same as the following::

   >>> Xor(S1[6], S2[6]).satisfy_one() is None
   True
