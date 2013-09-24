"""
DIMACS

For more information on the input formats,
see "Satisfiability Suggested Format",
published May 1993 by the Rutgers Center for Discrete Mathematics (DIMACS).

Also, see the proceedings of the International SAT Competition
(http://www.satcompetition.org) for information and CNF examples.

Exceptions:
    DIMACSError

Interface Functions:
    load_cnf
    dump_cnf
    load_sat
    dump_sat
"""

from pyeda.parsing.lex import RegexLexer, action
from pyeda.parsing.token import (
    KeywordToken, IntegerToken, OperatorToken, PunctuationToken,
)

from pyeda.expr import (
    Not, Or, And, Xor, Equal,
    Expression, ExprLiteral, ExprOr, ExprAnd, ExprNot, ExprXor, ExprEqual
)
from pyeda.vexpr import bitvec

class DIMACSError(Exception):
    def __init__(self, msg):
        super(DIMACSError, self).__init__(msg)

# Keywords
class KW_p(KeywordToken): pass
class KW_cnf(KeywordToken): pass
class KW_sat(KeywordToken): pass
class KW_satx(KeywordToken): pass
class KW_sate(KeywordToken): pass
class KW_satex(KeywordToken): pass

# Operators
class OP_not(OperatorToken): pass
class OP_or(OperatorToken): pass
class OP_and(OperatorToken): pass
class OP_xor(OperatorToken): pass
class OP_equal(OperatorToken): pass

# Punctuation
class LPAREN(PunctuationToken): pass
class RPAREN(PunctuationToken): pass


class CNFLexer(RegexLexer):
    """Lexical analysis of CNF strings"""

    def ignore(self, text):
        pass

    def keyword(self, text):
        cls = self.KEYWORDS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def operator(self, text):
        cls = self.OPERATORS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    @action(IntegerToken)
    def integer(self, text):
        return int(text)

    RULES = {
        'root': [
            (r"c.*\n", ignore),
            (r"\bp\b", keyword, 'preamble'),
        ],
        'preamble': [
            (r"[ \t]+", ignore),
            (r"\bcnf\b", keyword),
            (r"\d+", integer),
            (r"\n", ignore, 'formula'),
        ],
        'formula': [
            (r"\s+", ignore),
            (r"-", operator),
            (r"\d+", integer),
        ],
    }

    KEYWORDS = {
        'p': KW_p,
        'cnf': KW_cnf,
    }

    OPERATORS = {
        '-': OP_not,
    }


def expect_token(lex, types):
    """Return the next token, or raise an exception."""
    tok = next(lex)
    if any(isinstance(tok, t) for t in types):
        return tok
    else:
        raise DIMACSError("unexpected token: " + str(tok))

def load_cnf(s, varname='x'):
    """
    Parse an input string in DIMACS CNF format,
    and return an expression.
    """
    lex = iter(CNFLexer(s))

    expect_token(lex, {KW_p})
    expect_token(lex, {KW_cnf})
    nvariables = expect_token(lex, {IntegerToken}).value
    nclauses = expect_token(lex, {IntegerToken}).value

    X = bitvec(varname, (1, nvariables + 1))
    formula = _cnf_formula(lex, X)

    if len(formula) < nclauses:
        fstr = "formula has fewer than {} clauses"
        raise DIMACSError(fstr.format(nclauses))
    elif len(formula) > nclauses:
        fstr = "formula has more than {} clauses"
        raise DIMACSError(fstr.format(nclauses))

    return And(*[Or(*clause) for clause in formula])

def _cnf_formula(lex, X):
    formula = list()
    while True:
        try:
            tok = expect_token(lex, {OP_not, IntegerToken})
        except StopIteration:
            break
        lex.unpop_token(tok)
        formula.append(_cnf_clause(lex, X))

    return formula

def _cnf_clause(lex, X):
    clause = list()
    tok = expect_token(lex, {OP_not, IntegerToken})
    while not (isinstance(tok, IntegerToken) and tok.value == 0):
        if isinstance(tok, OP_not):
            neg = True
            tok = expect_token(lex, {IntegerToken})
            idx = tok.value
        else:
            neg = False
            idx = tok.value
        if idx > len(X):
            fstr = "formula literal {} is greater than {}"
            raise DIMACSError(fstr.format(idx, len(X)))
        clause.append(-X[idx] if neg else X[idx])
        try:
            tok = expect_token(lex, {OP_not, IntegerToken})
        except StopIteration:
            raise DIMACSError("incomplete clause")

    return clause

def dump_cnf(expr):
    """Convert an expression into an equivalent DIMACS CNF string."""
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")
    if not expr.is_cnf():
        raise ValueError("expression is not a CNF")

    nums = {v.uniqid: None for v in expr.support}
    num = 1
    for uniqid in sorted(nums.keys()):
        nums[uniqid] = num
        nums[-uniqid] = -num
        num += 1

    nvariables = num - 1
    nclauses = len(expr.args)

    formula = list()
    for clause in expr.args:
        for arg in clause.arg_set:
            formula.extend([str(nums[arg.uniqid]), " "])
        formula.extend(['0', '\n'])
    formula = "".join(formula)

    return "p cnf {} {}\n{}".format(nvariables, nclauses, formula)


class SATLexer(RegexLexer):
    """Lexical analysis of SAT strings"""

    def ignore(self, text):
        pass

    def keyword(self, text):
        cls = self.KEYWORDS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def operator(self, text):
        cls = self.OPERATORS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def punct(self, text):
        cls = self.PUNCTUATION[text]
        self.push_token(cls(text, self.lineno, self.offset))

    @action(IntegerToken)
    def integer(self, text):
        return int(text)

    RULES = {
        'root': [
            (r"c.*\n", ignore),
            (r"\bp\b", keyword, 'preamble'),
        ],
        'preamble': [
            (r"[ \t]+", ignore),
            (r"\bsat\b", keyword),
            (r"\bsatx\b", keyword),
            (r"\bsate\b", keyword),
            (r"\bsatex\b", keyword),
            (r"\d+", integer),
            (r"\n", ignore, 'formula'),
        ],
        'formula': [
            (r"\s+", ignore),
            (r"\+", operator),
            (r"\-", operator),
            (r"\*", operator),
            (r"\bxor\b", operator),
            (r"=", operator),
            (r"\(", punct),
            (r"\)", punct),
            (r"\d+", integer),
        ],
    }

    KEYWORDS = {
        'p': KW_p,
        'sat': KW_sat,
        'satx': KW_satx,
        'sate': KW_sate,
        'satex': KW_satex,
    }

    OPERATORS = {
        '-': OP_not,
        '+': OP_or,
        '*': OP_and,
        'xor': OP_xor,
        '=': OP_equal,
    }

    PUNCTUATION = {
        '(': LPAREN,
        ')': RPAREN,
    }

# Grammar for a SAT file
#
# SAT := COMMENT* PREAMBLE FORMULA
#
# COMMENT := 'c' .* '\n'
#
# PREAMBLE := 'p' FORMAT VARIABLES '\n'
#
# FORMAT := 'sat' | 'satx' | 'sate' | 'satex'
#
# VARIABLES := INT
#
# FORMULA := INT
#          | '-' INT
#          | '(' FORMULA ')'
#          | '-' '(' FORMULA ')'
#          | '+' '(' FORMULA* ')'
#          | '*' '(' FORMULA* ')'
#          | 'xor' '(' FORMULA* ')'
#          | '=' '(' FORMULA* ')'

_SAT_TOKS = {
    'sat': {OP_not, OP_or, OP_and},
    'satx': {OP_not, OP_or, OP_and, OP_xor},
    'sate': {OP_not, OP_or, OP_and, OP_equal},
    'satex': {OP_not, OP_or, OP_and, OP_xor, OP_equal},
}

_OPS = {
    OP_not: Not,
    OP_or: Or,
    OP_and: And,
    OP_xor: Xor,
    OP_equal: Equal,
}

def load_sat(s, varname='x'):
    """
    Parse an input string in DIMACS SAT format,
    and return an expression.
    """
    lex = iter(SATLexer(s))

    expect_token(lex, {KW_p})
    fmt = expect_token(lex, {KW_sat, KW_satx, KW_sate, KW_satex}).value
    nvariables = expect_token(lex, {IntegerToken}).value

    X = bitvec(varname, (1, nvariables + 1))
    try:
        types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
        tok = expect_token(lex, types)
        lex.unpop_token(tok)
        return _sat_formula(lex, fmt, X)
    except StopIteration:
        raise DIMACSError("incomplete formula")

def _sat_formula(lex, fmt, X):
    types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
    tok = expect_token(lex, types)
    if isinstance(tok, IntegerToken):
        idx = tok.value
        if not 0 < idx <= len(X):
            fstr = "formula literal {} outside valid range: (0, {}]"
            raise DIMACSError(fstr.format(idx, len(X)))
        return X[idx]
    elif isinstance(tok, OP_not):
        tok = expect_token(lex, {IntegerToken, LPAREN})
        if isinstance(tok, IntegerToken):
            idx = tok.value
            if not 0 < idx <= len(X):
                fstr = "formula literal {} outside valid range: (0, {}]"
                raise DIMACSError(fstr.format(idx, len(X)))
            return -X[idx]
        else:
            return Not(_one_formula(lex, fmt, X))
    elif isinstance(tok, LPAREN):
        return _one_formula(lex, fmt, X)
    # OR/AND/XOR/EQUAL
    else:
        op = _OPS[type(tok)]
        tok = expect_token(lex, {LPAREN})
        return op(*_zom_formulas(lex, fmt, X))

def _one_formula(lex, fmt, X):
    f = _sat_formula(lex, fmt, X)
    expect_token(lex, {RPAREN})
    return f

def _zom_formulas(lex, fmt, X):
    fs = []
    types = {IntegerToken, LPAREN, RPAREN} | _SAT_TOKS[fmt]
    tok = expect_token(lex, types)
    while not isinstance(tok, RPAREN):
        lex.unpop_token(tok)
        fs.append(_sat_formula(lex, fmt, X))
        tok = expect_token(lex, types)
    return fs

def dump_sat(expr):
    """Convert an expression into an equivalent DIMACS SAT string."""
    if not isinstance(expr, Expression):
        raise ValueError("input is not an expression")

    nums = {v.uniqid: None for v in expr.support}
    num = 1
    for uniqid in sorted(nums.keys()):
        nums[uniqid] = num
        nums[-uniqid] = -num
        num += 1

    nvariables = num - 1

    formula = _expr2sat(expr, nums)
    if 'xor' in formula:
        if '=' in formula:
            fmt = 'satex'
        else:
            fmt = 'satx'
    elif '=' in formula:
        fmt = 'sate'
    else:
        fmt = 'sat'
    return "p {} {}\n{}".format(fmt, nvariables, formula)

def _expr2sat(expr, nums):
    if isinstance(expr, ExprLiteral):
        return str(nums[expr.uniqid])
    elif isinstance(expr, ExprOr):
        return "+(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    elif isinstance(expr, ExprAnd):
        return "*(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    elif isinstance(expr, ExprNot):
        return "-(" + _expr2sat(expr.args[0], nums) + ")"
    elif isinstance(expr, ExprXor):
        return "xor(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    elif isinstance(expr, ExprEqual):
        return "=(" + " ".join(_expr2sat(arg, nums) for arg in expr.args) + ")"
    else:
        raise ValueError("invalid expression")
