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
    EndToken,
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
        ast = _cnf(lex, varname)
    except LexRunError as exc:
        fstr = ("{0.args[0]}: "
                "(line: {0.lineno}, offset: {0.offset}, text: {0.text})")
        raise DIMACSError(fstr.format(exc))

    # Check for end of buffer
    _expect_token(lex, {EndToken})

    return ast

def _cnf(lex, varname):
    """Return a DIMACS CNF."""
    _expect_token(lex, {KW_p})
    _expect_token(lex, {KW_cnf})
    nvars = _expect_token(lex, {IntegerToken}).value
    nclauses = _expect_token(lex, {IntegerToken}).value
    return _cnf_formula(lex, varname, nvars, nclauses)

def _cnf_formula(lex, varname, nvars, nclauses):
    """Return a DIMACS CNF formula."""
    clauses = _clauses(lex, varname, nvars)

    if len(clauses) < nclauses:
        fstr = "formula has fewer than {} clauses"
        raise DIMACSError(fstr.format(nclauses))
    if len(clauses) > nclauses:
        fstr = "formula has more than {} clauses"
        raise DIMACSError(fstr.format(nclauses))

    return ('and', ) + clauses

def _clauses(lex, varname, nvars):
    """Return a tuple of DIMACS CNF clauses."""
    tok = next(lex)
    toktype = type(tok)
    if toktype is OP_not or toktype is IntegerToken:
        lex.unpop_token(tok)
        first = _clause(lex, varname, nvars)
        rest = _clauses(lex, varname, nvars)
        return (first, ) + rest
    # null
    else:
        lex.unpop_token(tok)
        return tuple()

def _clause(lex, varname, nvars):
    """Return a DIMACS CNF clause."""
    return ('or', ) + _lits(lex, varname, nvars)

def _lits(lex, varname, nvars):
    """Return a tuple of DIMACS CNF clause literals."""
    tok = _expect_token(lex, {OP_not, IntegerToken})
    if type(tok) is IntegerToken and tok.value == 0:
        return tuple()
    else:
        if type(tok) is OP_not:
            neg = True
            tok = _expect_token(lex, {IntegerToken})
        else:
            neg = False
        index = tok.value

        if index > nvars:
            fstr = "formula literal {} is greater than {}"
            raise DIMACSError(fstr.format(index, nvars))

        lit = ('var', (varname, ), (index, ))
        if neg:
            lit = ('not', lit)

        return (lit, ) + _lits(lex, varname, nvars)


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


SAT_GRAMMAR = """

SAT := COMMENT* PREAMBLE FORMULA

COMMENT := 'c' .* '\n'

PREAMBLE := 'p' FORMAT VARIABLES '\n'

FORMAT := 'sat' | 'satx' | 'sate' | 'satex'

VARIABLES := INT

FORMULA := INT
         | '-' INT
         | '(' FORMULA ')'
         | '-' '(' FORMULA ')'
         | OP '(' FORMULAS ')'

OP := '+' | '*' | 'xor' | '='

FORMULAS := FORMULAS FORMULA
          | null
"""

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

    try:
        ast = _sat(lex, varname)
    except LexRunError as exc:
        fstr = ("{0.args[0]}: "
                "(line: {0.lineno}, offset: {0.offset}, text: {0.text})")
        raise DIMACSError(fstr.format(exc))

    # Check for end of buffer
    _expect_token(lex, {EndToken})

    return ast

def _sat(lex, varname):
    """Return a DIMACS SAT."""
    _expect_token(lex, {KW_p})
    fmt = _expect_token(lex, {KW_sat, KW_satx, KW_sate, KW_satex}).value
    nvars = _expect_token(lex, {IntegerToken}).value
    return _sat_formula(lex, varname, fmt, nvars)

def _sat_formula(lex, varname, fmt, nvars):
    """Return a DIMACS SAT formula."""
    types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
    tok = _expect_token(lex, types)
    # INT
    if type(tok) is IntegerToken:
        index = tok.value
        if not 0 < index <= nvars:
            fstr = "formula literal {} outside valid range: (0, {}]"
            raise DIMACSError(fstr.format(index, nvars))
        return ('var', (varname, ), (index, ))
    # '-'
    elif type(tok) is OP_not:
        tok = _expect_token(lex, {IntegerToken, LPAREN})
        # '-' INT
        if type(tok) is IntegerToken:
            index = tok.value
            if not 0 < index <= nvars:
                fstr = "formula literal {} outside valid range: (0, {}]"
                raise DIMACSError(fstr.format(index, nvars))
            return ('not', ('var', (varname, ), (index, )))
        # '-' '(' FORMULA ')'
        else:
            formula = _sat_formula(lex, varname, fmt, nvars)
            _expect_token(lex, {RPAREN})
            return ('not', formula)
    # '(' FORMULA ')'
    elif type(tok) is LPAREN:
        formula = _sat_formula(lex, varname, fmt, nvars)
        _expect_token(lex, {RPAREN})
        return formula
    # OP '(' FORMULAS ')'
    else:
        _expect_token(lex, {LPAREN})
        formulas = _formulas(lex, varname, fmt, nvars)
        _expect_token(lex, {RPAREN})
        return (tok.ASTOP, ) + formulas

def _formulas(lex, varname, fmt, nvars):
    """Return a tuple of DIMACS SAT formulas."""
    types = {IntegerToken, LPAREN} | _SAT_TOKS[fmt]
    tok = lex.peek_token()
    if any(type(tok) is t for t in types):
        first = _sat_formula(lex, varname, fmt, nvars)
        rest = _formulas(lex, varname, fmt, nvars)
        return (first, ) + rest
    # null
    else:
        return tuple()

