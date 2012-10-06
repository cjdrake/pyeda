"""
Dimacs
"""

from expr import var, Not, Or, And, Xor, Equal
from vexpr import bitvec

PREAMBLE, CNF, SAT = range(3)

def parse(stream):
    state = PREAMBLE
    args = list()
    for i, line in enumerate(stream.splitlines()):
        if state == PREAMBLE:
            if line.startswith('c'):
                pass
            elif line.startswith('p'):
                sp = line.split()
                if len(sp) == 2:
                    fmt, nvars, nargs = sp[0], sp[1], None
                elif len(sp) == 3:
                    fmt, nvars, nargs = sp
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
                args += [int(n) for n in line.split()]
            except ValueError:
                raise SyntaxError("line {}: {}".format(i, line))
        elif state == SAT:
            raise NotImplementedError("SAT format not supported yet")

#def emit(expr):
#    pass

# load, dump
# file input or string input?
