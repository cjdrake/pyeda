"""
Interface Functions:
    clog2
    bit_on
    cached_property
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

def clog2(num):
    """Return the ceiling, log base two of an integer."""
    assert num >= 1
    i, x = 0, 1
    while x < num:
        x = x << 1;
        i += 1
    return i

def bit_on(num, bit):
    """Return the truth value of a number's bit position."""
    return bool((num >> bit) & 1)

def cached_property(func):
    """Return a cached property calculated by input function."""
    def get(self):
        try:
            return self._property_cache[func]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[func] = func(self)
            return x
        except KeyError:
            x = self._property_cache[func] = func(self)
            return x
    return property(get)
