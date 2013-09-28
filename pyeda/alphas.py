"""
Alphabetic Variables
"""

# Disable "invalid variable name", "line too long"
# pylint: disable=C0103
# pylint: disable=C0301

from pyeda.expr import exprvar

ALPHAS = "abcdeijklmnopqrstuvwxyz"

(a, b, c, d, e, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z) = map(exprvar, ALPHAS)
