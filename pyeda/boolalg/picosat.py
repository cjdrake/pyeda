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
    PicosatError = None
else:
    PICOSAT_IMPORTED = True
    PICOSAT_VERSION = _picosat.PICOSAT_VERSION
    PICOSAT_COPYRIGHT = _picosat.PICOSAT_COPYRIGHT
    PicosatError = _picosat.PicosatError

def satisfy_one(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
                decision_limit=-1):
    """
    If the input CNF is satisfiable, return a satisfying input point.
    A contradiction will return None.

    Keyword Arguments:
        verbosity
        default_phase
        progagation_limit
        decision_limit
    """
    assert verbosity >= 0
    assert default_phase in range(4)
    assert propagation_limit >= -1
    assert decision_limit >= -1

    return _picosat.satisfy_one(cnf.nvars, cnf.clauses,
                                verbosity, default_phase, propagation_limit,
                                decision_limit)

def satisfy_all(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
                decision_limit=-1):
    """
    Iterate through all satisfying input points.

    Keyword Arguments:
        verbosity
        default_phase
        progagation_limit
        decision_limit
    """
    assert verbosity >= 0
    assert default_phase in range(4)
    assert propagation_limit >= -1
    assert decision_limit >= -1

    return _picosat.satisfy_all(cnf.nvars, cnf.clauses,
                                verbosity, default_phase, propagation_limit,
                                decision_limit)
