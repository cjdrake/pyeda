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
    # Split the formula into var=0 and var=1 cofactors
    cf0, cf1 = expr.cofactors(var)
    if cf0 == 1:
        if cf1 == 1:
            # tautology
            point = {}
        else:
            # var=0 satisfies the formula
            point = {var: 0}
    elif cf1 == 1:
        # var=1 satisfies the formula
        point = {var: 1}
    else:
        for num, cf in [(0, cf0), (1, cf1)]:
            if cf != 0:
                point = naive_sat_one(cf)
                if point is not None:
                    point[var] = num
                    break
        else:
            point = None
    return point
