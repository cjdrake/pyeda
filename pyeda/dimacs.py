"""
Dimacs
"""

from pyeda.expr import var, Not, Or, And, Xor, Equal
from pyeda.vexpr import bitvec

PREAMBLE, CNF, SAT = range(3)

def parse(stream):
    state = PREAMBLE
    clauses = [[]]
    for i, line in enumerate(stream.splitlines()):
        if state == PREAMBLE:
            if line.startswith('c'):
                pass
            elif line.startswith('p'):
                sp = line.split()
                if len(sp) == 3:
                    fmt, nvars, nargs = sp[1], sp[2], None
                elif len(sp) == 4:
                    fmt, nvars, nargs = sp[1], sp[2], sp[3]
                else:
                    raise SyntaxError("line {}: {}".format(i, line))
                try:
                    nvars = int(nvars)
                except ValueError:
                    raise SyntaxError("invalid VARIABLES: " + nvars)
                if nvars <= 0:
                    raise SyntaxError("invalid VARIABLES: " + nvars)
                X = bitvec('x', (1, nvars+1))
                if fmt == 'cnf':
                    state = CNF
                elif fmt == 'sat':
                    state = SAT
                else:
                    raise SyntaxError("invalid FORMAT: " + fmt)
        elif state == CNF:
            try:
                nums = [int(n) for n in line.split()]
            except ValueError:
                raise SyntaxError("line {}: {}".format(i, line))
            for num in nums:
                if num == 0:
                    clauses.append([])
                else:
                    try:
                        clauses[-1].append(-X[-num] if num < 0 else X[num])
                    except IndexError:
                        raise ValueError("invalid number: " + str(num))
        elif state == SAT:
            raise NotImplementedError("SAT format not supported yet")

    # Assume CNF
    return And(*[Or(*clause) for clause in clauses])
