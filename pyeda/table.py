"""
Boolean Tables
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

# Positional Cube Notation
#PC_VOID, PC_ONE, PC_ZERO, PC_DC = range(4)

#PC_STR = {
#    PC_ZERO : "0",
#    PC_ONE  : "1",
#    PC_DC   : "*"
#}

#class Table(Scalar):
#    pass
#
#
#class TruthTable(Table):
#
#    def __init__(self, inputs, outputs):
#        self._inputs = inputs
#        self._data = bytearray()
#        self._length = 0
#        pos = 0
#        for pc_val in outputs:
#            if pos == 0:
#                self._data.append(0)
#            self._data[-1] += pc_val << pos
#            self._length += 1
#            pos = (pos + 2) & 0x07
#        assert self._length == 2 ** len(self._inputs)
#
#    def __len__(self):
#        return self._length
#
#    def __str__(self):
#        s = ["f(" + ", ".join(str(v) for v in self._inputs) + ") = "]
#        for i in range(self._length):
#            pos = (i & 0x03) << 1
#            byte = self._data[(i >> 2)] >> pos
#            pc_val = byte & 0x03
#            s.append(PC_STR[pc_val])
#        return "".join(s)
#
#    @property
#    def support(self):
#        return set(self._inputs)
#
#    @property
#    def inputs(self):
#        return self._inputs
