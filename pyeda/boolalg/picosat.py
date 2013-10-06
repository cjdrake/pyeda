"""
PicoSAT Interface

Constants:
    PICOSAT_VERSION
    PICOSAT_COPYRIGHT
    PICOSAT_IMPORTED

Exceptions:
    PicosatError

Interface Functions:
    solve
"""

# Disable import problems
# pylint: disable=E0611
# pylint: disable=F0401

try:
    import pyeda.boolalg._picosat
except ImportError:
    PICOSAT_VERSION = None
    PICOSAT_COPYRIGHT = None
    PICOSAT_IMPORTED = False
else:
    from pyeda.boolalg._picosat import PICOSAT_VERSION, PICOSAT_COPYRIGHT
    from pyeda.boolalg._picosat import PicosatError
    from pyeda.boolalg._picosat import solve as _solve
    from pyeda.boolalg._picosat import iter_solve as _iter_solve
    PICOSAT_IMPORTED = True

def solve(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
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

    soln = _solve(cnf.nvars, cnf.clauses,
                  verbosity, default_phase, propagation_limit, decision_limit)
    return cnf.soln2point(soln)

def iter_solve(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
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

    solns = _iter_solve(cnf.nvars, cnf.clauses,
                        verbosity, default_phase, propagation_limit,
                        decision_limit)
    for soln in solns:
        yield cnf.soln2point(soln)
