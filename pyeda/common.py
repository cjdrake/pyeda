"""
Interface Functions:
    bit_on
    clog2
    parity
    boolify
    pcify
    cached_property
"""

# Positional Cube Notation
PC_VOID, PC_ONE, PC_ZERO, PC_DC = range(4)

BOOL_DICT = {
    0: 0,
    1: 1,
    '0': 0,
    '1': 1,
}

PC_DICT = {
    0: PC_ZERO,
    1: PC_ONE,
    '0': PC_ZERO,
    '1': PC_ONE,
    'x': PC_DC,
    'X': PC_DC,
    '-': PC_DC,
}

def bit_on(num, bit):
    """Return the value of a number's bit position.

    >>> [bit_on(42, i) for i in range(clog2(42))]
    [0, 1, 0, 1, 0, 1]
    """
    return (num >> bit) & 1

def clog2(num):
    """Return the ceiling log base two of an integer >= 1.

    This function tells you the minimum dimension of a Boolean space with at
    least N points.

    >>> [clog2(n) for n in range(1, 18)]
    [0, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5]

    >>> clog2(0)
    Traceback (most recent call last):
        ...
    ValueError: num must be >= 1
    """
    if num < 1:
        raise ValueError("num must be >= 1")
    accum, shifter = 0, 1
    while num > shifter:
        shifter <<= 1
        accum += 1
    return accum

def parity(num):
    """Return the parity of the number.

    >>> [parity(n) for n in range(10)]
    [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
    >>> parity(-1)
    Traceback (most recent call last):
        ...
    ValueError: num must be >= 0
    """
    if num < 0:
        raise ValueError("num must be >= 0")
    p = 0
    while num:
        p ^= (num & 1)
        num >>= 1
    return p

def boolify(arg):
    """Convert arg to an integer in B = {0, 1}.

    >>> [boolify(x) for x in (False, True, 0, 1, '0', '1')]
    [0, 1, 0, 1, 0, 1]
    >>> boolify(42)
    Traceback (most recent call last):
        ...
    ValueError: arg not in {0, 1}
    """
    try:
        return BOOL_DICT[arg]
    except KeyError:
        raise ValueError("arg not in {0, 1}")

def pcify(arg):
    """Convert arg to a positional cube value.

    >>> [pcify(x) for x in (False, True, 0, 1, '0', '1', 'x', 'X', '-')]
    [2, 1, 2, 1, 2, 1, 3, 3, 3]
    >>> pcify(42)
    Traceback (most recent call last):
        ...
    ValueError: arg not in {0, 1, X, -}
    """
    try:
        return PC_DICT[arg]
    except KeyError:
        raise ValueError("arg not in {0, 1, X, -}")

def cached_property(func):
    """Return a cached property calculated by input function."""
    def get(self):
        try:
            return self._property_cache[func]
        except AttributeError:
            self._property_cache = {}
            prop = self._property_cache[func] = func(self)
            return prop
        except KeyError:
            prop = self._property_cache[func] = func(self)
            return prop
    return property(get)
