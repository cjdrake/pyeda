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
    parse_cnf
    parse_sat
"""

# pylint: disable=C0103

from pyeda.parsing.lex import LexRunError, RegexLexer, action
from pyeda.parsing.token import (
    KeywordToken, IntegerToken, OperatorToken, PunctuationToken,
)

class DIMACSError(Exception):
    """An error happened during parsing a DIMACS file"""


# Keywords
class KW_p(KeywordToken):
    """DIMACS 'p' preamble token"""

class KW_cnf(KeywordToken):
    """DIMACS 'cnf' token"""

class KW_sat(KeywordToken):
    """DIMACS 'sat' token"""

class KW_satx(KeywordToken):
    """DIMACS 'satx' token"""

class KW_sate(KeywordToken):
    """DIMACS 'sate' token"""

class KW_satex(KeywordToken):
    """DIMACS 'satex' token"""


# Operators
class OP_not(OperatorToken):
    """DIMACS '-' operator"""
    ASTOP = 'not'

class OP_or(OperatorToken):
    """DIMACS '+' operator"""
    ASTOP = 'or'

class OP_and(OperatorToken):
    """DIMACS '*' operator"""
    ASTOP = 'and'

class OP_xor(OperatorToken):
    """DIMACS 'xor' operator"""
    ASTOP = 'xor'

class OP_equal(OperatorToken):
    """DIMACS '=' operator"""
    ASTOP = 'equal'


# Punctuation
class LPAREN(PunctuationToken):
    """DIMACS '(' token"""

class RPAREN(PunctuationToken):
    """DIMACS ')' token"""


class CNFLexer(RegexLexer):
    """Lexical analysis of CNF strings"""

    def ignore(self, text):
        """Ignore this text."""

    def keyword(self, text):
        """Push a keyword onto the token queue."""
        cls = self.KEYWORDS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def operator(self, text):
        """Push an operator onto the token queue."""
        cls = self.OPERATORS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    @action(IntegerToken)
    def integer(self, text):
        """Push an integer onto the token queue."""
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


def _expect_token(lex, types):
    """Return the next token, or raise an exception."""
    tok = next(lex)
    if any(type(tok) is t for t in types):
        return tok
    else:
        raise DIMACSError("unexpected token: " + str(tok))

def parse_cnf(s, varname='x'):
    """
    Parse an input string in DIMACS CNF format,
    and return an expression abstract syntax tree.

    Parameters
    ----------
    s : str
        String containing a DIMACS CNF.

    varname : str, optional
        The variable name used for creating literals.
        Defaults to 'x'.

    Returns
    -------
    An ast tuple, defined recursively:

    ast := ('var', names, indices)
         | ('not', ast)
         | ('or', ast, ...)
         | ('and', ast, ...)

    names := (name, ...)

    indices := (index, ...)
    """
    lex = iter(CNFLexer(s))
    try:
        _expect_token(lex, {KW_p})
        _expect_token(lex, {KW_cnf})
        nvars = _expect_token(lex, {IntegerToken}).value
        nclauses = _expect_token(lex, {IntegerToken}).value
        ast = _cnf_formula(lex, varname, nvars, nclauses)
    except LexRunError as exc:
        fstr = ("{0.args[0]}: "
                "(line: {0.lineno}, offset: {0.offset}, text: {0.text})")
        raise DIMACSError(fstr.format(exc))

    return ast

def _cnf_formula(lex, varname, nvars, nclauses):
    """Return a DIMACS CNF formula."""
    clauses = list()
    while True:
        try:
            tok = _expect_token(lex, {OP_not, IntegerToken})
        except StopIteration:
            break
        lex.unpop_token(tok)
        clauses.append(_cnf_clause(lex, varname, nvars))

    if len(clauses) < nclauses:
        fstr = "formula has fewer than {} clauses"
        raise DIMACSError(fstr.format(nclauses))
    elif len(clauses) > nclauses:
        fstr = "formula has more than {} clauses"
        raise DIMACSError(fstr.format(nclauses))

    return ('and', ) + tuple(clauses)

def _cnf_clause(lex, varname, nvars):
    """Return a DIMACS CNF clause."""
    clause = list()
    tok = _expect_token(lex, {OP_not, IntegerToken})
    while not (type(tok) is IntegerToken and tok.value == 0):
        if type(tok) is OP_not:
            neg = True
            tok = _expect_token(lex, {IntegerToken})
            index = tok.value
        else:
            neg = False
            index = tok.value
        if index > nvars:
            fstr = "formula literal {} is greater than {}"
            raise DIMACSError(fstr.format(index, nvars))
        if neg:
            clause.append((OP_not.ASTOP, ('var', (varname, ), (index, ))))
        else:
            clause.append(('var', (varname, ), (index, )))
        try:
            tok = _expect_token(lex, {OP_not, IntegerToken})
        except StopIteration:
            raise DIMACSError("incomplete clause")

    return ('or', ) + tuple(clause)


class SATLexer(RegexLexer):
    """Lexical analysis of SAT strings"""

    def ignore(self, text):
        """Ignore this text."""

    def keyword(self, text):
        """Push a keyword onto the token queue."""
        cls = self.KEYWORDS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def operator(self, text):
        """Push an operator onto the token queue."""
        cls = self.OPERATORS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def punct(self, text):
        """Push punctuation onto the token queue."""
        cls = self.PUNCTUATION[text]
        self.push_token(cls(text, self.lineno, self.offset))

    @action(IntegerToken)
    def integer(self, text):
        """Push an integer onto the token queue."""
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

def parse_sat(s, varname='x'):
    """
    Parse an input string in DIMACS SAT format,
    and return an expression.
    """
    lex = iter(SATLexer(s))

    _expect_token(lex, {KW_p})
    fmt = _expect_token(lex, {KW_sat, KW_satx, KW_sate, KW_satex}).value
    nvars = _expect_token(lex, {IntegerToken}).value

    try:
        types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
        tok = _expect_token(lex, types)
        lex.unpop_token(tok)
        return _sat_formula(lex, fmt, varname, nvars)
    except StopIteration:
        raise DIMACSError("incomplete formula")

def _sat_formula(lex, fmt, varname, nvars):
    """Return a DIMACS SAT formula."""
    types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
    tok = _expect_token(lex, types)
    if type(tok) is IntegerToken:
        index = tok.value
        if not 0 < index <= nvars:
            fstr = "formula literal {} outside valid range: (0, {}]"
            raise DIMACSError(fstr.format(index, nvars))
        return ('var', (varname, ), (index, ))
    elif type(tok) is OP_not:
        tok = _expect_token(lex, {IntegerToken, LPAREN})
        if type(tok) is IntegerToken:
            index = tok.value
            if not 0 < index <= nvars:
                fstr = "formula literal {} outside valid range: (0, {}]"
                raise DIMACSError(fstr.format(index, nvars))
            return (OP_not.ASTOP, ('var', (varname, ), (index, )))
        else:
            return (OP_not.ASTOP, _one_formula(lex, fmt, varname, nvars))
    elif type(tok) is LPAREN:
        return _one_formula(lex, fmt, varname, nvars)
    # OR/AND/XOR/EQUAL
    else:
        _expect_token(lex, {LPAREN})
        return (tok.ASTOP, ) + _zom_formulas(lex, fmt, varname, nvars)

def _one_formula(lex, fmt, varname, nvars):
    """Return one DIMACS SAT formula."""
    f = _sat_formula(lex, fmt, varname, nvars)
    _expect_token(lex, {RPAREN})
    return f

def _zom_formulas(lex, fmt, varname, nvars):
    """Return zero or more DIMACS SAT formulas."""
    fs = list()
    types = {IntegerToken, LPAREN, RPAREN} | _SAT_TOKS[fmt]
    tok = _expect_token(lex, types)
    while type(tok) is not RPAREN:
        lex.unpop_token(tok)
        fs.append(_sat_formula(lex, fmt, varname, nvars))
        tok = _expect_token(lex, types)
    return tuple(fs)

