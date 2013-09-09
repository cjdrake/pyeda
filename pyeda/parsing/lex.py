"""
Lexical Analysis Utilities

Exceptions:
    LexError
    LexCompileError
    LexRunError

Interface Classes:
    RegexLexer
"""

import re

class LexError(Exception):
    """
    Base class for all lexical analysis errors
    """

class LexCompileError(LexError):
    """
    Errors raised during compilation of lexical analysis rules.
    """

class LexRunError(LexError):
    """
    Errors raised during lexical analysis of the source text.
    """
    def __init__(self, msg, lineno, offset, text):
        super(LexRunError, self).__init__(msg, (lineno, offset, text))
        self.lineno = lineno
        self.offset = offset
        self.text = text


class RegexLexer(object):
    """
    Lexer based on regular expressions.
    """

    RULES = {
        'root': []
    }

    def __init__(self, string):
        self.string = string

        self.pos = None
        self.lineno = None
        self.offset = None
        self.states = None
        self.tokens = None

        self._compile_rules()

    def _compile_rules(self):
        """Compile the rules into the internal lexer state."""
        self._rules = dict()
        for state, table in self.RULES.items():
            patterns = list()
            actions = list()
            nextstates = list()
            for i, row in enumerate(table):
                if len(row) == 2:
                    pattern, action = row
                    nextstate = None
                elif len(row) == 3:
                    pattern, action, nextstate = row
                else:
                    fstr = "invalid RULES: state {}, row {}"
                    raise LexCompileError(fstr.format(state, i))
                patterns.append(pattern)
                actions.append(action)
                nextstates.append(nextstate)
            reobj = re.compile('|'.join("(" + p + ")" for p in patterns))
            self._rules[state] = (reobj, actions, nextstates)

    def iter_tokens(self):
        """Iterate through all tokens in the input string."""
        self.pos = 0
        self.lineno = 1
        self.offset = 1

        self.states = ['root']
        self.tokens = []

        reobj, actions, nextstates = self._rules[self.states[-1]]
        mobj = reobj.match(self.string, self.pos)
        while mobj is not None:
            text = mobj.group(0)
            idx = mobj.lastindex - 1
            action = actions[idx]
            nextstate = nextstates[idx]

            # Take action
            action(self, text)
            if nextstate and nextstate != self.states[-1]:
                self.states[-1] = nextstate
            while self.tokens:
                yield self.tokens.pop()

            # Update position variables
            self.pos = mobj.end()
            lines = text.split('\n')
            nlines = len(lines) - 1
            if nlines == 0:
                self.offset = self.offset + len(lines[0])
            else:
                self.lineno = self.lineno + nlines
                self.offset = 1 + len(lines[-1])

            reobj, actions, nextstates = self._rules[self.states[-1]]
            mobj = reobj.match(self.string, self.pos)

        if self.pos != len(self.string):
            msg = "unexpected character"
            text = self.string[self.pos]
            raise LexRunError(msg, self.lineno, self.offset, text)

    def push_token(self, tok):
        """Push a token onto the internal token stack."""
        self.tokens.append(tok)


def action(toktype):
    def outer(func):
        def inner(lexer, text):
            value = func(lexer, text)
            lexer.tokens.append(toktype(value, lexer.lineno, lexer.offset))
        return inner
    return outer
