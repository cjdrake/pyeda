"""
Boolean Constant Functions

Interface Functions:
    boolify

Interface Classes:
    Constant
        Zero
        One
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

import random

from pyeda.common import bit_on
from pyeda.boolfunc import Function

_bool_dict = {
    0: 0,
    1: 1,
    "0": 0,
    "1": 1
}

def boolify(arg):
    """Convert 'arg' to an integer in B = {0, 1}.

    >>> [boolify(x) for x in (False, True, 0, 1, "0", "1")]
    [0, 1, 0, 1, 0, 1]

    >>> boolify(42)
    Traceback (most recent call last):
        ...
    ValueError: arg not in {0, 1}
    """
    try:
        return _bool_dict[arg]
    except KeyError:
        raise ValueError("arg not in {0, 1}")


class Constant(Function):
    """Constant Boolean Function, either Zero or One."""
    def __init__(self, val, support=None):
        self._val = val
        if support is None:
            self._support = set()
        else:
            self._support = support

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._val)

    def __eq__(self, other):
        """Overloaded equals '==' operator

        >>> zero, one = Zero(), One()
        >>> zero == one
        False
        >>> zero == 0, zero == 1, one == 0, one == 1
        (True, False, False, True)
        """
        if isinstance(other, Constant):
            return self._val == other._val
        else:
            return self._val == other

    def __bool__(self):
        return bool(self._val)

    def __int__(self):
        return self._val

    @property
    def support(self):
        return self._support

    def restrict(self, mapping):
        return self

    def compose(self, mapping):
        return self


class Zero(Constant):
    """Proxy class for the number zero."""
    def __init__(self, support=None):
        super(Zero, self).__init__(0, support)

    def op_not(self):
        """Boolean NOT operator

        >>> Zero().op_not()
        1
        """
        return One(self.support)

    def op_or(self, *args):
        """Boolean OR operator
        >>> zero, one = Zero(), One()
        >>> zero + zero, zero + one
        (0, 1)
        """
        if args:
            return args[0].op_or(*args[1:])
        else:
            return self

    def op_and(self, *args):
        """Boolean AND operator

        >>> zero, one = Zero(), One()
        >>> zero * zero, zero * one
        (0, 0)
        """
        support = self.support.copy()
        for arg in args:
            support |= arg.support
        if self.support == support:
            return self
        else:
            return Zero(support)

    def satisfy_one(self):
        return {}

    def satisfy_all(self):
        return []

    def satisfy_count(self):
        return 0


class One(Constant):
    """Proxy class for the number one."""
    def __init__(self, support=None):
        super(One, self).__init__(1, support)

    def op_not(self):
        """Boolean NOT operator

        >>> One().op_not()
        0
        """
        return Zero(self.support)

    def op_or(self, *args):
        """Boolean OR operator

        >>> zero, one = Zero(), One()
        >>> one + zero, one + one
        (1, 1)
        """
        support = self.support.copy()
        for arg in args:
            support |= arg.support
        if self.support == support:
            return self
        else:
            return One(support)

    def op_and(self, *args):
        """Boolean AND operator

        >>> zero, one = Zero(), One()
        >>> one * zero, one * one
        (0, 1)
        """
        if args:
            return args[0].op_and(*args[1:])
        else:
            return self

    def satisfy_one(self):
        return {v: random.randint(0, 1) for v in self.support}

    def satisfy_all(self):
        vs = sorted(self.support)
        return [ {v: bit_on(n, i) for i, v in enumerate(vs)}
                 for n in range(2 ** self.degree) ]

    def satisfy_count(self):
        return 2 ** self.degree
