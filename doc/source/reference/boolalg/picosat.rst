.. reference/boolalg/picosat.rst

********************************************************
  :mod:`pyeda.boolalg.picosat` --- PicoSAT C Extension
********************************************************

Interface to PicoSAT SAT solver C extension

Constants
=========

.. data:: VERSION

   PicoSAT version string

.. data:: COPYRIGHT

   PicoSAT copyright statement

Exceptions
==========

.. exception:: Error

   An error happened inside PicoSAT.
   Examples include initialization errors, and unexpected return codes.

Interface Functions
===================

.. function:: satisfy_one(nvars, clauses, assumptions, verbosity=0, default_phase=2, propagation_limit=-1, decision_limit=-1)

   If the input CNF is satisfiable, return a satisfying input point.
   A contradiction will return None.

   Parameters

   nvars : posint
       Number of variables in the CNF

   clauses : iter of iter of (nonzero) int
       The CNF clauses

   assumptions : iter of (nonzero) int
       Add assumptions (unit clauses) to the CNF

   verbosity : int, optional
       Set verbosity level. A verbosity level of 1 and above prints more and
       more detailed progress reports to stdout.

   default_phase : {0, 1, 2, 3}

       Set default initial phase:
           * 0 = false
           * 1 = true
           * 2 = Jeroslow-Wang (default)
           * 3 = random

   progagation_limit : int
       Set a limit on the number of propagations. A negative value sets no
       propagation limit.

   decision_limit : int
       Set a limit on the number of decisions. A negative value sets no
       decision limit.

   Returns

   tuple of {-1, 0, 1}
       * -1 : zero
       *  0 : dont-care
       *  1 : one

.. function:: satisfy_all(nvars, clauses, verbosity=0, default_phase=2, propagation_limit=-1, decision_limit=-1)

   Iterate through all satisfying input points.

   Parameters

   nvars : posint
       Number of variables in the CNF

   clauses : iter of iter of (nonzero) int
       The CNF clauses

   verbosity : int, optional
       Set verbosity level. A verbosity level of 1 and above prints more and
       more detailed progress reports to stdout.

   default_phase : {0, 1, 2, 3}
       Set default initial phase:
           * 0 = false
           * 1 = true
           * 2 = Jeroslow-Wang (default)
           * 3 = random

   progagation_limit : int
       Set a limit on the number of propagations. A negative value sets no
       propagation limit.

   decision_limit : int
       Set a limit on the number of decisions. A negative value sets no
       decision limit.

   Returns

   iter of tuple of {-1, 0, 1}
       * -1 : zero
       *  0 : dont-care
       *  1 : one

