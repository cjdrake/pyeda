"""
Interface Functions:
    boolify
    clog2
    bit_on
    cached_property
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

def boolify(arg):
    """Return an integer in {0, 1}."""
    if arg in {0, 1}:
        return arg
    num = int(arg)
    if num not in {0, 1}:
        raise ValueError("not a Boolean integer: " + str(num))
    return num

def clog2(num):
    """Return the ceiling, log base two of an integer."""
    assert num >= 1
    i, shifter = 0, 1
    while num > shifter:
        shifter <<= 1
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
            prop = self._property_cache[func] = func(self)
            return prop
        except KeyError:
            prop = self._property_cache[func] = func(self)
            return prop
    return property(get)
