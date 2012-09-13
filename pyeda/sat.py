"""
Boolean Satisfiability
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

def naive_sat_one(expr):
    """
    If this function is satisfiable, return a satisfying input point. A
    tautology *may* return an empty dictionary; a contradiction *must*
    return None.

    >>> from pyeda import var
    >>> a, b, c = map(var, "abc")
    >>> point = (-a * b).satisfy_one(algorithm='naive')
    >>> sorted(point.items())
    [(a, 0), (b, 1)]
    >>> (-a * -b + -a * b + a * -b + a * b).satisfy_one(algorithm='naive')
    {}
    >>> (a * b * (-a + -b)).satisfy_one(algorithm='naive')
    """
    var = expr.top
    cfs = {p[var]: cf for p, cf in expr.iter_cofactors(var)}
    if cfs[0] == 1:
        if cfs[1] == 1:
            # tautology
            point = {}
        else:
            # var=0 satisfies the formula
            point = {var: 0}
    elif cfs[1] == 1:
        # var=1 satisfies the formula
        point = {var: 1}
    else:
        for num, cf in cfs.items():
            if cf != 0:
                point = naive_sat_one(cf)
                if point is not None:
                    point[var] = num
                    break
        else:
            point = None
    return point
