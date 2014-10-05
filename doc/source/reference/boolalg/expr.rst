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

.. autofunction:: pyeda.boolalg.expr.Nor

.. autofunction:: pyeda.boolalg.expr.Nand

.. autofunction:: pyeda.boolalg.expr.Xor

.. autofunction:: pyeda.boolalg.expr.Xnor

.. autofunction:: pyeda.boolalg.expr.Equal

.. autofunction:: pyeda.boolalg.expr.Unequal

.. autofunction:: pyeda.boolalg.expr.Implies

.. autofunction:: pyeda.boolalg.expr.ITE

High Order Operators
^^^^^^^^^^^^^^^^^^^^

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
             to_unicode, to_latex,
             invert,
             simplify,
             simplified,
             depth,
             to_ast,
             expand,
             to_nnf,
             flatten,
             to_dnf,
             to_cdnf,
             to_cnf,
             to_ccnf,
             cover,
             absorb,
             reduce,
             encode_inputs,
             encode_dnf,
             encode_cnf,
             tseitin,
             complete_sum,
             equivalent,
             to_dot
   :member-order: bysource

.. autoclass:: pyeda.boolalg.expr.ExprConstant

.. autoclass:: pyeda.boolalg.expr.ExprLiteral

.. autoclass:: pyeda.boolalg.expr.ExprVariable

.. autoclass:: pyeda.boolalg.expr.ExprComplement

.. autoclass:: pyeda.boolalg.expr.ExprNot

.. autoclass:: pyeda.boolalg.expr.ExprOrAnd

.. autoclass:: pyeda.boolalg.expr.ExprOr

.. autoclass:: pyeda.boolalg.expr.ExprAnd

.. autoclass:: pyeda.boolalg.expr.ExprXor

.. autoclass:: pyeda.boolalg.expr.ExprEqual

.. autoclass:: pyeda.boolalg.expr.ExprImplies

.. autoclass:: pyeda.boolalg.expr.ExprITE

Normal Forms
------------

.. autoclass:: pyeda.boolalg.expr.NormalForm

.. autoclass:: pyeda.boolalg.expr.DisjNormalForm

.. autoclass:: pyeda.boolalg.expr.ConjNormalForm

.. autoclass:: pyeda.boolalg.expr.DimacsCNF

