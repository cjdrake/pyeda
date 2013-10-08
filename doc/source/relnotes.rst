.. _relnotes:

*****************
  Release Notes
*****************

Version 0.15 (Coming Soon)
==========================

* Drop support for Python 2.7. Will only support Python 3.2+ going forward.
* Integrate `PicoSAT <http://fmv.jku.at/picosat/>`_,
  a compact SAT solver written in C.

Version 0.14
============

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

Release 0.14.1
--------------

Fixed `Issue #41 <https://github.com/cjdrake/pyeda/issues/41>`_.
Basically, the package metadata in the ``0.14.0`` release was incomplete,
so the source distribution only contained a few modules. Whoops.

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

Release 0.11.1
--------------

* Fixed bug #16: ``Function.reduce`` only implemented by Variable
