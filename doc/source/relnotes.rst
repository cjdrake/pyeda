.. relnotes.rst

*****************
  Release Notes
*****************

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

Version 0.11.1
--------------

* Fixed bug #16: ``Function.reduce`` only implemented by Variable

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
