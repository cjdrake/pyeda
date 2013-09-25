"""
Boolean Expression Parsing

Exceptions:
    BoolExprParseError

Interface Functions:
    str2expr
"""

from pyeda.parsing.lex import RegexLexer, action
from pyeda.parsing.token import (
    NameToken, OperatorToken, PunctuationToken,
)
from pyeda.expr import exprvar

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

    RULES = {
        'root': [
            (r"\s+", ignore),

            (r"[a-zA-Z][a-zA-Z_]*(?:\.[a-zA-Z][a-zA-Z_]*)*(?:\[\d+\])*", name),

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

def expect_token(lex, types):
    """Return the next token, or raise an exception."""
    tok = next(lex)
    if any(type(tok) is t for t in types):
        return tok
    else:
        raise BoolExprParseError("unexpected token: " + str(tok))

def str2expr(s):
    """
    Parse an input string in DIMACS SAT format,
    and return an expression.
    """
    lex = iter(BoolExprLexer(s))
    return _expr(lex)

def _expr(lex):
    try:
        return _term(lex) + _expr_prime(lex)
    except StopIteration:
        raise BoolExprParseError("incomplete expression")

def _expr_prime(lex):
    try:
        tok = next(lex)
    except StopIteration:
        return 0
    # '+' T E'
    if type(tok) is OP_or:
        return _term(lex) + _expr_prime(lex)
    # null
    else:
        lex.unpop_token(tok)
        return 0

def _term(lex):
    return _factor(lex) * _term_prime(lex)

def _term_prime(lex):
    try:
        tok = next(lex)
    except StopIteration:
        return 1
    # '*' F T'
    if type(tok) is OP_and:
        return _factor(lex) * _term_prime(lex)
    # null
    else:
        lex.unpop_token(tok)
        return 1

def _factor(lex):
    tok = expect_token(lex, {OP_not, LPAREN, NameToken})
    # '-' F
    if type(tok) is OP_not:
        return -(_factor(lex))
    # '(' EXPR ')'
    elif type(tok) is LPAREN:
        expr = _expr(lex)
        expect_token(lex, {RPAREN})
        return expr
    # VAR
    else:
        lex.unpop_token(tok)
        return _variable(lex)

def _variable(lex):
    tok = expect_token(lex, {NameToken})
    try:
        idx = tok.value.index('[')
        name, tail = tok.value[:idx], tok.value[idx:]
        indices = tuple(int(s[:-1]) for s in tail.split('[')[1:])
    except ValueError:
        name = tok.value
        indices = None
    names = tuple(reversed(name.split('.')))
    return exprvar(names, indices)
