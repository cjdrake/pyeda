"""
Graphviz IPython magic extensions

Magic methods:
    %dot <dot graph>
    %%dot <dot ...
    ... graph>
    %dotstr "<dot graph>"
    %dotobj obj.to_dot()
    %dotobjs obj[0].to_dot(), obj[1].to_dot(), ...

Usage:

    %load_ext gvmagic
"""

from subprocess import Popen, PIPE

from IPython.core.display import display_svg
from IPython.core.magic import (
    Magics, magics_class,
    line_magic, line_cell_magic
)
from IPython.utils.warn import info, error


def rundot(s):
    """Execute dot and return a raw SVG image, or None."""
    dot = Popen(['dot', '-Tsvg'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = dot.communicate(s.encode('utf-8'))
    status = dot.wait()
    if status == 0:
        return stdoutdata
    else:
        fstr = "dot returned {}\n[==== stderr ====]\n{}"
        error(fstr.format(status, stderrdata.decode('utf-8')))
        return None


@magics_class
class GraphvizMagics(Magics):

    @line_cell_magic
    def dot(self, line, cell=None):
        """dot line magic"""
        if cell is None:
            s = line
        else:
            s = line + '\n' + cell
        data = rundot(s)
        if data:
            display_svg(data, raw=True)

    @line_magic
    def dotstr(self, line):
        """dot string magic"""
        s = self.shell.ev(line)
        data = rundot(s)
        if data:
            display_svg(data, raw=True)

    @line_magic
    def dotobj(self, line):
        """dot object magic"""
        obj = self.shell.ev(line)
        data = rundot(obj.to_dot())
        if data:
            display_svg(data, raw=True)

    @line_magic
    def dotobjs(self, line):
        """dot objects magic"""
        objs = self.shell.ev(line)
        for i, obj in enumerate(objs):
            data = rundot(obj.to_dot())
            if data:
                info("object {}:".format(i))
                display_svg(data, raw=True)


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(GraphvizMagics)
