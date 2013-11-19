"""
PicoSAT Interface

Constants:
    PICOSAT_IMPORTED
    PICOSAT_VERSION
    PICOSAT_COPYRIGHT

Exceptions:
    PicosatError

Interface Functions:
    satisfy_one
    satisfy_all
"""

# Disable import problems
# pylint: disable=E0611
# pylint: disable=F0401

try:
    from pyeda.boolalg import _picosat
except ImportError:
    PICOSAT_IMPORTED = False
    PICOSAT_VERSION = None
    PICOSAT_COPYRIGHT = None
    # pylint: disable=C0103
    PicosatError = None
else:
    PICOSAT_IMPORTED = True
    PICOSAT_VERSION = _picosat.PICOSAT_VERSION
    PICOSAT_COPYRIGHT = _picosat.PICOSAT_COPYRIGHT
    # pylint: disable=C0103
    PicosatError = _picosat.PicosatError

def satisfy_one(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
                decision_limit=-1):
    """
    If the input CNF is satisfiable, return a satisfying input point.
    A contradiction will return None.

    Parameters
    ----------
    cnf : DimacsCNF

    verbosity : int, optional
        Set verbosity level. A verbosity level of 1 and above prints more and
        more detailed progress reports to stdout.

    default_phase : {0, 1, 2, 3}
        Set default initial phase:
            0 = false
            1 = true
            2 = Jeroslow-Wang (default)
            3 = random

    progagation_limit : int
        Set a limit on the number of propagations. A negative value sets no
        propagation limit.

    decision_limit : int
        Set a limit on the number of decisions. A negative value sets no
        decision limit.

    Returns
    -------
    tuple of {-1, 0, 1}
        -1 : zero
         0 : dont-care
         1 : one
    """
    return _picosat.satisfy_one(cnf.nvars, cnf.clauses,
                                verbosity, default_phase, propagation_limit,
                                decision_limit)

def satisfy_all(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
                decision_limit=-1):
    """
    Iterate through all satisfying input points.

    Parameters
    ----------
    cnf : DimacsCNF

    verbosity : int, optional
        Set verbosity level. A verbosity level of 1 and above prints more and
        more detailed progress reports to stdout.

    default_phase : {0, 1, 2, 3}
        Set default initial phase:
            0 = false
            1 = true
            2 = Jeroslow-Wang (default)
            3 = random

    progagation_limit : int
        Set a limit on the number of propagations. A negative value sets no
        propagation limit.

    decision_limit : int
        Set a limit on the number of decisions. A negative value sets no
        decision limit.

    Returns
    -------
    iter of tuple of {-1, 0, 1}
        -1 : zero
         0 : dont-care
         1 : one
    """
    return _picosat.satisfy_all(cnf.nvars, cnf.clauses,
                                verbosity, default_phase, propagation_limit,
                                decision_limit)
