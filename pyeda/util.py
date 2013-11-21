"""
Utility Functions

Interface Functions:
    bit_on
    clog2
    parity
    boolify
    cached_property
"""

BOOL_DICT = {
    0: 0,
    1: 1,
    '0': 0,
    '1': 1,
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
    ValueError: expected num >= 1
    """
    if num < 1:
        raise ValueError("expected num >= 1")
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
    ValueError: expected num >= 0
    """
    if num < 0:
        raise ValueError("expected num >= 0")
    par = 0
    while num:
        par ^= (num & 1)
        num >>= 1
    return par

def boolify(arg):
    """Convert arg to an integer in B = {0, 1}.

    >>> [boolify(x) for x in (False, True, 0, 1, '0', '1')]
    [0, 1, 0, 1, 0, 1]
    >>> boolify(42)
    Traceback (most recent call last):
        ...
    ValueError: expected arg in {0, 1}
    """
    try:
        return BOOL_DICT[arg]
    except KeyError:
        raise ValueError("expected arg in {0, 1}")

def cached_property(func):
    """Return a cached property calculated by the input function.

    Unlike the 'property' decorator from the standard library, this decorator
    will cache the return value in order to avoid repeated calculations. This
    is particularly useful when the property involves some non-trivial
    computation.
    """
    # pylint: disable=W0212
    def get(self):
        """Return the cached property."""
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
