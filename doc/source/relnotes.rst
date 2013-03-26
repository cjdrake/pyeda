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
