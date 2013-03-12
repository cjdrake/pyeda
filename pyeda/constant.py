"""
Boolean Constant Functions

Interface Classes:
    Constant
        Zero
        One
"""

from pyeda.common import boolify, iter_space
from pyeda.boolfunc import Function


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
        return One(self.support)

    def __add__(self, other):
        return other

    def __mul__(self, other):
        return self

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
        return Zero(self.support)

    def __add__(self, other):
        return self

    def __mul__(self, other):
        return other

    def satisfy_one(self):
        return {}

    def satisfy_all(self):
        vs = sorted(self.support)
        for point in iter_space(vs):
            yield point

    def satisfy_count(self):
        return 2 ** self.degree
