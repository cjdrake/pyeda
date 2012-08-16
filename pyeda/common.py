"""
Interface Functions:
    bit_on
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

def bit_on(num, bit):
    """Return the truth value of a number's bit position."""
    return bool((num >> bit) & 1)
