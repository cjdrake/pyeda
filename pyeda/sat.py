"""
Boolean Satisfiability

Interface Classes:
    DPLLInterface

Interface Functions:
    backtrack
    iter_backtrack
    dpll
"""

import random


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


def backtrack(bf):
    """
    If this function is satisfiable, return a satisfying input upoint.
    Otherwise, return None.
    """
    if bf.is_zero():
        ret = None
    elif bf.is_one():
        ret = frozenset(), frozenset()
    else:
        v = bf.top
        #v = random.choice(bf.inputs)
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        for upnt in [upnt0, upnt1]:
            bt_upnt = backtrack(bf.urestrict(upnt))
            if bt_upnt is not None:
                ret = (upnt[0] | bt_upnt[0], upnt[1] | bt_upnt[1])
                break
        else:
            ret = None
    return ret

def iter_backtrack(bf, rand=False):
    """Iterate through all satisfying points using backtrack algorithm."""
    if bf.is_one():
        yield frozenset(), frozenset()
    elif not bf.is_zero():
        if rand:
            v = random.choice(bf.inputs) if rand else bf.top
        else:
            v = bf.top
        upnt0 = frozenset([v.uniqid]), frozenset()
        upnt1 = frozenset(), frozenset([v.uniqid])
        upoints = [upnt0, upnt1]
        if rand:
            random.shuffle(upoints)
        for upnt in upoints:
            for bt_upnt in iter_backtrack(bf.urestrict(upnt), rand):
                yield (upnt[0] | bt_upnt[0], upnt[1] | bt_upnt[1])

def dpll(cnf):
    """
    Davis-Putnam-Logemann-Loveland (DPLL) Algorithm
    """
    if cnf.is_zero():
        ret = None
    elif cnf.is_one():
        ret = frozenset(), frozenset()
    else:
        # 1. Boolean constraint propagation
        bcp_upnt = cnf.bcp()
        if bcp_upnt is None:
            # BCP found a contradiction
            ret = None
        else:
            bcp_cnf = cnf.urestrict(bcp_upnt)
            if bcp_cnf.is_one():
                # BCP found a solution
                ret = bcp_upnt
            else:
                # 2. Pure literal elimination
                ple_upnt = bcp_cnf.ple()
                bcp_ple_cnf = bcp_cnf.urestrict(ple_upnt)
                bcp_ple_upnt = (bcp_upnt[0] | ple_upnt[0],
                                bcp_upnt[1] | ple_upnt[1])
                if bcp_ple_cnf.is_one():
                    # PLE found a solution
                    ret = bcp_ple_upnt
                else:
                    # 3. Variable selection heuristic
                    v = bcp_ple_cnf.top
                    #v = random.choice(bcp_ple_cnf.inputs)

                    # 4. Backtrack
                    upnt0 = (bcp_ple_upnt[0] | {v.uniqid}, bcp_ple_upnt[1])
                    upnt1 = (bcp_ple_upnt[0], bcp_ple_upnt[1] | {v.uniqid})
                    for upnt in [upnt0, upnt1]:
                        bt_upnt = dpll(bcp_ple_cnf.urestrict(upnt))
                        if bt_upnt is not None:
                            # Backtrack found a solution
                            ret = (upnt[0] | bt_upnt[0], upnt[1] | bt_upnt[1])
                            break
                    else:
                        # Backtrack found a contradiction
                        ret = None
    return ret
