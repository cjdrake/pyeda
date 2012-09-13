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

from pyeda.common import iter_space
from pyeda.boolfunc import Function

BOOL_DICT = {
    0: 0,
    1: 1,
    "0": 0,
    "1": 1
}

def boolify(arg):
    """Convert 'arg' to an integer in B = {0, 1}.

    >>> [boolify(x) for x in (False, True, 0, 1, "0", "1", ZERO, ONE)]
    [0, 1, 0, 1, 0, 1, 0, 1]
    >>> boolify(42)
    Traceback (most recent call last):
        ...
    ValueError: arg not in {0, 1}
    """
    try:
        return BOOL_DICT[arg]
    except KeyError:
        raise ValueError("arg not in {0, 1}")


class Constant(Function):
    """Constant Boolean Function, either Zero or One."""

    def __init__(self, support=None):
        if support is None:
            self._support = set()
        else:
            self._support = support

    def __str__(self):
        return str(self.VAL)

    # From Function
    @property
    def support(self):
        return self._support

    def restrict(self, mapping):
        return self

    def compose(self, mapping):
        return self

    # Specific to Constant
    def __bool__(self):
        return bool(self.VAL)

    def __eq__(self, other):
        """Overloaded equals '==' operator

        >>> ZERO == ONE
        False
        >>> ZERO == 0, ZERO == 1, ONE == 0, ONE == 1
        (True, False, False, True)
        """
        if isinstance(other, Constant):
            return self.VAL == other.VAL
        else:
            return self.VAL == other

    def __hash__(self):
        return self.VAL

    def __int__(self):
        return self.VAL

    def __repr__(self):
        return self.__str__()


class Zero(Constant):
    """Proxy class for the number zero."""

    VAL = 0

    def __init__(self, support=None):
        super(Zero, self).__init__(support)

    def __neg__(self):
        return 1

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return _invert(other)

    def __mul__(self, other):
        return 0

    def __rshift__(self, other):
        return 1

    def __rrshift__(self, other):
        return _invert(other)

    def satisfy_one(self):
        return None

    def satisfy_all(self):
        return iter([])

    def satisfy_count(self):
        return 0


class One(Constant):
    """Proxy class for the number one."""

    VAL = 1

    def __init__(self, support=None):
        super(One, self).__init__(support)

    def __neg__(self):
        return 0

    def __add__(self, other):
        return 1

    def __sub__(self, other):
        return 1

    def __mul__(self, other):
        return other

    def __rshift__(self, other):
        return other

    def __rrshift__(self, other):
        return 1

    def satisfy_one(self):
        return {}

    def satisfy_all(self):
        vs = sorted(self.support)
        for point in iter_space(vs):
            yield point

    def satisfy_count(self):
        return 2 ** self.degree


ZERO = Zero()
ONE = One()


def _invert(arg):
    if isinstance(arg, Function):
        return -arg
    else:
        return 1 - boolify(arg)
