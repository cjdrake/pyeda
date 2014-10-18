"""
Boolean Satisfiability

Interface Functions:
    backtrack
    iter_backtrack
"""

import random


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

