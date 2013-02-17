"""
Dimacs

For more information on the input formats,
see "Satisfiability Suggested Format".
"""

# standard library
import collections
import re

# pyeda
from pyeda.expr import Expression, Not, Or, And, Xor, Equal
from pyeda.vexpr import bitvec

Token = collections.namedtuple('Token', ['typ', 'val', 'line', 'col'])

# lexical states
TOKENS = (
    ('WS', r'[ \t]+'),
    ('NL', r'\n'),

    ('CNF',   r'\bcnf\b'),
    ('SATEX', r'\bsatex\b'),
    ('SATX',  r'\bsatx\b'),
    ('SATE',  r'\bsate\b'),
    ('SAT',   r'\bsat\b'),

    ('c', r'c.*'),
    ('p', r'p'),

    ('ZERO',   r'0'),
    ('POSINT', r'[1-9][0-9]*'),

    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),

    ('NOT',   r'\-'),
    ('OR',    r'\+'),
    ('AND',   r'\*'),
    ('XOR',   r'xor'),
    ('EQUAL', r'='),
)

_TOP = {'POSINT', 'LPAREN', 'RPAREN', 'NOT', 'OR', 'AND', 'XOR', 'EQUAL'}

_OPS = {
    '-': Not,
    '+': Or,
    '*': And,
    'xor': Xor,
    '=': Equal,
}

_SUPPORTED = {
    'sat': {'-', '+', '*'},
    'satx': {'-', '+', '*', 'xor'},
    'sate': {'-', '+', '*', '='},
    'satex': {'-', '+', '*', 'xor', '='},
}

_regex = re.compile('|'.join("(?P<%s>%s)" % pair for pair in TOKENS))

def iter_tokens(s):
    """Iterate through all tokens in a DIMACS format input string.

    This method is common between cnf/sat/satx/sate/satex formats
    """
    line = 1
    pos = line_start = 0

    m = _regex.match(s)
    while m is not None:
        typ = m.lastgroup
        if typ == 'NL':
            line_start = pos
            line += 1
        elif typ != 'WS':
            val = m.group(typ)
            if typ in ('ZERO', 'POSINT'):
                val = int(val)
            col = m.start() - line_start
            yield Token(typ, val, line, col)
        pos = m.end()
        m = _regex.match(s, pos)
    if pos != len(s):
        fstr = "unexpected character on line {}: {}"
        raise SyntaxError(fstr.format(line, s[pos]))

def expect_token(gen, types):
    tok = gen.__next__()
    if tok.typ in types:
        return tok
    else:
        fstr = "unexpected token on line {0.line}, col {0.col}: {0.val}"
        raise SyntaxError(fstr.format(tok))

# Grammar for a CNF file
#
# CNF := COMMENT* PREAMBLE POSINT+ ('0' POSINT+)*
#
# PREAMBLE := 'p' 'cnf' VARIABLES CLAUSES
#
# FORMAT := POSINT
#
# VARIABLES := POSINT
#
# CLAUSES := POSINT

def parse_cnf(s, varname='x'):
    """Parse an input string in DIMACS CNF format, and return an expression."""
    gen = iter_tokens(s)
    try:
        while True:
            tok = expect_token(gen, {'c', 'p'})
            if tok.typ == 'p':
                break
        expect_token(gen, {'CNF'})
        nvars = expect_token(gen, {'POSINT'}).val
        ncls = expect_token(gen, {'POSINT'}).val
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))
    clauses = [[]]

    try:
        while True:
            tok = expect_token(gen, {'ZERO', 'NOT', 'POSINT'})
            if tok.typ == 'ZERO':
                clauses.append([])
            elif tok.typ == 'NOT':
                tok = expect_token(gen, {'POSINT'})
                assert tok.val <= nvars
                clauses[-1].append(-X[tok.val])
            else:
                assert tok.val <= nvars
                clauses[-1].append(X[tok.val])
    except StopIteration:
        pass

    assert len(clauses) == ncls
    return And(*[Or(*clause) for clause in clauses])

# Grammar for a SAT file
#
# SAT := COMMENT* PREAMBLE FORMULA
#
# PREAMBLE := 'p' FORMAT VARIABLES
#
# FORMAT := 'sat' | 'satx' | 'sate' | 'satex'
#
# VARIABLES := POSINT
#
# FORMULA := POSINT
#          | '-' POSINT
#          | '(' FORMULA ')'
#          | '-' '(' FORMULA ')'
#          | '+' '(' FORMULA* ')'
#          | '*' '(' FORMULA* ')'
#          | 'xor' '(' FORMULA* ')'
#          | '=' '(' FORMULA* ')'

def parse_sat(s, varname='x'):
    """Parse an input string in DIMACS SAT format, and return an expression."""
    gen = iter_tokens(s)
    try:
        while True:
            tok = expect_token(gen, {'c', 'p'})
            if tok.typ == 'p':
                break
        fmt = expect_token(gen, {'SAT', 'SATX', 'SATE', 'SATEX'}).val
        nvars = expect_token(gen, {'POSINT'}).val
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))

    stack = []
    try:
        while True:
            tok = expect_token(gen, _TOP)
            if tok.typ == 'POSINT':
                stack.append(X[tok.val])
            elif tok.typ == 'NOT':
                tok2 = expect_token(gen, {'POSINT', 'LPAREN'})
                if tok2.typ == 'POSINT':
                    stack.append(-X[tok2.val])
                else:
                    stack.append(tok)
            elif tok.typ == 'LPAREN':
                stack.append(tok)
            elif tok.typ in {'OR', 'AND', 'XOR', 'EQUAL'}:
                stack.append(tok)
                tok = expect_token(gen, {'LPAREN'})
            elif tok.typ == 'RPAREN':
                for i in range(len(stack)-1, -1, -1):
                    entry = stack[i]
                    if not isinstance(entry, Token):
                        continue
                    if entry.val in _OPS:
                        if entry.val not in _SUPPORTED[fmt]:
                            raise SyntaxError("unsupported operator")
                        stack, args = stack[:i], stack[i+1:]
                        for arg in args:
                            assert isinstance(arg, Expression)
                        stack.append(_OPS[entry.val](*args))
                        break
                    elif entry.val == '(':
                        stack, args = stack[:i], stack[i+1:]
                        assert len(args) == 1
                        stack.append(args[0])
                        break
                else:
                    raise SyntaxError("non-matching parenthesis")
    except StopIteration:
        pass

    if len(stack) != 1:
        raise SyntaxError("invalid formula")

    return stack[0]
