"""
PLA

Interface Functions:
    parse_pla
"""

import re

from pyeda.boolalg.espresso import FTYPE, DTYPE, RTYPE

_COMMENT = re.compile(r"^#.*$")
_NINS = re.compile(r"^.i\s+(\d+)$")
_NOUTS = re.compile(r"^.o\s+(\d+)$")
_PROD = re.compile(r"^.p\s+(\d+)$")
_ILB = re.compile(r"^.ilb\s+(\w+(?:\s+\w+)*)$")
_OB = re.compile(r"^.ob\s+(\w+(?:\s+\w+)*)$")
_TYPE = re.compile(r"^.type\s+(f|r|fd|fr|dr|fdr)$")
_CUBE = re.compile(r"^([01-]+)\s+([01-]+)$")
_END = re.compile(r"^.e(?:nd)?$")

_TYPES = {
    'f': FTYPE,
    'r': RTYPE,
    'fd': FTYPE | DTYPE,
    'fr': FTYPE | RTYPE,
    'dr': DTYPE | RTYPE,
    'fdr': FTYPE | DTYPE | RTYPE,
}

INCODE = {'0': 1, '1': 2, '-': 3}
OUTCODE = {'0': 0, '1': 1, '-': 2}


class PLAError(Exception):
    """An error happened during parsing a PLA file"""
    def __init__(self, msg):
        super(PLAError, self).__init__(msg)


def parse_pla(fin):
    """Parse a file object, and return ..."""
    pla = dict(ninputs=None, noutputs=None,
               input_labels=None, output_labels=None,
               intype=None, cover=set())

    for i, line in enumerate(fin, start=1):
        line = line.strip()

        # skip comments
        if not line or _COMMENT.match(line):
            continue

        # .i
        m_in = _NINS.match(line)
        if m_in:
            if pla['ninputs'] is None:
                try:
                    n = int(m_in.group(1))
                except (TypeError, ValueError) as exc:
                    raise PLAError(".i expected a positive int")
                if n <= 0:
                    raise PLAError(".i expected a positive int")
                pla['ninputs'] = n
            else:
                raise PLAError(".i declared more than once")
            continue

        # .o
        m_out = _NOUTS.match(line)
        if m_out:
            if pla['noutputs'] is None:
                try:
                    n = int(m_out.group(1))
                except (TypeError, ValueError) as exc:
                    raise PLAError(".o expected a positive int")
                if n <= 0:
                    raise PLAError(".o expected a positive int")
                pla['noutputs'] = n
            else:
                raise PLAError(".o declared more than once")
            continue

        # ignore .p
        m_prod = _PROD.match(line)
        if m_prod:
            continue

        # .ilb
        m_ilb = _ILB.match(line)
        if m_ilb:
            if pla['input_labels'] is None:
                pla['input_labels'] = m_ilb.group(1).split()
            else:
                raise PLAError(".ilb declared more than once")
            continue

        # .ob
        m_ob = _OB.match(line)
        if m_ob:
            if pla['output_labels'] is None:
                pla['output_labels'] = m_ob.group(1).split()
            else:
                raise PLAError(".ob declared more than once")
            continue

        # .type
        m_type = _TYPE.match(line)
        if m_type:
            if pla['intype'] is None:
                pla['intype'] = _TYPES[m_type.group(1)]
            else:
                raise PLAError(".type declared more tha once")
            continue

        # cube
        m_cube = _CUBE.match(line)
        if m_cube:
            inputs, outputs = m_cube.groups()
            invec = tuple(INCODE[c] for c in inputs)
            outvec = tuple(OUTCODE[c] for c in outputs)
            pla['cover'].add((invec, outvec))
            continue

        # ignore .e
        m_end = _END.match(line)
        if m_end:
            continue

        raise PLAError("syntax error on line {}: {}".format(i, line))

    return pla

