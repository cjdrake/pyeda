.. reference/boolalg/bfarray.rst

************************************************************
  :mod:`pyeda.boolalg.bfarray` --- Boolean Function Arrays
************************************************************

.. automodule:: pyeda.boolalg.bfarray

Interface Functions
===================

.. autofunction:: pyeda.boolalg.bfarray.bddzeros

.. autofunction:: pyeda.boolalg.bfarray.bddones

.. autofunction:: pyeda.boolalg.bfarray.bddvars

.. autofunction:: pyeda.boolalg.bfarray.exprzeros

.. autofunction:: pyeda.boolalg.bfarray.exprones

.. autofunction:: pyeda.boolalg.bfarray.exprvars

.. autofunction:: pyeda.boolalg.bfarray.ttzeros

.. autofunction:: pyeda.boolalg.bfarray.ttones

.. autofunction:: pyeda.boolalg.bfarray.ttvars

.. autofunction:: pyeda.boolalg.bfarray.uint2bdds

.. autofunction:: pyeda.boolalg.bfarray.uint2exprs

.. autofunction:: pyeda.boolalg.bfarray.uint2tts

.. autofunction:: pyeda.boolalg.bfarray.int2bdds

.. autofunction:: pyeda.boolalg.bfarray.int2exprs

.. autofunction:: pyeda.boolalg.bfarray.int2tts

.. autofunction:: pyeda.boolalg.bfarray.fcat

Interface Classes
=================

.. autoclass:: pyeda.boolalg.bfarray.farray
   :members: __invert__, __or__, __and__, __xor__,
             __lshift__, __rshift__,
             __add__, __mul__,
             restrict, vrestrict, compose,
             size, offsets, ndim, reshape, flat,
             to_uint, to_int,
             zext, sext,
             uor, unor, uand, unand, uxor, uxnor,
             lsh, rsh, arsh,
             decode
   :member-order: bysource

