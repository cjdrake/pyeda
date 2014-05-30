.. reference/boolalg/bdd.rst

*********************************************************
  :mod:`pyeda.boolalg.bdd` --- Binary Decision Diagrams
*********************************************************

.. automodule:: pyeda.boolalg.bdd

Interface Functions
===================

.. autofunction:: pyeda.boolalg.bdd.bddvar

.. autofunction:: pyeda.boolalg.bdd.expr2bdd

.. autofunction:: pyeda.boolalg.bdd.bdd2expr

.. autofunction:: pyeda.boolalg.bdd.upoint2bddpoint

.. autofunction:: pyeda.boolalg.bdd.ite

Interface Classes
-----------------

.. autoclass:: pyeda.boolalg.bdd.BDDNode

.. autoclass:: pyeda.boolalg.bdd.BinaryDecisionDiagram
   :members: dfs_preorder,
             dfs_postorder,
             bfs,
             equivalent,
             to_dot
   :member-order: bysource

.. autoclass:: pyeda.boolalg.bdd.BDDConstant

.. autoclass:: pyeda.boolalg.bdd.BDDVariable

