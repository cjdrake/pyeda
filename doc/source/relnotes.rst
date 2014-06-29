.. _relnotes:

*****************
  Release Notes
*****************

Version 0.25
============

This is a small, incremental release.
I recently changed jobs and moved,
so development will definitely slow down for a while.

Function array concatenation and repetition for MDAs is now a bit smarter
(`Issue 96 <https://github.com/cjdrake/pyeda/issues/96>`_).
Rather than simply flattening,
the operators will attempt to retain the shape of the MDAs if possible.
For example, a ``2x6x7 + 2x6x7`` concatenation will return ``4x6x7``,
and ``2x6x7 * 2`` repetition will return ``4x6x7``.

Got rid of ``a[0][1][2]`` expression parsing syntax.
Use ``a[0,1,2]`` instead.
Also got rid of the ``bitvec`` function.
Use the ``exprvars`` function (or ``bddvars``, ``ttvars``) instead.
Finally all vestiges of the legacy ``BitVector`` MDA methodology are gone.

Everything else was just miscellaneous code/test/documentation cleanup.

Version 0.24
============

Variables names are now required to be C-style identifiers.
I.e., ``[a-zA-Z_][a-zA-Z0-9_]*``.

The expression parser now handles both ``a[1][2][3]`` and ``a[1,2,3]`` syntaxes
(`Issue 91 <https://github.com/cjdrake/pyeda/issues/91>`_).
The ``a[1][2][3]`` is deprecated.

Got rid of expression ``is_neg_unate``, ``is_pos_unate``,
and ``is_binate`` functions.
I haven't been able to find an *efficient* algorithm for this,
so just convert expressions and BDDs to truth tables first.
If your function is too big to fit in a truth table,
it's probably also too big to expand to a canonical expression.

``Not(Not(...))`` double negation is now automatically reduced,
just like ``Not(Nand(...))``, etc.

Cleaned up the definition of expression depth
(`Issue 92 <https://github.com/cjdrake/pyeda/issues/92>`_).
This is not backwards compatible.

Fixed `Issue 93 <https://github.com/cjdrake/pyeda/issues/93>`_,
picosat script fails with trivial zero input::

   $ picosat
   p cnf 0 1
   0

Changed ``RegexLexer`` to yield ``EndToken`` at the end of a token stream.
This makes parsing nicer, avoiding catching ``StopIteration`` everywhere.

Got rid of ``factor=False`` on expression factory functions.
This was overly designed UI.

The expression ``restrict`` method is a little faster now.
Especially for big functions.

Added *lots* of new reference documentation.

Added new ``farray`` documentation chapter.
Fixed several little issues with function arrays during this process.
The constructor now takes an ``ftype=None`` parameter.
Negative indices make more sense now.
Slices behave more like Python tuple slices.
Fixed several inconsistencies with empty arrays.

Deprecated ``bitvec`` function.

Version 0.23
============

This version introduces a new ``picosat`` script.
Now you can solve DIMACS CNF files from the command-line.
See http://pyeda.readthedocs.org/en/latest/expr.html#picosat-script
for details.

Finally there is a proper documentation chapter for binary decision diagrams!
While writing this documentation,
I noticed, and fixed some obscure bugs related to incorrect usage of weak
references to BDD nodes.

Made some minor changes to the public interface of the ``bdd`` module.

Replaced the ``traverse`` method with three options for BDD iteration:

* ``bdd.dfs_preorder`` - Depth-first search pre-order traversal
* ``bdd.dfs_postorder`` - Depth-first search post-order traversal
* ``bdd.bfs()`` - Breadth-first search

Got rid of the deprecated ``uint2bv`` and ``int2bv`` functions.
Use the ``uint2exprs``, ``int2exprs`` functions instead.

Changed the ``pyeda.parsing.parse_pla`` function so it takes a string input.
This makes it much easier to test.

Deprecated the ``is_neg_unate``, ``is_pos_unate``, ``is_binate``
methods for expressions.
I haven't found a correct algorithm that is better than just 1) converting
to a truth table, and 2) checking for monotonicity in the cofactors.

As of this release, I will be dropping support for Python 3.2.

Version 0.22
============

A couple features, and some good bug-fixes in this release.

Fixed `Issue 80 <https://github.com/cjdrake/pyeda/issues/80>`_.
Apparently, I forgot to implement the right-side version of XOR operator: ``0 ^ x``.

Fixed `Issue 81 <https://github.com/cjdrake/pyeda/issues/81>`_.
I continue finding bugs with degenerate forms.
This particular one comes up when you try to do something similar to
``Or(Or(a, b))``.
The ``__new__`` method was implemented incorrectly,
so I moved the ``Or(a) = a`` (and similar) rules to the ``simplify`` method.

To match the notation used by Univ of Illinois VLSI class,
I changed BDD low/high nodes to "lo", and "hi".

Got rid of the "minus" operator, ``a - b``.
This was previously implemented as ``a | ~b``,
but I don't think it has merit anymore.

The ``farray`` type now uses the ``+`` operator for concatenation,
and ``*`` for repetition.
These are very important features in SystemVerilog.
See `Issue 77 <https://github.com/cjdrake/pyeda/issues/77>`_ for details.

Implemented the ``farray.__setitem__`` method.
It is very useful to instantiate an ``farray`` using ``exprzeros``,
and then programmatically assign indices one-by-one.
See `Issue 78 <https://github.com/cjdrake/pyeda/issues/78>`_ for details.

To demonstrate some of the fancy, new ``farray`` features,
I added the AES algorithm to the ``logic`` package.
It manages to complete all the logic assignments,
but I haven't been able to test its correctness yet,
because it explodes the memory on my machine.
At a bare minimum, it will be a nice test case for performance optimizations
necessary to handle large designs.

Version 0.21
============

Important bug fix! `Issue 75 <https://github.com/cjdrake/pyeda/issues/75>`_.
`Harnesser <https://github.com/Harnesser>`_ pointed out that Espresso was
returning some goofy results for
degenerate inputs (a literal or ``AND(lit, lit, ...)``).

The major new feature in this release is the ``farray`` mult-dimensional
array (MDA) data type.
The implementation of ``BitVector`` was a kludge --
it was built around the ``Expression`` function type,
and didn't support all the fancy things you could do with numpy slices.
All usage of the old ``Slicer`` and ``BitVector`` types has been eliminated,
and replaced by ``farray``.
This includes the ``bitvec``, ``uint2bv``, and ``int2bv`` functions,
and the contents of the ``pyeda.logic`` package (addition, Sudoku, etc).

Both ``uint2bv`` and ``int2bv`` are deprecated,
superceded by ``uint2exprs`` and ``int2exprs`` (or ``uint2bdds``, etc).
So far I haven't deprecated ``bitvec``,
because it's a very commonly-used function.

See `Issue 68 <https://github.com/cjdrake/pyeda/issues/68>`_ for some details
on the ``farray`` type.
My favorite part is the ability to multiplex an ``farray`` using Python's
slice syntax::

   >>> xs = exprvars('x', 4)
   >>> sel = exprvars('s', 2)
   >>> xs[sel]
   Or(And(~s[0], ~s[1], x[0]), And(s[0], ~s[1], x[1]), And(~s[0], s[1], x[2]), And(s[0], s[1], x[3]))

This even works with MDAs::

   >>> xs = exprvars('x', 4, 4)
   >>> sel = exprvars('s', 2)
   >>> xs[0,sel]
   Or(And(~s[0], ~s[1], x[0][0]), And(s[0], ~s[1], x[0][1]), And(~s[0], s[1], x[0][2]), And(s[0], s[1], x[0][3]))

Added ``AchillesHeel`` function to expression parsing engine.

Eliminated the ``+`` and ``*`` operators for Boolean OR, AND, respectively.
This is annoying, but I need these operators for
`Issue 77 <https://github.com/cjdrake/pyeda/issues/77>`_.
Sorry for any trouble, but that's what major version zero is for :).

Version 0.20
============

Probably the most useful feature in this release is the ``espresso`` script::

   $ espresso -h
   usage: espresso [-h] [-e {fast,ness,nirr,nunwrap,onset,strong}] [--fast]
                   [--no-ess] [--no-irr] [--no-unwrap] [--onset] [--strong]
                   [file]

   Minimize a PLA file

   positional arguments:
     file                  PLA file (default: stdin)

   optional arguments:
     ...

This script implements a subset of the functionality of the original
``Espresso`` command-line program.
It uses the new ``parse_pla`` function in the ``pyeda.parsing.pla`` module
to parse common PLA files.
Note that the script only intends to implement basic truth-table functionality
at the moment.
It doesn't support multiple-valued variables,
and various other Espresso built-in features.

Added Espresso ``get_config`` and ``set_config`` functions,
to manipulate global configuration

New ``Bitvector`` methods:

* ``unor`` - unary nor
* ``unand`` - unary nand
* ``uxnor`` - unary xnor

Made ``BitVector`` an immutable type.
As a result, dropped item assignment ``X[0] = a``,
zero extension ``X.zext(4)``, sign extension ``X.sext(4)``,
and ``append`` method.

The ``BitVector`` type now supports more overloaded operators:

* ``X + Y`` concatenate two bit vectors
* ``X << n`` return the bit vector left-shifted by ``n`` places
* ``X >> n`` return the bit vector right-shifted by ``n`` places

Both left shift and right shift are simple shifts--they use the default
"carry-in" of zero.

Got rid of ``boolify`` utility function.
It had been replaced over time by more sophisticated techniques.

There is a new ``Mux`` factory function,
for multiplexing arbitrarily many input functions.

Update to PicoSAT 959.
Check the `homepage <http://fmv.jku.at/picosat>`_ for details,
but it looks like the only changes were related to header file documentation.

Added a neat capability to specify assumptions for SAT-solving using a ``with``
statement.
It supports both literal and product-term forms::

   >>> f = Xor(a, b, c)
   >>> with a, ~b:
   ...     print(f.satisfy_one())
   {a: 1, b: 0, c: 0}
   >>> with a & ~b:
   ...     print(f.satisfy_one())
   {a: 1, b: 0, c: 0}

At the moment, this only works for the ``satisfy_one`` method,
because it is so handy and intuitive.

Version 0.19
============

Release 0.19.3
--------------

Enhanced error handling in the Espresso C extension.

Release 0.19.2
--------------

Added the ``espresso_tts`` function,
which allows you to run Espresso on one or more ``TruthTable`` instances.

Release 0.19.1
--------------

Fixed a bone-headed mistake: leaving ``espresso.h`` out of the source
distribution.
One of these days I will remember to test the source distribution for all the
necessary files before releasing it.

Release 0.19.0
--------------

This is a very exciting release!
After much hard work, PyEDA now has a C extension to the famous Espresso logic
minimization software from Berkeley!
See the new chapter on two-level logic minimization for usage information.

Also, after some feedback from users, it became increasingly obvious that
using the ``-+*`` operators for NOT, OR, AND was a limitation.
Now, just like Sympy, PyEDA uses the ``~|&^`` operators for symbolic algebra.
For convenience, the legacy operators will issue deprecation warnings for now.
In some upcoming release, they will no longer work.

After other feedback from users, I changed the way ``Expression`` string
representation works.
Now, the ``__str__`` method uses ``Or``, ``And``, etc, instead of ascii
characters.
The idea is that the string representation now returns valid Python that can
be parsed by the ``expr`` function (or the Python interpreter).
To provide support for fancy formatting in IPython notebook,
I added the new ``to_unicode`` and ``to_latex`` methods.
These methods also return fancy string representations.

For consistency, the ``uint2vec`` and ``int2vec`` functions have been renamed
to ``uint2bv`` and ``int2bv``, respectively.

Since ``is_pos_unate``, ``is_neg_unate``, and ``is_binate`` didn't seem like
fundamental operations,
I remove them from the ``Function`` base class.

Version 0.18
============

Release 0.18.1
--------------

Three minor tweaks in this release:

* ``expr``/``bdd`` ``to_dot`` methods now return undirected graphs.
* Added ``AchillesHeel`` factory function to ``expr``.
* Fixed a few obscure bugs with simplification of ``Implies`` and ``ITE``.

Release 0.18.0
--------------

New stuff in this release:

* Unified the ``Expression`` and ``Normalform`` expression types,
  getting rid of the need for the ``nfexpr`` module.
* Added ``to_dot`` methods to both ``Expression`` and ``BinaryDecisionDiagram``
  data types.

Mostly incremental changes this time around.
My apologies to anybody who was using the ``nfexpr`` module.
Lately, ``Expression`` has gotten quite fast, especially with the addition
of the PicoSAT C extension.
The normal form data type as ``set(frozenset(int))`` was not a proper
implementation of the ``Function`` class,
so finally did away with it in favor of the new "encoded" representation that
matches the Dimacs CNF convention of mapping an index 1..N to each variable,
and having the negative index correspond to the complement.
So far this is only useful for CNF SAT-solving,
but may also come in handy for any future, fast operations on 2-level covers.

Also, somewhat awesome is the addition of the ``to_dot`` methods.
I was playing around with IPython extensions,
and eventually hacked up a neat solution for drawing BDDs into the notebook.
The magic functions are published in my
`ipython-magic repo <https://github.com/cjdrake/ipython-magic>`_.
See the
`usage notes <https://github.com/ipython/ipython/wiki/Extensions-Index#graphviz-extensions>`_.
Using ``subprocess`` is probably not the best way to interface with Graphviz,
but it works well enough without any dependencies.

Version 0.17
============

Release 0.17.1
--------------

Got rid of the ``assumptions`` parameter from ``boolalg.picosat.satisfy_all``
function, because it had no effect.
Read through ``picosat.h`` to figure out what happened,
and you need to re-apply assumptions for every call to ``picosat_sat``.
For now, the usage model seems a little dubious, so just got rid of it.

Release 0.17.0
--------------

New stuff in this release:

* Added ``assumptions=None`` parameter to PicoSAT ``satisfy_one`` and
  ``satisfy_all`` functions.
  This produces a *very* nice speedup in some situations.
* Got rid of extraneous ``picosat.py`` Python wrapper module.
  Now the PicoSAT Python interface is implemented by ``picosatmodule.c``.
* Updated Nor/Nand operators to secondary status.
  That is, they now can be natively represented by symbolic expressions.
* Added a Brent-Kung adder to logic.addition module
* Lots of other miscellaneous cleanup and better error handling

Version 0.16
============

Release 0.16.3
--------------

Fixed bug: absorption algorithm not returning a fully simplified expression.

Release 0.16.2
--------------

Significantly enhance the performance of the absorption algorithm

Release 0.16.1
--------------

Fixed bug: PicoSAT module compilation busted on Windows

Release 0.16.0
--------------

New stuff in this release:

* Added Expression ``complete_sum`` method,
  to generate a normal form expression that contains all prime implicants.
* Unicode expression symbols, because it's awesome
* Added new Expression ForEach, Exists factory functions.
* Changed ``frozenset`` implementation of ``OrAnd`` and ``EqualBase`` arguments
  back to ``tuple``.
  The simplification aspects had an unfortunate performance penalty.
  Use ``absorb`` to get rid of duplicate terms in DNF/CNF forms.
* Added flatten=False/True to Expression to_dnf, to_cdnf, to_cnf, to_ccnf methods.
  Often, flatten=False is faster at reducing to a normal form.
* Simplified absorb algorithm using Python sets.
* Expression added a new splitvar property,
  which implements a common heuristic to find a good splitting variable.

Version 0.15
============

Release 0.15.1
--------------

* Thanks to `Christoph Gohlke <http://www.lfd.uci.edu/~gohlke>`_,
  added build support for Windows platforms.

Release 0.15.0
--------------

This is probably the most exciting release of PyEDA yet!
Integration of the popular `PicoSAT <http://fmv.jku.at/picosat/>`_
fast C SAT solver makes PyEDA suitable for industrial-strength applications.
Unfortunately, I have no idea how to make this work on Windows yet.

Here are the full release notes:

* Drop support for Python 2.7. Will only support Python 3.2+ going forward.
* Integrate `PicoSAT <http://fmv.jku.at/picosat/>`_,
  a compact SAT solver written in C.
* Added *lots* of new capabilities to Boolean expression parsing:

  * ``s ? d1 : d0`` (ITE), ``p => q`` (Implies),
    and ``p <=> q`` (Equal) symbolic operators.
  * Full complement of explicit form Boolean operators:
    ``Or``, ``And``, ``Xor``, ``Xnor``, ``Equal``, ``Unequal``,
    ``Nor``, ``Nand``, ``OneHot0``, ``OneHot``, ``Majority``,
    ``ITE``, ``Implies``, ``Not``
  * The ``expr`` function now simplifies by default,
    and has ``simplify=True``, and ``factor=False`` parameters.

* New ``Unequal`` expression operator.
* New ``Majority`` high-order expression operator.
* ``OneHot0``, ``OneHot``, and ``Majority`` all have both disjunctive
  (``conj=False``) and conjunctive (``conj=True``) forms.
* Add new ``Expression.to_ast`` method.
  This might replace the ``expr2dimacssat`` function in the future,
* Fixed bug: ``Xor.factor(conj=True)`` returns non-equivalent expression.
* Changed the meaning of ``conj`` parameter in ``Expression.factor`` method.
  Now it is only used by the top-level, and not passed recursively.
* Normal form expression no longer inherit from ``Function``.
  They didn't implement the full interface, so this just made sense.
* Replaced ``pyeda.expr.expr2dimacscnf`` with a new
  ``pyeda.expr.DimacsCNF`` class.
  This might be unified with normal form expressions in the future.

Version 0.14
============

Release 0.14.2
--------------

Fixed `Issue #42 <https://github.com/cjdrake/pyeda/issues/42>`_.

There was a bug in the implementation of ``OrAnd``,
due to the new usage of a `frozenset` to represent the argument container.

With ``0.14.1``, you could get this::

   >>> And('a', 'b', 'c') == Or('a', 'b', 'c')
   True

Now::

   >>> And('a', 'b', 'c') == Or('a', 'b', 'c')
   False

The ``==`` operator is only used by PyEDA for hashing,
and is not overloaded by ``Expression``.
Therefore, this could potentially cause some serious issues with ``Or``/``And``
expressions that prune arguments incorrectly.

Release 0.14.1
--------------

Fixed `Issue #41 <https://github.com/cjdrake/pyeda/issues/41>`_.
Basically, the package metadata in the ``0.14.0`` release was incomplete,
so the source distribution only contained a few modules. Whoops.

Release 0.14.0
--------------

This release reorganizes the PyEDA source code around quite a bit,
and introduces some awesome new parsing utilities.

Probably the most important new feature is the addition of the
``pyeda.boolalg.expr.expr`` function.
This function takes ``int`` or ``str`` as an input.
If the input is a ``str`` instance, the function *parses the input string*,
and returns an ``Expression`` instance.
This makes it easy to form symbolic expression without even having to declare
variables ahead of time::

   >>> from pyeda.boolalg.expr import expr
   >>> f = expr("-a * b + -b * c")
   >>> g = expr("(-x[0] + x[1]) * (-x[1] + x[2])")

The return value of ``expr`` function is **not** simplified by default.
This allows you to represent arbitrary expressions, for example::

   >>> h = expr("a * 0")
   >>> h
   0 * a
   >>> h.simplify()
   0

* Reorganized source code:

  * Moved all Boolean algebra (functions, vector functions) into a new package,
    ``pyeda.boolalg``.
  * Split ``arithmetic`` into ``addition`` and ``gray_code`` modules.
  * Moved all logic functions (addition, gray code) into a new package,
    ``pyeda.logic``.
  * Created new Sudoku module under ``pyeda.logic``.

* Awesome new regex-based lexical analysis class, ``pyeda.parsing.RegexLexer``.
* Reorganized the DIMACS parsing code:

  * Refactored parsing code to use ``RegexLexer``.
  * Parsing functions now return an abstract syntax tree,
    to be used by ``pyeda.boolalg.ast2expr`` function.
  * Changed ``dimacs.load_cnf`` to ``pyeda.parsing.dimacs.parse_cnf``.
  * Changed ``dimacs.load_sat`` to ``pyeda.parsing.dimacs.parse_sat``.
  * Changed ``dimacs.dump_cnf`` to ``pyeda.boolalg.expr2dimacscnf``.
  * Changed ``dimacs.dump_sat`` to ``pyeda.boolalg.expr2dimacssat``.

* Changed constructors for ``Variable`` factories.
  Unified ``namespace`` as just a part of the ``name``.
* Changed interactive usage. Originally was ``from pyeda import *``.
  Now use ``from pyeda.inter import *``.
* Some more miscellaneous refactoring on logic expressions:

  * Fixed weirdness with ``Expression.simplified`` implementation.
  * Added new private class ``_ArgumentContainer``,
    which is now the parent of ``ExprOrAnd``, ``ExprExclusive``, ``ExprEqual``,
    ``ExprImplies``, ``ExprITE``.
  * Changed ``ExprOrAnd`` argument container to a ``frozenset``,
    which has several nice properties for simplification of AND/OR expressions.

* Got rid of ``pyeda.alphas`` module.
* Preliminary support for logic expression ``complete_sum`` method,
  for generating the set of prime implicants.
* Use a "computed table" cache in BDD ``restrict`` method.
* Use weak references to help with BDD garbage collection.
* Replace distutils with setuptools.
* Preliminary support for Tseitin encoding of logic expressions.
* Rename ``pyeda.common`` to ``pyeda.util``.

Version 0.13
============

Wow, this release took a huge leap from version 0.12.
We're probably not ready to declare a "1.0",
but it is definitely time to take a step back from API development,
and start focusing on producing useful documentation.

This is not a complete list of changes, but here are the highlights.

* Binary Decision Diagrams!
  The recursive algorithms used to implement this datatype are awesome.
* Unification of all Variable subclasses by using separate factory functions
  (``exprvar``, ``ttvar``, ``bddvar``), but a common integer "uniqid".
* New "untyped point" is an immutable 2-tuple of variable uniqids assigned
  to zero and one.
  Also a new ``urestrict`` method to go along with it.
  Most important algorithms now use untyped points internally,
  because the set operations are very elegant and avoid dealing with which type
  of variable you are using.
* Changed the Variable's ``namespace`` argument to a tuple of strings.
* Restricting a function to a 0/1 state no longer returns an integer.
  Now every function representation has its own zero/one representations.
* Now using the fantastic Logilab PyLint program!
* Truth tables now use the awesome stdlib array.array for internal
  representation.
* Changed the names of almost all Expression sublasses to ExprSomething.
  the Or/And/Not operators are now functions.
  This simplified lots of crummy ``__new__`` magic.
* Expression instances to not automatically simplify,
  but they do if you use Or/And/Not/etc with default ``**kwargs``.
* Got rid of ``constant`` and ``binop`` modules, of dubious value.
* Added ``is_zero``, ``is_one``, ``box``, and ``unbox`` to Function interface.
* Removed ``reduce``, ``iter_zeros``, and ``iter_ones`` from Function interface.
* Lots of refactoring of SAT methodology.
* Finally implemented ``unate`` methods correctly for Expressions.

Version 0.12
============

* Lots of work in ``pyeda.table``:

  * Now two classes, ``TruthTable``, and ``PCTable``
    (for positional-cube format, which allows ``X`` outputs).
  * Implemented *most* of the ``boolfunc.Function`` API.
  * Tables now support ``-``, ``+``, ``*``, and ``xor`` operators.

* Using a set container for And/Or/Xor argument simplification results in
  about 30% speedup of unit tests.
* Renamed ``boolfunc.iter_space`` to ``boolfunc.iter_points``.
* New ``boolfunc.iter_terms`` generator.
* Changed ``dnf=True`` to ``conf=False`` on several methods that give the
  option of returnin an expression in conjunctive or disjunctive form.
* Added ``conj=False`` argument to all expression ``factor`` methods.
* New ``Function.iter_domain`` and ``Function.iter_image`` iterators.
* Renamed ``Function.iter_outputs`` to ``Function.iter_relation``.
* Add ``pyeda.alphas`` module for a convenience way to grab all the a, b, c, d,
  ... variables.
* ``Xor.factor`` now returns a flattened form, instead of nested.

Version 0.11
============

Release 0.11.1
--------------

* Fixed bug #16: ``Function.reduce`` only implemented by Variable

Release 0.11.0
--------------

* In ``pyeda.dimacs`` changed ``parse_cnf`` method name to ``load_cnf``
* In ``pyeda.dimacs`` changed ``parse_sat`` method name to ``load_sat``
* In ``pyeda.dimacs`` added new method ``dump_cnf``, to convert expressions
  to CNF-formatted strings.
* In ``pyeda.dimacs`` added new method ``dump_sat``, to convert expressions
  to SAT-formatted strings.
* Variables now have a ``qualname`` attribute, to allow referencing a variable
  either by its local name or its fully-qualified name.
* Function gained a ``reduce`` method, to provide a standard interface to
  reduce Boolean function implementations to their canonical forms.
* Expressions gained a ``simplify`` parameter, to allow constructing
  unsimplified expressions.
* Expressions gained an ``expand`` method, to implement Shannon expansion.
* New if-then-else (ITE) expression type.
* NormalForm expressions now both support ``-``, ``+``, and ``*`` operators.

