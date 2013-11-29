.. _queens:

********************************************
  All Solutions To The Eight Queens Puzzle
********************************************

The **eight queens** puzzle is the problem of placing eight chess queens on an
8x8 chessboard so that no two queens attack each other.
It is a classic demonstration of finding the solutions to a constraint problem.

In this essay we will use the PyEDA SAT solver to find all solutions to the eight queens puzzle.

Getting Started
===============

First, import all the standard symbols from PyEDA.

::

   >>> from pyeda.inter import *

Setting Up the Chess Board
==========================

A chess board is an 8x8 **grid**.
Each square on the grid either has a queen on it, or doesn't.
Therefore, we can represent the board using a two-dimensional bit vector, ``X``.

::

   >>> X = bitvec('x', 8, 8)

Constraints
===========

Row and Column Constraints
--------------------------

Rather than start with the constraint that :math:`\sum X_{i,j} = 8`,
we will instead start with a simplifying observation.
In order to place eight queens on the board,
since there are exactly eight rows and eight columns on the board itself,
it is obvious that exactly one queen must be placed on each row,
and each column.

First, we write a constraint that says
"exactly one queen must be placed on each row".

::

   >>> R = And(*[OneHot(*[X[r][c] for c in range(8)]) for r in range(8)])

Next, we write a constraint that says
"exactly one queen must be placed on each column".

::

   >>> C = And(*[OneHot(*[X[r][c] for r in range(8)]) for c in range(8)])

Diagonal Constraints
--------------------

Diagonal constraints are easy to visualize, but slightly trickier to specify mathematically.
We will break down the diagonal constraints into two separate sets:

* left-to-right
* right-to-left

In both cases, the diagonal is always oriented "bottom-to-top".

In both cases, we need to write a constraint that says
"at most one queen can be located on each diagonal".

::

   >>> starts = [(i, 0) for i in range(6, 0, -1)] + [(0, i) for i in range(7)]
   >>> lrdiags = []
   >>> for r, c in starts:
   ...     lrdiags.append([])
   ...     ri, ci = r, c
   ...     while ri < 8 and ci < 8:
   ...         lrdiags[-1].append((ri, ci))
   ...         ri += 1
   ...         ci += 1
   ...
   >>> DLR = And(*[OneHot0(*[X[r][c] for r, c in diag]) for diag in lrdiags])

::

   >>> starts = [(i, 7) for i in range(6, -1, -1)] + [(0, i) for i in range(6, 0, -1)]
   >>> rldiags = []
   >>> for r, c in starts:
   ...     rldiags.append([])
   ...     ri, ci = r, c
   ...     while ri < 8 and ci >= 0:
   ...         rldiags[-1].append((ri, ci))
   ...         ri += 1
   ...         ci -= 1
   ...
   >>> DRL = And(*[OneHot0(*[X[r][c] for r, c in diag]) for diag in rldiags])

Putting It All Together
-----------------------

Now that we have constraints for rows, columns, and diagonals,
we have successfully defined all rules for solving the puzzle.
Put them all together using the And function,
because all constraints must simultaneously be valid.

::

   >>> S = R * C * DLR * DRL

Verify the formula is in CNF form, and show how large it is::

   >>> S.is_cnf()
   True
   >>> len(S.args)
   744

Display Method
==============

For convenience,
let's define a function display to conveniently convert a solution point to
ASCII:

::

   >>> def display(point):
   ...     chars = list()
   ...     for r in range(8):
   ...         for c in range(8):
   ...             if point[X[r][c]]:
   ...                 chars.append("Q")
   ...             else:
   ...                 chars.append(".")
   ...         if r != 7:
   ...             chars.append("\n")
   ...     print("".join(chars))

Find a Single Solution
======================

Find a single solution to the puzzle using the `satisfy_one` method::

   >>> display(S.satisfy_one())

   .......Q
   ...Q....
   Q.......
   ..Q.....
   .....Q..
   .Q......
   ......Q.
   ....Q...

Find All Solutions
==================

Part of the challenge of the eight queens puzzle is to not just find a
single solution,
but find all solutions.
Use the `satisfy_all` method to iterate through all solutions::

   >>> for i, soln in enumerate(S.satisfy_all()):
   ...     print("Solution", i+1, end="\n\n")
   ...     display(soln)
   ...     print("")

   Solution 1

   .......Q
   ...Q....
   Q.......
   ..Q.....
   .....Q..
   .Q......
   ......Q.
   ....Q...

   ...

It is easy to verify that there are exactly 92 distinct solutions to the puzzle::

   >>> len(list(S.satisfy_all()))
   92
