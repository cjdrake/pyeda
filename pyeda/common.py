"""
Interface Functions:
    bit_on
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

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
