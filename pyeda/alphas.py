"""
Alphabetic Variables

To grab all a, b, c, ... variables::

   >>> from pyeda.alphas import *
"""

from pyeda.expr import exprvar

ALPHAS = "abcdefghijklmnopqrstuvwxyz"

# pylint: disable=C0103
(a, b, c, d, e, f, g, h, i, j, k, l, m,
 n, o, p, q, r, s, t, u, v, w, x, y, z) = map(exprvar, ALPHAS)
