"""
Token types used by lex and parse operations

Interface Classes:
    Token
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

class KeywordToken(Token): pass
class NameToken(Token): pass
class LiteralToken(Token): pass
class StringToken(LiteralToken): pass
class NumberToken(LiteralToken): pass
class IntegerToken(NumberToken): pass
class FloatToken(NumberToken): pass
class OperatorToken(Token): pass
class PunctuationToken(Token): pass
