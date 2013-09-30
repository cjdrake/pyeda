"""
PicoSAT Interface

Constants:
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
    from pyeda.boolalg._picosat import solve as _solve
    from pyeda.boolalg._picosat import PicosatError
except ImportError:
    PICOSAT_IMPORTED = False
else:
    PICOSAT_IMPORTED = True

def solve(cnf, verbosity=0, default_phase=2, propagation_limit=-1,
          decision_limit=-1):
    """
    If the input CNF is satisfiable, return a satisfyint input point.
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
