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
