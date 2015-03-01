.. reference/boolalg/expr.rst

*********************************************
  :mod:`pyeda.boolalg.expr` --- Expressions
*********************************************

.. automodule:: pyeda.boolalg.expr

Interface Functions
===================

.. autofunction:: pyeda.boolalg.expr.exprvar

.. autofunction:: pyeda.boolalg.expr.expr

.. autofunction:: pyeda.boolalg.expr.ast2expr

.. autofunction:: pyeda.boolalg.expr.expr2dimacscnf

.. autofunction:: pyeda.boolalg.expr.upoint2exprpoint

Operators
---------

Primary Operators
^^^^^^^^^^^^^^^^^

.. autofunction:: pyeda.boolalg.expr.Not

.. autofunction:: pyeda.boolalg.expr.Or

.. autofunction:: pyeda.boolalg.expr.And

Secondary Operators
^^^^^^^^^^^^^^^^^^^

.. autofunction:: pyeda.boolalg.expr.Xor

.. autofunction:: pyeda.boolalg.expr.Equal

.. autofunction:: pyeda.boolalg.expr.Implies

.. autofunction:: pyeda.boolalg.expr.ITE

High Order Operators
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: pyeda.boolalg.expr.Nor

.. autofunction:: pyeda.boolalg.expr.Nand

.. autofunction:: pyeda.boolalg.expr.Xnor

.. autofunction:: pyeda.boolalg.expr.Unequal

.. autofunction:: pyeda.boolalg.expr.OneHot0

.. autofunction:: pyeda.boolalg.expr.OneHot

.. autofunction:: pyeda.boolalg.expr.Majority

.. autofunction:: pyeda.boolalg.expr.AchillesHeel

.. autofunction:: pyeda.boolalg.expr.Mux

Interface Classes
=================

Expression Tree Nodes
---------------------

.. autoclass:: pyeda.boolalg.expr.Expression
   :members: __rshift__,
             simplify,
             simple,
             depth,
             to_ast,
             expand,
             to_nnf,
             to_dnf,
             to_cnf,
             cover,
             encode_inputs,
             encode_dnf,
             encode_cnf,
             tseitin,
             complete_sum,
             equivalent,
             to_dot
   :member-order: bysource

.. autoclass:: pyeda.boolalg.expr.Atom

.. autoclass:: pyeda.boolalg.expr.Constant

.. autoclass:: pyeda.boolalg.expr.Literal

.. autoclass:: pyeda.boolalg.expr.Complement

.. autoclass:: pyeda.boolalg.expr.Variable

.. autoclass:: pyeda.boolalg.expr.Operator

.. autoclass:: pyeda.boolalg.expr.NaryOp

.. autoclass:: pyeda.boolalg.expr.OrAndOp

.. autoclass:: pyeda.boolalg.expr.OrOp

.. autoclass:: pyeda.boolalg.expr.AndOp

.. autoclass:: pyeda.boolalg.expr.XorOp

.. autoclass:: pyeda.boolalg.expr.EqualOp

.. autoclass:: pyeda.boolalg.expr.NotOp

.. autoclass:: pyeda.boolalg.expr.ImpliesOp

.. autoclass:: pyeda.boolalg.expr.IfThenElseOp

Normal Forms
------------

.. autoclass:: pyeda.boolalg.expr.NormalForm

.. autoclass:: pyeda.boolalg.expr.DisjNormalForm

.. autoclass:: pyeda.boolalg.expr.ConjNormalForm

.. autoclass:: pyeda.boolalg.expr.DimacsCNF

