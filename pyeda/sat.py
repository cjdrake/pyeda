"""
Boolean Satisfiability

Interface classes:
    DPLLInterface

Interface functions:
    backtrack
    dpll
"""

#import random


class DPLLInterface(object):
    """DPLL algorithm interface"""

    def bcp(self):
        """Boolean Constraint Propagation

        Return an untyped point that results from unit propagation.
        If BCP detects a contradiction, return None.
        """
        raise NotImplementedError()

    def ple(self):
        """Pure Literal Elimination

        Return an untyped point that results from pure literal elimination.
        If PLE detects a contradiction, return None.
        """
        raise NotImplementedError()


def backtrack(expr):
    """
    If this function is satisfiable, return a satisfying input upoint.
    Otherwise, return None.
    """
    if expr.is_zero():
        return None
    elif expr.is_one():
        return frozenset(), frozenset()
    else:
        v = expr.top
        #v = random.choice(expr.inputs)

        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            bt_upnt = backtrack(expr.urestrict(upnt))
            if bt_upnt is not None:
                return (upnt[0] | bt_upnt[0], upnt[1] | bt_upnt[1])

        return None

def dpll(cnf):
    """
    Davis-Putnam-Logemann-Loveland (DPLL) Algorithm
    """
    if cnf.is_zero():
        return None
    elif cnf.is_one():
        return frozenset(), frozenset()
    else:
        # 1. Boolean constraint propagation
        bcp_upnt = cnf.bcp()
        if bcp_upnt is None:
            # BCP found a contradiction
            return None
        else:
            bcp_cnf = cnf.urestrict(bcp_upnt)
            if bcp_cnf.is_one():
                # BCP found a solution
                return bcp_upnt

        # 2. Pure literal elimination
        ple_upnt = bcp_cnf.ple()
        if ple_upnt is None:
            # PLE found a contradiction (FIXME: not sure this is possible)
            return None
        else:
            bcp_ple_cnf = bcp_cnf.urestrict(ple_upnt)
            bcp_ple_upnt = (bcp_upnt[0] | ple_upnt[0],
                            bcp_upnt[1] | ple_upnt[1])
            if bcp_ple_cnf.is_one():
                # PLE found a solution
                return bcp_ple_upnt

        # 3. Variable selection heuristic
        v = bcp_ple_cnf.top
        #v = random.choice(bcp_ple_cnf.inputs)

        # 4. Backtracking
        upnt0 = (bcp_ple_upnt[0] | {v.uniqid}, bcp_ple_upnt[1])
        upnt1 = (bcp_ple_upnt[0], bcp_ple_upnt[1] | {v.uniqid})
        for upnt in [upnt0, upnt1]:
            bt_upnt = dpll(bcp_ple_cnf.urestrict(upnt))
            if bt_upnt is not None:
                return (upnt[0] | bt_upnt[0], upnt[1] | bt_upnt[1])

        return None
