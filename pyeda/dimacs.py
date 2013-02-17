"""
Dimacs

For more information on the input formats,
see "Satisfiability Suggested Format".

Interface Functions:
    parse_cnf
    parse_sat
"""

# standard library
import collections
import re

# pyeda
from pyeda.expr import Expression, Not, Or, And, Xor, Equal
from pyeda.vexpr import bitvec

Token = collections.namedtuple('Token', ['typ', 'val', 'line', 'col'])

# lexical states
_TOK_RE = (
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
    ('XOR',   r'\bxor\b'),
    ('EQUAL', r'='),
)

_regex = re.compile('|'.join("(?P<%s>%s)" % pair for pair in _TOK_RE))

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
            tok = _expect_token(gen, {'c', 'p'})
            if tok.typ == 'p':
                break
        _expect_token(gen, {'CNF'})
        nvars = _expect_token(gen, {'POSINT'}).val
        ncls = _expect_token(gen, {'POSINT'}).val
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))
    clauses = [[]]

    try:
        while True:
            tok = _expect_token(gen, {'ZERO', 'NOT', 'POSINT'})
            if tok.typ == 'ZERO':
                clauses.append([])
            elif tok.typ == 'NOT':
                tok = _expect_token(gen, {'POSINT'})
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

_FORMULA = {'POSINT', 'LPAREN', 'NOT', 'OR', 'AND', 'XOR', 'EQUAL'}

_ZOM_FORMULAS = {'POSINT', 'LPAREN', 'RPAREN',
                 'NOT', 'OR', 'AND', 'XOR', 'EQUAL'}

_SAT_OPS = {
    'SAT': {'NOT', 'OR', 'AND'},
    'SATX': {'NOT', 'OR', 'AND', 'XOR'},
    'SATE': {'NOT', 'OR', 'AND', 'EQUAL'},
    'SATEX': {'NOT', 'OR', 'AND', 'XOR', 'EQUAL'},
}

_OP_EXPR = {
    'NOT': Not,
    'OR': Or,
    'AND': And,
    'XOR': Xor,
    'EQUAL': Equal,
}

def parse_sat(s, varname='x'):
    """Parse an input string in DIMACS SAT format, and return an expression."""
    gen = iter_tokens(s)
    try:
        while True:
            tok = _expect_token(gen, {'c', 'p'})
            if tok.typ == 'p':
                break
        fmt = _expect_token(gen, {'SAT', 'SATX', 'SATE', 'SATEX'}).typ
        nvars = _expect_token(gen, {'POSINT'}).val
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))
    try:
        return _formula(gen, fmt, X)
    except StopIteration:
        raise SyntaxError("incomplete formula")

def _expect_token(gen, types):
    tok = gen.__next__()
    if tok.typ in types:
        return tok
    else:
        fstr = "unexpected token on line {0.line}, col {0.col}: {0.val}"
        raise SyntaxError(fstr.format(tok))

def _formula(gen, fmt, X):
    tok = _expect_token(gen, _FORMULA)
    if tok.typ == 'POSINT':
        return X[tok.val]
    elif tok.typ == 'NOT':
        tok2 = _expect_token(gen, {'POSINT', 'LPAREN'})
        if tok2.typ == 'POSINT':
            return -X[tok2.val]
        else:
            return _one_formula(gen, fmt, X)
    elif tok.typ == 'LPAREN':
        return _one_formula(gen, fmt, X)
    # OR/AND/XOR/EQUAL
    else:
        if tok.typ not in _SAT_OPS[fmt]:
            raise SyntaxError("unsupported operator: " + tok.val)
        tok2 = _expect_token(gen, {'LPAREN'})
        fs = _get_fs(gen, fmt, X)
        return _OP_EXPR[tok.typ](*fs)

def _one_formula(gen, fmt, X):
    f = _formula(gen, fmt, X)
    _expect_token(gen, {'RPAREN'})
    return f

def _zom_formulas(gen, fmt, X):
    tok = _expect_token(gen, _ZOM_FORMULAS)
    if tok.typ == 'POSINT':
        return X[tok.val]
    elif tok.typ == 'NOT':
        tok2 = _expect_token(gen, {'POSINT', 'LPAREN'})
        if tok2.typ == 'POSINT':
            return -X[tok2.val]
        else:
            return _one_formula(gen, fmt, X)
    elif tok.typ == 'LPAREN':
        return _one_formula(gen, fmt, X)
    elif tok.typ in {'OR', 'AND', 'XOR', 'EQUAL'}:
        if tok.typ not in _SAT_OPS[fmt]:
            raise SyntaxError("unsupported operator: " + tok.val)
        tok2 = _expect_token(gen, {'LPAREN'})
        fs = _get_fs(gen, fmt, X)
        return _OP_EXPR[tok.typ](*fs)
    # RPAREN
    else:
        return None

def _get_fs(gen, fmt, X):
    fs = []
    f = _zom_formulas(gen, fmt, X)
    while f is not None:
        fs.append(f)
        f = _zom_formulas(gen, fmt, X)
    return fs
