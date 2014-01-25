.. _relnotes:

*****************
  Release Notes
*****************

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

