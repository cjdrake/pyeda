"""
Dimacs

For more information on the input formats,
see "Satisfiability Suggested Format".

Interface Functions:
    load_cnf
    dump_cnf
    load_sat
    dump_sat
"""

# standard library
import collections
import re

# pyeda
from pyeda.expr import Expression, Literal, Not, Or, And, Xor, Equal
from pyeda.vexpr import bitvec

Token = collections.namedtuple('Token', ['typ', 'val', 'line', 'col'])

_CNF_PREAMBLE_RE = re.compile(r"(?:c.*\n)*p\s+cnf\s+([1-9][0-9]*)\s+([1-9][0-9]*)\s*\n")
_SAT_PREAMBLE_RE = re.compile(r"(?:c.*\n)*p\s+(sat|satx|sate|satex)\s+([1-9][0-9]*)\s*\n")

# lexical states
_TOK_PAIRS = (
    ('WS', r'[ \t]+'),
    ('NL', r'\n'),

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

_TOK_RE = re.compile('|'.join("(?P<{}>{})".format(*pair)
                              for pair in _TOK_PAIRS))

def _iter_tokens(s, line=1):
    """Iterate through all tokens in a DIMACS format input string.

    This method is common between cnf/sat/satx/sate/satex formats
    """
    pos = line_start = 0

    m = _TOK_RE.match(s)
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
        m = _TOK_RE.match(s, pos)
    if pos != len(s):
        fstr = "unexpected character on line {}: {}"
        raise SyntaxError(fstr.format(line, s[pos]))

def _expect_token(gtoks, types):
    tok = next(gtoks)
    if tok.typ in types:
        return tok
    else:
        fstr = "unexpected token on line {0.line}, col {0.col}: {0.val}"
        raise SyntaxError(fstr.format(tok))

# Grammar for a CNF file
#
# CNF := COMMENT* PREAMBLE FORMULA
#
# COMMENT := 'c' .* NL
#
# PREAMBLE := 'p' 'cnf' VARIABLES CLAUSES NL
#
# VARIABLES := POSINT
#
# CLAUSES := POSINT
#
# FORMULA := POSINT+ ('0' POSINT+)*

_CNF_FORMULA_TOKS = {'ZERO', 'NOT', 'POSINT'}

def load_cnf(s, varname='x'):
    """Parse an input string in DIMACS CNF format, and return an expression."""
    m = _CNF_PREAMBLE_RE.match(s)
    if m:
        nvars = int(m.group(1))
        ncls = int(m.group(2))
    else:
        raise SyntaxError("incorrect preamble")

    ps, fs = s[:m.end()], s[m.end():]
    line = ps.count('\n') + 1

    gtoks = _iter_tokens(fs, line)
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
            elif tok.typ == 'POSINT':
                assert tok.val <= len(X)
                clauses[-1].append(X[tok.val])
    except StopIteration:
        pass

    assert len(clauses) == ncls
    return And(*[Or(*clause) for clause in clauses])

def dump_cnf(expr):
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")
    if not expr.is_cnf():
        raise ValueError("expression is not a CNF")
    formula = " 0\n".join(" ".join(str(arg.gnum) for arg in clause.args)
                          for clause in expr.args)
    nvars = max(v.gnum for v in expr.support)
    ncls = len(expr.args)
    return "p cnf {} {}\n{}".format(nvars, ncls, formula)

# Grammar for a SAT file
#
# SAT := COMMENT* PREAMBLE FORMULA
#
# COMMENT := 'c' .* NL
#
# PREAMBLE := 'p' FORMAT VARIABLES NL
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

_SAT_OP_TOKS = {
    'sat': {'NOT', 'OR', 'AND'},
    'satx': {'NOT', 'OR', 'AND', 'XOR'},
    'sate': {'NOT', 'OR', 'AND', 'EQUAL'},
    'satex': {'NOT', 'OR', 'AND', 'XOR', 'EQUAL'},
}

_SAT_TOK2OP = {
    'NOT': Not,
    'OR': Or,
    'AND': And,
    'XOR': Xor,
    'EQUAL': Equal,
}

def load_sat(s, varname='x'):
    """Parse an input string in DIMACS SAT format, and return an expression."""
    m = _SAT_PREAMBLE_RE.match(s)
    if m:
        fmt = m.group(1)
        nvars = int(m.group(2))
    else:
        raise SyntaxError("incorrect preamble")

    ps, fs = s[:m.end()], s[m.end():]
    line = ps.count('\n') + 1

    gtoks = _iter_tokens(fs, line)
    types = {'POSINT', 'LPAREN'} | _SAT_OP_TOKS[fmt]
    X = bitvec(varname, (1, nvars + 1))
    try:
        tok = _expect_token(gtoks, types)
        return _sat_formula(gtoks, tok, fmt, X)
    except StopIteration:
        raise SyntaxError("incomplete formula")

def _sat_formula(gtoks, tok, fmt, X):
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
        op = _SAT_TOK2OP[tok.typ]
        tok = _expect_token(gtoks, {'LPAREN'})
        return op(*_zom_formulas(gtoks, fmt, X))

def _one_formula(gtoks, fmt, X):
    f = _sat_formula(gtoks, next(gtoks), fmt, X)
    _expect_token(gtoks, {'RPAREN'})
    return f

def _zom_formulas(gtoks, fmt, X):
    fs = []
    types = {'POSINT', 'LPAREN', 'RPAREN'} | _SAT_OP_TOKS[fmt]
    tok = _expect_token(gtoks, types)
    while tok.typ != 'RPAREN':
        fs.append(_sat_formula(gtoks, tok, fmt, X))
        tok = _expect_token(gtoks, types)
    return fs

def dump_sat(expr):
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")

    formula = _expr2sat(expr)
    if 'xor' in formula:
        fmt = 'satex' if '=' in formula else 'satx'
    elif '=' in formula:
        fmt = 'sate'
    else:
        fmt = 'sat'
    nvars = max(v.gnum for v in expr.support)
    return "p {} {}\n{}".format(fmt, nvars, formula)

def _expr2sat(expr):
    if isinstance(expr, Literal):
        return str(expr.gnum)
    elif isinstance(expr, Not):
        return "-(" + _expr2sat(expr.arg) + ")"
    elif isinstance(expr, Or):
        return "+(" + " ".join(_expr2sat(arg) for arg in expr.args) + ")"
    elif isinstance(expr, And):
        return "*(" + " ".join(_expr2sat(arg) for arg in expr.args) + ")"
    elif isinstance(expr, Xor):
        return "xor(" + " ".join(_expr2sat(arg) for arg in expr.args) + ")"
    elif isinstance(expr, Equal):
        return "=(" + " ".join(_expr2sat(arg) for arg in expr.args) + ")"
    else:
        raise ValueError("invalid expression")
