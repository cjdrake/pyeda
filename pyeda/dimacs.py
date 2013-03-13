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
from pyeda.expr import Not, Or, And, Xor, Equal
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
            if typ in {'ZERO', 'POSINT'}:
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
# CNF := COMMENT* PREAMBLE FORMULA
#
# COMMENT := 'c' .*
#
# PREAMBLE := 'p' 'cnf' VARIABLES CLAUSES
#
# VARIABLES := POSINT
#
# CLAUSES := POSINT
#
# FORMULA := POSINT+ ('0' POSINT+)*

_CNF_FORMULA_TOKS = {'ZERO', 'NOT', 'POSINT'}

def parse_cnf(s, varname='x'):
    """Parse an input string in DIMACS CNF format, and return an expression."""
    gtoks = iter_tokens(s)
    try:
        nvars, ncls = _cnf_preamble(gtoks)
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))
    clauses = [[]]

    try:
        while True:
            tok = _expect_token(gtoks, _CNF_FORMULA_TOKS)
            if tok.typ == 'ZERO':
                clauses.append([])
            elif tok.typ == 'NOT':
                tok = _expect_token(gtoks, {'POSINT'})
                assert tok.val <= len(X)
                clauses[-1].append(-X[tok.val])
            else:
                assert tok.val <= len(X)
                clauses[-1].append(X[tok.val])
    except StopIteration:
        pass

    assert len(clauses) == ncls
    return And(*[Or(*clause) for clause in clauses])

def _cnf_preamble(gtoks):
    tok = _expect_token(gtoks, {'c', 'p'})
    if tok.typ == 'c':
        return _cnf_preamble(gtoks)
    else:
        _expect_token(gtoks, {'CNF'})
        nvars = _expect_token(gtoks, {'POSINT'}).val
        ncls = _expect_token(gtoks, {'POSINT'}).val
        return nvars, ncls

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

_SAT_TOKS = {'SAT', 'SATX', 'SATE', 'SATEX'}
_FORMULA_TOKS = {'POSINT', 'LPAREN', 'NOT', 'OR', 'AND', 'XOR', 'EQUAL'}

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
    gtoks = iter_tokens(s)
    try:
        tok = _expect_token(gtoks, {'c', 'p'})
        while tok.typ == 'c':
            tok = _expect_token(gtoks, {'c', 'p'})
        fmt = _expect_token(gtoks, _SAT_TOKS).typ
        nvars = _expect_token(gtoks, {'POSINT'}).val
    except StopIteration:
        raise SyntaxError("incomplete preamble")

    X = bitvec(varname, (1, nvars + 1))
    try:
        tok = _expect_token(gtoks, _FORMULA_TOKS)
        return _formula(gtoks, tok, fmt, X)
    except StopIteration:
        raise SyntaxError("incomplete formula")

def _expect_token(gtoks, types):
    tok = next(gtoks)
    if tok.typ in types:
        return tok
    else:
        fstr = "unexpected token on line {0.line}, col {0.col}: {0.val}"
        raise SyntaxError(fstr.format(tok))

def _formula(gtoks, tok, fmt, X):
    if tok.typ == 'POSINT':
        assert tok.val <= len(X)
        return X[tok.val]
    elif tok.typ == 'NOT':
        tok = _expect_token(gtoks, {'POSINT', 'LPAREN'})
        if tok.typ == 'POSINT':
            assert tok.val <= len(X)
            return -X[tok.val]
        else:
            return _one_formula(gtoks, fmt, X)
    elif tok.typ == 'LPAREN':
        return _one_formula(gtoks, fmt, X)
    # OR/AND/XOR/EQUAL
    else:
        assert tok.typ in _SAT_OPS[fmt]
        op = _OP_EXPR[tok.typ]
        tok = _expect_token(gtoks, {'LPAREN'})
        return op(*_zom_formulas(gtoks, fmt, X))

def _one_formula(gtoks, fmt, X):
    f = _formula(gtoks, next(gtoks), fmt, X)
    _expect_token(gtoks, {'RPAREN'})
    return f

def _zom_formulas(gtoks, fmt, X):
    fs = []
    tok = _expect_token(gtoks, _FORMULA_TOKS | {'RPAREN'})
    while tok.typ != 'RPAREN':
        fs.append(_formula(gtoks, tok, fmt, X))
        tok = _expect_token(gtoks, _FORMULA_TOKS | {'RPAREN'})
    return fs
