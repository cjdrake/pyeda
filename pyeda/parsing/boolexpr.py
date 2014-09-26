"""
Boolean Expression Parsing

Exceptions:
    BoolExprParseError

Interface Functions:
    parse
"""

# pylint: disable=C0103

from pyeda.parsing import lex
from pyeda.parsing.token import (
    EndToken,
    KeywordToken, NameToken, IntegerToken, OperatorToken, PunctuationToken,
)

class BoolExprParseError(Exception):
    """An error happened during parsing a Boolean expression."""


# Keywords
class KW_or(KeywordToken):
    """Expression 'Or' keyword"""
    ASTOP = 'or'

class KW_and(KeywordToken):
    """Expression 'And' keyword"""
    ASTOP = 'and'

class KW_xor(KeywordToken):
    """Expression 'Xor' keyword"""
    ASTOP = 'xor'

class KW_xnor(KeywordToken):
    """Expression 'Xnor' keyword"""
    ASTOP = 'xnor'

class KW_equal(KeywordToken):
    """Expression 'Equal' keyword"""
    ASTOP = 'equal'

class KW_unequal(KeywordToken):
    """Expression 'Unequal' keyword"""
    ASTOP = 'unequal'

class KW_nor(KeywordToken):
    """Expression 'Nor' keyword"""
    ASTOP = 'nor'

class KW_nand(KeywordToken):
    """Expression 'Nand' keyword"""
    ASTOP = 'nand'

class KW_onehot0(KeywordToken):
    """Expression 'OneHot0' keyword"""
    ASTOP = 'onehot0'

class KW_onehot(KeywordToken):
    """Expression 'OneHot' keyword"""
    ASTOP = 'onehot'

class KW_majority(KeywordToken):
    """Expression 'Majority' keyword"""
    ASTOP = 'majority'

class KW_achillesheel(KeywordToken):
    """Expression 'AchillesHeel' keyword"""
    ASTOP = 'achillesheel'

class KW_ite(KeywordToken):
    """Expression 'ITE' keyword"""
    ASTOP = 'ite'

class KW_implies(KeywordToken):
    """Expression 'Implies' keyword"""
    ASTOP = 'implies'

class KW_not(KeywordToken):
    """Expression 'Not' keyword"""
    ASTOP = 'not'


# Operators
class OP_rarrow(OperatorToken):
    """Expression '=>' operator"""

class OP_lrarrow(OperatorToken):
    """Expression '<=>' operator"""

class OP_question(OperatorToken):
    """Expression '?' operator"""

class OP_colon(OperatorToken):
    """Expression ':' operator"""

class OP_not(OperatorToken):
    """Expression '~' operator"""

class OP_or(OperatorToken):
    """Expression '|' operator"""

class OP_and(OperatorToken):
    """Expression '&' operator"""

class OP_xor(OperatorToken):
    """Expression '^' operator"""


# Punctuation
class LPAREN(PunctuationToken):
    """Expression '(' token"""

class RPAREN(PunctuationToken):
    """Expression ')' token"""

class LBRACK(PunctuationToken):
    """Expression '[' token"""

class RBRACK(PunctuationToken):
    """Expression ']' token"""

class COMMA(PunctuationToken):
    """Expression ',' token"""

class DOT(PunctuationToken):
    """Expression '.' token"""


class BoolExprLexer(lex.RegexLexer):
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

    @lex.action(NameToken)
    def name(self, text):
        """Push a variable name onto the token queue."""
        return text

    @lex.action(IntegerToken)
    def integer(self, text):
        """Push an integer onto the token queue."""
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
            (r"\bAchillesHeel\b", keyword),

            (r"\bITE\b", keyword),
            (r"\bImplies\b", keyword),
            (r"\bNot\b", keyword),

            (r"[a-zA-Z_][a-zA-Z0-9_]*", name),
            (r"\d+", integer),

            (r"=>", operator),
            (r"<=>", operator),
            (r"\?", operator),
            (r":", operator),
            (r"\~", operator),
            (r"\|", operator),
            (r"\^", operator),
            (r"\&", operator),

            (r"\(", punct),
            (r"\)", punct),
            (r"\[", punct),
            (r"\]", punct),
            (r",", punct),
            (r"\.", punct),
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
        'AchillesHeel' : KW_achillesheel,

        'ITE'     : KW_ite,
        'Implies' : KW_implies,
        'Not'     : KW_not,
    }

    OPERATORS = {
        '=>'  : OP_rarrow,
        '<=>' : OP_lrarrow,
        '?'   : OP_question,
        ':'   : OP_colon,
        '~'   : OP_not,
        '|'   : OP_or,
        '&'   : OP_and,
        '^'   : OP_xor,
    }

    PUNCTUATION = {
        '(': LPAREN,
        ')': RPAREN,
        '[': LBRACK,
        ']': RBRACK,
        ',': COMMA,
        '.': DOT,
    }


GRAMMAR = """

EXPR := ITE

ITE := IMPL '?' ITE ':' ITE
     | IMPL

IMPL := SUMTERM '=>' IMPL
      | SUMTERM '<=>' IMPL
      | SUMTERM

SUMTERM := XORTERM SUMTERM'

SUMTERM' := '|' XORTERM SUMTERM'
          | null

XORTERM := PRODTERM XORTERM'

XORTERM' := '^' PRODTERM XORTERM'
          | null

PRODTERM := FACTOR PRODTERM'

PRODTERM' := '&' FACTOR PRODTERM'
           | null

FACTOR := '~' FACTOR
        | '(' EXPR ')'
        | OPN '(' ')'
        | OPN '(' ARGS ')'
        | 'ITE' '(' EXPR ',' EXPR ',' EXPR ')'
        | 'Implies' '(' EXPR ',' EXPR ')'
        | 'Not' '(' EXPR ')'
        | VARIABLE
        | '0'
        | '1'

OPN := 'Or'
     | 'And'
     | 'Xor'
     | 'Xnor'
     | 'Equal'
     | 'Unequal'
     | 'Nor'
     | 'Nand'
     | 'OneHot0'
     | 'OneHot'
     | 'Majority'
     | 'AchillesHeel'

ARGS := EXPR ZOM_ARG
      | null

ZOM_ARG := ',' EXPR ZOM_ARG
          | null

VARIABLE := NAMES '[' INDICES ']'
          | NAMES

NAMES := NAME ZOM_NAME

ZOM_NAME := '.' NAME ZOM_NAME
          | null

INDICES := INT ZOM_INDEX

ZOM_INDEX := ',' INT ZOM_INDEX
           | null
"""

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
    KW_achillesheel,
}

FACTOR_TOKS = {
    OP_not, LPAREN,
    KW_ite, KW_implies, KW_not,
    NameToken, IntegerToken,
} | OPN_TOKS

def parse(s):
    """
    Parse a Boolean expression string,
    and return an expression abstract syntax tree.

    Parameters
    ----------
    s : str
        String containing a Boolean expression.
        See ``pyeda.parsing.boolexpr.GRAMMAR`` for details.

    Examples
    --------
    >>> parse("a | b ^ c & d")
    ('or', ('var', ('a',), ()), ('xor', ('var', ('b',), ()), ('and', ('var', ('c',), ()), ('var', ('d',), ()))))
    >>> parse("p => q")
    ('implies', ('var', ('p',), ()), ('var', ('q',), ()))

    Returns
    -------
    An ast tuple, defined recursively:

    ast := ('const', bool)
         | ('var', names, indices)
         | ('not', ast)
         | ('implies', ast, ast)
         | ('ite', ast, ast, ast)
         | (func, ast, ...)

    bool := 0 | 1

    names := (name, ...)

    indices := (index, ...)

    func := 'or' | 'and'
          | 'nor' | 'nand'
          | 'xor' | 'xnor'
          | 'equal' | 'unequal'
          | 'onehot0' | 'onehot'
          | 'majority' | 'achillesheel'
    """
    lexer = iter(BoolExprLexer(s))
    try:
        expr = _expr(lexer)
    except lex.RunError as exc:
        fstr = ("{0.args[0]}: "
                "(line: {0.lineno}, offset: {0.offset}, text: {0.text})")
        raise BoolExprParseError(fstr.format(exc))

    # Check for end of buffer
    _expect_token(lexer, {EndToken})

    return expr

def _expect_token(lexer, types):
    """Return the next token, or raise an exception."""
    tok = next(lexer)
    if any(type(tok) is t for t in types):
        return tok
    else:
        raise BoolExprParseError("unexpected token: " + str(tok))

def _expr(lexer):
    """Return an expression."""
    return _ite(lexer)

def _ite(lexer):
    """Return an ITE expression."""
    s = _impl(lexer)

    tok = next(lexer)
    # IMPL '?' ITE ':' ITE
    if type(tok) is OP_question:
        d1 = _ite(lexer)
        _expect_token(lexer, {OP_colon})
        d0 = _ite(lexer)
        return ('ite', s, d1, d0)
    # IMPL
    else:
        lexer.unpop_token(tok)
        return s

def _impl(lexer):
    """Return an Implies expression."""
    p = _sumterm(lexer)

    tok = next(lexer)
    # SUMTERM '=>' IMPL
    if type(tok) is OP_rarrow:
        q = _impl(lexer)
        return ('implies', p, q)
    # SUMTERM '<=>' IMPL
    elif type(tok) is OP_lrarrow:
        q = _impl(lexer)
        return ('equal', p, q)
    # SUMTERM
    else:
        lexer.unpop_token(tok)
        return p

def _sumterm(lexer):
    """Return a sum term expresssion."""
    xorterm = _xorterm(lexer)
    sumterm_prime = _sumterm_prime(lexer)
    if sumterm_prime is None:
        return xorterm
    else:
        return ('or', xorterm, sumterm_prime)

def _sumterm_prime(lexer):
    """Return a sum term' expression, eliminates left recursion."""
    tok = next(lexer)
    # '|' XORTERM SUMTERM'
    if type(tok) is OP_or:
        xorterm = _xorterm(lexer)
        sumterm_prime = _sumterm_prime(lexer)
        if sumterm_prime is None:
            return xorterm
        else:
            return ('or', xorterm, sumterm_prime)
    # null
    else:
        lexer.unpop_token(tok)
        return None

def _xorterm(lexer):
    """Return an xor term expresssion."""
    prodterm = _prodterm(lexer)
    xorterm_prime = _xorterm_prime(lexer)
    if xorterm_prime is None:
        return prodterm
    else:
        return ('xor', prodterm, xorterm_prime)

def _xorterm_prime(lexer):
    """Return an xor term' expression, eliminates left recursion."""
    tok = next(lexer)
    # '^' PRODTERM XORTERM'
    if type(tok) is OP_xor:
        prodterm = _prodterm(lexer)
        xorterm_prime = _xorterm_prime(lexer)
        if xorterm_prime is None:
            return prodterm
        else:
            return ('xor', prodterm, xorterm_prime)
    # null
    else:
        lexer.unpop_token(tok)
        return None

def _prodterm(lexer):
    """Return a product term expression."""
    factor = _factor(lexer)
    prodterm_prime = _prodterm_prime(lexer)
    if prodterm_prime is None:
        return factor
    else:
        return ('and', factor, prodterm_prime)

def _prodterm_prime(lexer):
    """Return a product term' expression, eliminates left recursion."""
    tok = next(lexer)
    # '&' FACTOR PRODTERM'
    if type(tok) is OP_and:
        factor = _factor(lexer)
        prodterm_prime = _prodterm_prime(lexer)
        if prodterm_prime is None:
            return factor
        else:
            return ('and', factor, prodterm_prime)
    # null
    else:
        lexer.unpop_token(tok)
        return None

def _factor(lexer):
    """Return a factor expression."""
    tok = _expect_token(lexer, FACTOR_TOKS)
    # '~' F
    toktype = type(tok)
    if toktype is OP_not:
        return ('not', _factor(lexer))
    # '(' EXPR ')'
    elif toktype is LPAREN:
        expr = _expr(lexer)
        _expect_token(lexer, {RPAREN})
        return expr
    # OPN '(' ... ')'
    elif any(toktype is t for t in OPN_TOKS):
        op = tok.ASTOP
        _expect_token(lexer, {LPAREN})
        tok = next(lexer)
        # OPN '(' ')'
        if type(tok) is RPAREN:
            args = tuple()
        # OPN '(' ARGS ')'
        else:
            lexer.unpop_token(tok)
            args = _args(lexer)
            _expect_token(lexer, {RPAREN})
        return (op, ) + args
    # ITE '(' EXPR ',' EXPR ',' EXPR ')'
    elif toktype is KW_ite:
        _expect_token(lexer, {LPAREN})
        s = _expr(lexer)
        _expect_token(lexer, {COMMA})
        d1 = _expr(lexer)
        _expect_token(lexer, {COMMA})
        d0 = _expr(lexer)
        _expect_token(lexer, {RPAREN})
        return ('ite', s, d1, d0)
    # Implies '(' EXPR ',' EXPR ')'
    elif toktype is KW_implies:
        _expect_token(lexer, {LPAREN})
        p = _expr(lexer)
        _expect_token(lexer, {COMMA})
        q = _expr(lexer)
        _expect_token(lexer, {RPAREN})
        return ('implies', p, q)
    # Not '(' EXPR ')'
    elif toktype is KW_not:
        _expect_token(lexer, {LPAREN})
        arg = _expr(lexer)
        _expect_token(lexer, {RPAREN})
        return ('not', arg)
    # VARIABLE
    elif toktype is NameToken:
        lexer.unpop_token(tok)
        return _variable(lexer)
    # '0' | '1'
    else:
        if tok.value not in {0, 1}:
            raise BoolExprParseError("unexpected token: " + str(tok))
        return ('const', tok.value)

def _args(lexer):
    """Return a tuple of arguments."""
    return (_expr(lexer), ) + _zom_arg(lexer)

def _zom_arg(lexer):
    """Return zero or more arguments."""
    tok = next(lexer)
    # ',' EXPR ZOM_ARG
    if type(tok) is COMMA:
        return (_expr(lexer), ) + _zom_arg(lexer)
    # null
    else:
        lexer.unpop_token(tok)
        return tuple()

def _variable(lexer):
    """Return a variable expression."""
    names = _names(lexer)

    tok = next(lexer)
    # NAMES '[' ... ']'
    if type(tok) is LBRACK:
        indices = _indices(lexer)
        _expect_token(lexer, {RBRACK})
    # NAMES
    else:
        lexer.unpop_token(tok)
        indices = tuple()

    return ('var', names, indices)

def _names(lexer):
    """Return a tuple of names."""
    first = _expect_token(lexer, {NameToken}).value
    rest = _zom_name(lexer)
    rnames = (first, ) + rest
    return rnames[::-1]

def _zom_name(lexer):
    """Return zero or more names."""
    tok = next(lexer)
    # '.' NAME ZOM_NAME
    if type(tok) is DOT:
        first = _expect_token(lexer, {NameToken}).value
        rest = _zom_name(lexer)
        return (first, ) + rest
    # null
    else:
        lexer.unpop_token(tok)
        return tuple()

def _indices(lexer):
    """Return a tuple of indices."""
    first = _expect_token(lexer, {IntegerToken}).value
    rest = _zom_index(lexer)
    return (first, ) + rest

def _zom_index(lexer):
    """Return zero or more indices."""
    tok = next(lexer)
    # ',' INT
    if type(tok) is COMMA:
        first = _expect_token(lexer, {IntegerToken}).value
        rest = _zom_index(lexer)
        return (first, ) + rest
    # null
    else:
        lexer.unpop_token(tok)
        return tuple()

