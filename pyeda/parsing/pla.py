"""
PLA

This is a partial implementation of the Berkeley PLA format.
See extension/espresso/html/espresso.5.html for details.

Exceptions:
    PLAError

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

_INCODE = {'0': 1, '1': 2, '-': 3}
_OUTCODE = {'0': 0, '1': 1, '-': 2}


class PLAError(Exception):
    """An error happened during parsing a PLA file"""


def parse_pla(s):
    """
    Parse an input string in PLA format,
    and return an intermediate representation dict.

    Parameters
    ----------
    s : str
        String containing a PLA.

    Returns
    -------
    A dict with all PLA information:

        ===============  ============  =================================
         Key              Value type    Value description
        ===============  ============  =================================
         ninputs          int           Number of inputs
         noutputs         int           Number of outputs
         input_labels     list          Input variable names
         output_labels    list          Output function names
         intype           int           Cover type: {F, R, FD, FR, DR, FDR}
         cover            set           Implicant table
        ===============  ============  =================================
    """
    pla = dict(ninputs=None, noutputs=None,
               input_labels=None, output_labels=None,
               intype=None, cover=set())

    lines = [line.strip() for line in s.splitlines()]
    for i, line in enumerate(lines, start=1):
        # skip comments
        if not line or _COMMENT.match(line):
            continue

        # .i
        m_in = _NINS.match(line)
        if m_in:
            if pla['ninputs'] is None:
                pla['ninputs'] = int(m_in.group(1))
                continue
            else:
                raise PLAError(".i declared more than once")

        # .o
        m_out = _NOUTS.match(line)
        if m_out:
            if pla['noutputs'] is None:
                pla['noutputs'] = int(m_out.group(1))
                continue
            else:
                raise PLAError(".o declared more than once")

        # ignore .p
        m_prod = _PROD.match(line)
        if m_prod:
            continue

        # .ilb
        m_ilb = _ILB.match(line)
        if m_ilb:
            if pla['input_labels'] is None:
                pla['input_labels'] = m_ilb.group(1).split()
                continue
            else:
                raise PLAError(".ilb declared more than once")

        # .ob
        m_ob = _OB.match(line)
        if m_ob:
            if pla['output_labels'] is None:
                pla['output_labels'] = m_ob.group(1).split()
                continue
            else:
                raise PLAError(".ob declared more than once")

        # .type
        m_type = _TYPE.match(line)
        if m_type:
            if pla['intype'] is None:
                pla['intype'] = _TYPES[m_type.group(1)]
                continue
            else:
                raise PLAError(".type declared more tha once")

        # cube
        m_cube = _CUBE.match(line)
        if m_cube:
            inputs, outputs = m_cube.groups()
            invec = tuple(_INCODE[c] for c in inputs)
            outvec = tuple(_OUTCODE[c] for c in outputs)
            pla['cover'].add((invec, outvec))
            continue

        # ignore .e
        m_end = _END.match(line)
        if m_end:
            continue

        raise PLAError("syntax error on line {}: {}".format(i, line))

    return pla

