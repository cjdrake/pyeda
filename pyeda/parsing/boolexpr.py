"""
Boolean Expression Parsing

Exceptions:
    BoolExprParseError

Interface Functions:
    parse
"""

from pyeda.parsing.lex import RegexLexer, action
from pyeda.parsing.token import (
    NameToken, IntegerToken, OperatorToken, PunctuationToken,
)

class BoolExprParseError(Exception):
    def __init__(self, msg):
        super(BoolExprParseError, self).__init__(msg)

# Operators
class OP_not(OperatorToken): pass
class OP_or(OperatorToken): pass
class OP_and(OperatorToken): pass

class LPAREN(PunctuationToken): pass
class RPAREN(PunctuationToken): pass


class BoolExprLexer(RegexLexer):
    """Lexical analysis of SAT strings"""

    def ignore(self, text):
        pass

    def operator(self, text):
        cls = self.OPERATORS[text]
        self.push_token(cls(text, self.lineno, self.offset))

    def punct(self, text):
        cls = self.PUNCTUATION[text]
        self.push_token(cls(text, self.lineno, self.offset))

    @action(NameToken)
    def name(self, text):
        return text

    @action(IntegerToken)
    def num(self, text):
        return int(text)

    RULES = {
        'root': [
            (r"\s+", ignore),

            (r"[a-zA-Z][a-zA-Z_]*(?:\.[a-zA-Z][a-zA-Z_]*)*(?:\[\d+\])*", name),
            (r"\b[01]\b", num),

            (r"\+", operator),
            (r"\-", operator),
            (r"\*", operator),

            (r"\(", punct),
            (r"\)", punct),
        ],
    }

    OPERATORS = {
        '-': OP_not,
        '+': OP_or,
        '*': OP_and,
    }

    PUNCTUATION = {
        '(': LPAREN,
        ')': RPAREN,
    }


# Grammar for a Boolean expression
#
# E := T E'
#
# E' := '+' T E'
#     | null
#
# T := F T'
#
# T' := '*' F T'
#     | null
#
# F := '-' F
#    | '(' EXPR ')'
#    | VAR
#    | '0'
#    | '1'

def parse(s):
    """
    Parse an input string in DIMACS SAT format,
    and return an expression abstract syntax tree.
    """
    lex = iter(BoolExprLexer(s))
    try:
        expr = _expr(lex)
    except StopIteration:
        raise BoolExprParseError("incomplete expression")
    try:
        tok = next(lex)
    except StopIteration:
        return expr
    else:
        raise BoolExprParseError("unexpected token: " + str(tok))

def _expect_token(lex, types):
    """Return the next token, or raise an exception."""
    tok = next(lex)
    if any(type(tok) is t for t in types):
        return tok
    else:
        raise BoolExprParseError("unexpected token: " + str(tok))

def _expr(lex):
    term = _term(lex)
    expr_prime = _expr_prime(lex)
    if expr_prime is None:
        return term
    else:
        return ('or', term, expr_prime)

def _expr_prime(lex):
    try:
        tok = next(lex)
    except StopIteration:
        return None
    # '+' T E'
    toktype = type(tok)
    if toktype is OP_or:
        term = _term(lex)
        expr_prime = _expr_prime(lex)
        if expr_prime is None:
            return term
        else:
            return ('or', term, expr_prime)
    # null
    else:
        lex.unpop_token(tok)
        return None

def _term(lex):
    factor = _factor(lex)
    term_prime = _term_prime(lex)
    if term_prime is None:
        return factor
    else:
        return ('and', factor, term_prime)

def _term_prime(lex):
    try:
        tok = next(lex)
    except StopIteration:
        return None
    # '*' F T'
    toktype = type(tok)
    if toktype is OP_and:
        factor = _factor(lex)
        term_prime = _term_prime(lex)
        if term_prime is None:
            return factor
        else:
            return ('and', factor, term_prime)
    # null
    else:
        lex.unpop_token(tok)
        return None

def _factor(lex):
    tok = _expect_token(lex, {OP_not, LPAREN, NameToken, IntegerToken})
    # '-' F
    toktype = type(tok)
    if toktype is OP_not:
        return ('not', _factor(lex))
    # '(' EXPR ')'
    elif toktype is LPAREN:
        expr = _expr(lex)
        _expect_token(lex, {RPAREN})
        return expr
    # VAR
    elif toktype is NameToken:
        lex.unpop_token(tok)
        return _variable(lex)
    # 0 | 1
    else:
        return ('const', tok.value)

def _variable(lex):
    tok = _expect_token(lex, {NameToken})
    try:
        idx = tok.value.index('[')
        name, tail = tok.value[:idx], tok.value[idx:]
        indices = tuple(int(s[:-1]) for s in tail.split('[')[1:])
    except ValueError:
        name = tok.value
        indices = tuple()
    names = tuple(reversed(name.split('.')))
    return ('var', names, indices)
