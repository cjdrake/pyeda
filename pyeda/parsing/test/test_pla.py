"""
Test PLA parsing functions
"""


import pytest

from pyeda.boolalg.espresso import FTYPE, RTYPE
from pyeda.parsing.pla import Error, parse

BASIC = """
# Filename: basic.pla

.i 4
.o 2
.ilb x y z
.ob f g
.p 3
.type fr
0001 00
0010 01
0100 10
1000 11
.e
"""


def test_errors():
    # General syntax error
    with pytest.raises(Error):
        parse("foo\nbar\nfiz\nbuz\n")
    # .i declared more than once
    with pytest.raises(Error):
        parse(".i 1\n.i 2\n")
    # .o declared more than once
    with pytest.raises(Error):
        parse(".o 1\n.o 2\n")
    # .ilb declared more than once
    with pytest.raises(Error):
        parse(".ilb a b\n.ilb c d\n")
    # .ob declared more than once
    with pytest.raises(Error):
        parse(".ob a b\n.ob c d\n")
    # .type declared more than once
    with pytest.raises(Error):
        parse(".type f\n.type r\n")


def test_basic():
    d = parse(BASIC)
    assert d == {
        "ninputs": 4,
        "noutputs": 2,
        "input_labels": ["x", "y", "z"],
        "output_labels": ["f", "g"],
        "intype": FTYPE | RTYPE,
        "cover": {
            ((1, 1, 1, 2), (0, 0)),
            ((1, 1, 2, 1), (0, 1)),
            ((1, 2, 1, 1), (1, 0)),
            ((2, 1, 1, 1), (1, 1))
        },
    }
