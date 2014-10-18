"""
Token types used by lex and parse operations

Interface Classes:
    Token
        EndToken
        KeywordToken
        NameToken
        LiteralToken
            StringToken
            NumberToken
                IntegerToken
                FloatToken
        OperatorToken
        PunctuationToken
"""

import collections

Token = collections.namedtuple('Token', ['value', 'lineno', 'offset'])


class EndToken(Token):
    """Special token for end of buffer"""

class KeywordToken(Token):
    """Base class for keyword tokens"""

class NameToken(Token):
    """Base class for name tokens"""

class LiteralToken(Token):
    """Base class for literal tokens"""

class StringToken(LiteralToken):
    """literal.string tokens, eg 'hello world'"""

class NumberToken(LiteralToken):
    """Base class for literal.number tokens"""

class IntegerToken(NumberToken):
    """literal.number.integer tokens, eg 42"""

class FloatToken(NumberToken):
    """literal.number.float tokens, eg 6.0221413e+23"""

class OperatorToken(Token):
    """literal.operator tokens, eg +-*/"""

class PunctuationToken(Token):
    """literal.punctuation tokens, eg !@#$"""

