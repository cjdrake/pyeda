"""
Boolean Expression Parsing

Exceptions:
    BoolExprParseError

Interface Functions:
    parse
"""

from pyeda.parsing.lex import RegexLexer, action
from pyeda.parsing.token import (
    KeywordToken, NameToken, IntegerToken, OperatorToken, PunctuationToken,
)

class BoolExprParseError(Exception):
    def __init__(self, msg):
        super(BoolExprParseError, self).__init__(msg)

# Keywords
class KW_or(KeywordToken):
    ASTOP = 'or'
class KW_and(KeywordToken):
    ASTOP = 'and'
class KW_xor(KeywordToken):
    ASTOP = 'xor'
class KW_xnor(KeywordToken):
    ASTOP = 'xnor'
class KW_equal(KeywordToken):
    ASTOP = 'equal'
class KW_unequal(KeywordToken):
    ASTOP = 'unequal'
class KW_nor(KeywordToken):
    ASTOP = 'nor'
class KW_nand(KeywordToken):
    ASTOP = 'nand'
class KW_onehot0(KeywordToken):
    ASTOP = 'onehot0'
class KW_onehot(KeywordToken):
    ASTOP = 'onehot'
class KW_majority(KeywordToken):
    ASTOP = 'majority'
class KW_ite(KeywordToken):
    ASTOP = 'ite'
class KW_implies(KeywordToken):
    ASTOP = 'implies'
class KW_not(KeywordToken):
    ASTOP = 'not'

# Operators
class OP_rarrow(OperatorToken): pass
class OP_lrarrow(OperatorToken): pass
class OP_question(OperatorToken): pass
class OP_colon(OperatorToken): pass
class OP_not(OperatorToken): pass
class OP_or(OperatorToken): pass
class OP_and(OperatorToken): pass

# Punctuation
class LPAREN(PunctuationToken): pass
class RPAREN(PunctuationToken): pass
class COMMA(PunctuationToken): pass


class BoolExprLexer(RegexLexer):
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

    @action(NameToken)
    def name(self, text):
        return text

    @action(IntegerToken)
    def num(self, text):
        return int(text)

    RULES = {
        'root': [
            (r"\s+", ignore),

            (r"\bOr\b", keyword),
            (r"\bAnd\b", keyword),
            (r"\bXor\b", keyword),
            (r"\bXnor\b", keyword),
            (r"\bEqual\b", keyword),
            (r"\bUnequal\b", keyword),
            (r"\bNor\b", keyword),
            (r"\bNand\b", keyword),
            (r"\bOneHot0\b", keyword),
            (r"\bOneHot\b", keyword),
            (r"\bMajority\b", keyword),

            (r"\bITE\b", keyword),
            (r"\bImplies\b", keyword),
            (r"\bNot\b", keyword),

            (r"[a-zA-Z][a-zA-Z_]*(?:\.[a-zA-Z][a-zA-Z_]*)*(?:\[\d+\])*", name),
            (r"\b[01]\b", num),

            (r"=>", operator),
            (r"<=>", operator),
            (r"\?", operator),
            (r":", operator),
            (r"\-", operator),
            (r"\+", operator),
            (r"\*", operator),

            (r"\(", punct),
            (r"\)", punct),
            (r",", punct),
        ],
    }

    KEYWORDS = {
        'Or'       : KW_or,
        'And'      : KW_and,
        'Xor'      : KW_xor,
        'Xnor'     : KW_xnor,
        'Equal'    : KW_equal,
        'Unequal'  : KW_unequal,
        'Nor'      : KW_nor,
        'Nand'     : KW_nand,
        'OneHot0'  : KW_onehot0,
        'OneHot'   : KW_onehot,
        'Majority' : KW_majority,

        'ITE'     : KW_ite,
        'Implies' : KW_implies,
        'Not'     : KW_not,
    }

    OPERATORS = {
        '=>'  : OP_rarrow,
        '<=>' : OP_lrarrow,
        '?'   : OP_question,
        ':'   : OP_colon,
        '-'   : OP_not,
        '+'   : OP_or,
        '*'   : OP_and,
    }

    PUNCTUATION = {
        '(': LPAREN,
        ')': RPAREN,
        ',': COMMA,
    }


# Grammar for a Boolean expression
#
# EXPR := ITE
#
# ITE := IMPL '?' ITE ':' ITE
#      | IMPL
#
# IMPL := SUM '=>' IMPL
#       | SUM '<=>' IMPL
#       | SUM
#
# SUM := TERM SUM'
#
# SUM' := '+' TERM SUM'
#       | null
#
# TERM := FACTOR TERM'
#
# TERM' := '*' FACTOR TERM'
#        | null
#
# FACTOR := '-' FACTOR
#         | '(' EXPR ')'
#         | OPN '(' ARGS ')'
#         | 'ITE' '(' EXPR ',' EXPR ',' EXPR ')'
#         | 'Implies' '(' EXPR ',' EXPR ')'
#         | 'Not' '(' EXPR ')'
#         | VAR
#         | '0'
#         | '1'
#
# OPN := 'Or'
#      | 'And'
#      | 'Xor'
#      | 'Xnor'
#      | 'Equal'
#      | 'Unequal'
#      | 'Nor'
#      | 'Nand'
#      | 'OneHot0'
#      | 'OneHot'
#      | 'Majority'
#
# ARGS := EXPR ',' ARGS
#       | EXPR
#       | null

OPN_TOKS = {
    KW_or,
    KW_and,
    KW_xor,
    KW_xnor,
    KW_equal,
    KW_unequal,
    KW_nor,
    KW_nand,
    KW_onehot0,
    KW_onehot,
    KW_majority,
}

FACTOR_TOKS = {
    OP_not, LPAREN,
    KW_ite, KW_implies, KW_not,
    NameToken, IntegerToken,
} | OPN_TOKS

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
    return _ite(lex)

def _ite(lex):
    s = _impl(lex)
    try:
        tok = next(lex)
    except StopIteration:
        return s

    if type(tok) is OP_question:
        d1 = _ite(lex)
        _expect_token(lex, {OP_colon})
        d0 = _ite(lex)
        return ('ite', s, d1, d0)
    else:
        lex.unpop_token(tok)
        return s

def _impl(lex):
    p = _sum(lex)
    try:
        tok = next(lex)
    except StopIteration:
        return p

    if type(tok) is OP_rarrow:
        q = _impl(lex)
        return ('implies', p, q)
    elif type(tok) is OP_lrarrow:
        q = _impl(lex)
        return ('equal', p, q)
    else:
        lex.unpop_token(tok)
        return p

def _sum(lex):
    term = _term(lex)
    expr_prime = _sum_prime(lex)
    if expr_prime is None:
        return term
    else:
        return ('or', term, expr_prime)

def _sum_prime(lex):
    try:
        tok = next(lex)
    except StopIteration:
        return None
    # '+' T E'
    toktype = type(tok)
    if toktype is OP_or:
        term = _term(lex)
        expr_prime = _sum_prime(lex)
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
    tok = _expect_token(lex, FACTOR_TOKS)
    # '-' F
    toktype = type(tok)
    if toktype is OP_not:
        return ('not', _factor(lex))
    # '(' EXPR ')'
    elif toktype is LPAREN:
        expr = _expr(lex)
        _expect_token(lex, {RPAREN})
        return expr
    # OPN '(' ... ')'
    elif any(toktype is t for t in OPN_TOKS):
        _expect_token(lex, {LPAREN})
        args = _args(lex)
        _expect_token(lex, {RPAREN})
        return (tok.ASTOP, ) + args
    # ITE '(' EXPR ',' EXPR ',' EXPR ')'
    elif toktype is KW_ite:
        _expect_token(lex, {LPAREN})
        arg0 = _expr(lex)
        _expect_token(lex, {COMMA})
        arg1 = _expr(lex)
        _expect_token(lex, {COMMA})
        arg2 = _expr(lex)
        _expect_token(lex, {RPAREN})
        return (tok.ASTOP, arg0, arg1, arg2)
    # Implies '(' EXPR ',' EXPR ')'
    elif toktype is KW_implies:
        _expect_token(lex, {LPAREN})
        arg0 = _expr(lex)
        _expect_token(lex, {COMMA})
        arg1 = _expr(lex)
        _expect_token(lex, {RPAREN})
        return (tok.ASTOP, arg0, arg1)
    # Not '(' EXPR ')'
    elif toktype is KW_not:
        _expect_token(lex, {LPAREN})
        arg = _expr(lex)
        _expect_token(lex, {RPAREN})
        return (tok.ASTOP, arg)
    # VAR
    elif toktype is NameToken:
        lex.unpop_token(tok)
        return _variable(lex)
    # 0 | 1
    else:
        return ('const', tok.value)

def _args(lex):
    tok = next(lex)
    if type(tok) is RPAREN:
        lex.unpop_token(tok)
        return tuple()
    else:
        lex.unpop_token(tok)
        args = (_expr(lex), )
        tok = _expect_token(lex, {COMMA, RPAREN})
        if type(tok) is COMMA:
            return args + _args(lex)
        else:
            lex.unpop_token(tok)
            return args

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
