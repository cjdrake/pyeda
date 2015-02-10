.. reference/boolalg/espresso.rst

**********************************************************
  :mod:`pyeda.boolalg.espresso` --- Espresso C Extension
**********************************************************

Constants
=========

.. data:: FTYPE

.. data:: DTYPE

.. data:: RTYPE

Exceptions
==========

.. exception:: espresso.Error

   An error happened inside Espresso.

Interface Functions
===================

.. function:: get_config()

   Return a dict of Espresso global configuration values.

.. function:: set_config(single_expand=0, remove_essential=0, force_irredundant=0, unwrap_onset=0, recompute_onset=0, use_super_gasp=0, skip_make_sparse=0)

   Set Espresso global configuration values.

.. function:: espresso(ninputs, noutputs, cover, intype=FTYPE|DTYPE)

   Return a logically equivalent, (near) minimal cost set of product-terms
   to represent the ON-set and optionally minterms that lie in the DC-set,
   without containing any minterms of the OFF-set.

   Parameters

   ninputs : posint
       Number of inputs in the implicant in-part vector.

   noutputs : posint
       Number of outputs in the implicant out-part vector.

   cover : iter(((int), (int)))
       The iterator over multi-output implicants.
       A multi-output implicant is a pair of row vectors of dimension
       *ninputs*, and *noutputs*, respectively.
       The input part contains integers in positional cube notation,
       and the output part contains entries in {0, 1, 2}.

       * '0' means 0 for R-type covers, otherwise has no meaning.
       * '1' means 1 for F-type covers, otherwise has no meaning.
       * '2' means \"don't care\" for D-type covers, otherwise has no meaning.

   intype : int
       A flag field that indicates the type of the input cover.
       F-type = 1, D-type = 2, R-type = 4

   Returns

   set of implicants in the same format as the input cover

