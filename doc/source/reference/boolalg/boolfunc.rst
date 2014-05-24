.. reference/boolalg/boolfunc.rst

*******************************************************
  :mod:`pyeda.boolalg.boolfunc` --- Boolean Functions
*******************************************************

.. automodule:: pyeda.boolalg.boolfunc

Interface Functions
===================

.. autofunction:: pyeda.boolalg.boolfunc.num2point

.. autofunction:: pyeda.boolalg.boolfunc.num2upoint

.. autofunction:: pyeda.boolalg.boolfunc.num2term

.. autofunction:: pyeda.boolalg.boolfunc.point2upoint

.. autofunction:: pyeda.boolalg.boolfunc.point2term

.. autofunction:: pyeda.boolalg.boolfunc.iter_points

.. autofunction:: pyeda.boolalg.boolfunc.iter_upoints

.. autofunction:: pyeda.boolalg.boolfunc.iter_terms

.. autofunction:: pyeda.boolalg.boolfunc.vpoint2point

Interface Classes
=================

.. autoclass:: pyeda.boolalg.boolfunc.Variable
   :members: __lt__,
             name,
             qualname
   :member-order: bysource

.. autoclass:: pyeda.boolalg.boolfunc.Function
   :members: __invert__, __or__, __and__, __xor__,
             __add__, __mul__,
             support, usupport, inputs, top,
             degree, cardinality,
             iter_domain, iter_image, iter_relation,
             restrict, vrestrict, compose,
             satisfy_one, satisfy_all, satisfy_count,
             iter_cofactors, cofactors,
             smoothing, consensus, derivative,
             is_zero, is_one,
             box, unbox
   :member-order: bysource

