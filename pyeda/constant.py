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

from pyeda.common import bit_on
from pyeda.boolfunc import Function

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

    def op_not(self):
        """Boolean NOT operator

        >>> -ZERO
        1
        """
        return One(self.support)

    def op_or(self, *args):
        """Boolean OR operator
        >>> ZERO + ZERO, ZERO + ONE
        (0, 1)
        """
        if args:
            return args[0].op_or(*args[1:])
        else:
            return self

    def op_and(self, *args):
        """Boolean AND operator

        >>> ZERO * ZERO, ZERO * ONE
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

    def op_not(self):
        """Boolean NOT operator

        >>> -ONE
        0
        """
        return Zero(self.support)

    def op_or(self, *args):
        """Boolean OR operator

        >>> ONE + ZERO, ONE + ONE
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

        >>> ONE * ZERO, ONE * ONE
        (0, 1)
        """
        if args:
            return args[0].op_and(*args[1:])
        else:
            return self

    def satisfy_one(self):
        return {}

    def satisfy_all(self):
        vs = sorted(self.support)
        for n in range(2 ** self.degree):
            yield {v: bit_on(n, i) for i, v in enumerate(vs)}

    def satisfy_count(self):
        return 2 ** self.degree


ZERO = Zero()
ONE = One()


BOOL_DICT = {
    0: 0,
    1: 1,
    "0": 0,
    "1": 1
}
