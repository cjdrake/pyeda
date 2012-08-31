"""
Boolean Logic Expressions

Interface Functions:
    var
    comp

    factor

    f_not
    f_or, f_nor
    f_and, f_nand
    f_xor, f_xnor

Interface Classes:
    Expression
        Literal
        OrAnd
            Or
            And
        BufNot
            Buf
            Not
        Exclusive
            Xor
            Xnor
"""

__copyright__ = "Copyright (c) 2012, Chris Drake"

from pyeda.common import bit_on, cached_property

from pyeda.boolfunc import Variable, Function
from pyeda.constant import boolify

VARIABLES = dict()
COMPLEMENTS = dict()

def var(name, index=None):
    """Return a single variable expression."""
    try:
        ret = VARIABLES[(name, index)]
    except KeyError:
        ret = _Variable(name, index)
        VARIABLES[(name, index)] = ret
    return ret

def comp(v):
    """Return a single complement expression."""
    try:
        ret = COMPLEMENTS[v]
    except KeyError:
        ret = _Complement(v)
        COMPLEMENTS[v] = ret
    return ret

def factor(expr):
    """Return a factored expression."""
    return expr.factor()

# factored operators
def f_not(arg):
    """Return factored NOT expression.

    >>> a, b, c = map(var, "abc")
    >>> f_not(a * b * c), f_not(a + b + c)
    (a' + b' + c', a' * b' * c')
    >>> f_not(-a * b * c), f_not(-a + b + c)
    (a + b' + c', a * b' * c')
    """
    return Not(arg).factor()

def f_or(*args):
    """Return factored OR expression."""
    return Or(*args).factor()

def f_nor(*args):
    """Return factored NOR expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_nor(a, b, c, d)
    a' * b' * c' * d'
    >>> f_nor(-a, b, -c, d)
    a * b' * c * d'
    """
    return Not(Or(*args)).factor()

def f_and(*args):
    """Return factored AND expression."""
    return And(*args).factor()

def f_nand(*args):
    """Return factored NAND expression.

    >>> a, b, c, d = map(var, "abcd")
    >>> f_nand(a, b, c, d)
    a' + b' + c' + d'
    >>> f_nand(-a, b, -c, d)
    a + b' + c + d'
    """
    return Not(And(*args)).factor()

def f_xor(*args):
    """Return factored XOR expression."""
    return Xor(*args).factor()

def f_xnor(*args):
    """Return factored XNOR expression."""
    return Xnor(*args).factor()


class Expression(Function):
    """Boolean function represented by a logic expression"""

    SOP, POS = range(2)

    # From Function
    @cached_property
    def support(self):
        return {v for v in self.iter_vars()}

    def op_not(self):
        return Not(self)

    def op_or(self, *args):
        return Or(self, *args)

    def op_nor(self, *args):
        return Not(Or(self, *args))

    def op_and(self, *args):
        return And(self, *args)

    def op_nand(self, *args):
        return Not(And(self, *args))

    def op_xor(self, *args):
        return Xor(self, *args)

    def op_xnor(self, *args):
        return Xnor(self, *args)

    def op_le(self, *args):
        return _less_equal(self, *args) if args else self

    def op_ge(self, *args):
        return _greater_equal(self, *args) if args else self

    def satisfy_one(self, algorithm='naive'):
        if algorithm == 'naive':
            return naive_sat_one(self)
        else:
            raise ValueError("invalid algorithm")

    def satisfy_count(self, algorithm='naive'):
        return len(self.satisfy_all(algorithm))

    def is_neg_unate(self, vs=None):
        if vs is None:
            vs = self.support
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in {0, 1} or fv1 in {0, 1}:
                if not (fv0 == 1 or fv1 == 0):
                    return False
            elif not fv0.min_indices >= fv1.min_indices:
                return False
        return True

    def is_pos_unate(self, vs=None):
        if vs is None:
            vs = self.support
        for v in vs:
            fv0, fv1 = self.cofactors(v)
            if fv0 in {0, 1} or fv1 in {0, 1}:
                if not (fv1 == 1 or fv0 == 0):
                    return False
            elif not fv1.min_indices >= fv0.min_indices:
                return False
        return True

    def smoothing(self, vs=None):
        return Or(*self.cofactors(vs))

    def consensus(self, vs=None):
        return And(*self.cofactors(vs))

    def derivative(self, vs=None):
        return Xor(*self.cofactors(vs))

    # Specific to Expression
    def __lt__(self, other):
        """Implementing this function makes expressions sortable."""
        raise NotImplementedError()

    def __repr__(self):
        """Return a printable representation."""
        return self.__str__()

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    @property
    def depth(self):
        """The number of levels in the expression tree."""
        raise NotImplementedError()

    def invert(self):
        """Return an inverted expression."""
        raise NotImplementedError()

    def factor(self):
        """Return a factored expression.

        A factored expression is one and only one of the following:
        * A literal.
        * A sum / product of factored expressions.
        """
        raise NotImplementedError()

    @cached_property
    def inputs(self):
        """Return the support set in name/index order."""
        return sorted(self.support)

    def iter_outputs(self):
        for n in range(2 ** self.degree):
            point = {v: bit_on(n, i) for i, v in enumerate(self.inputs)}
            yield point, self.restrict(point)

    def iter_vars(self):
        """Recursively iterate through all variables in the expression."""
        raise NotImplementedError()

    def iter_minterms(self):
        """Iterate through the sum of products of N literals."""
        for point, output in self.iter_outputs():
            if output:
                space = [(v if v_on else -v) for v, v_on in point.items()]
                yield And(*space)

    @cached_property
    def minterms(self):
        """The sum of products of N literals"""
        return {term for term in self.iter_minterms()}

    def iter_maxterms(self):
        """Iterate through the product of sums of N literals."""
        for point, output in self.iter_outputs():
            if not output:
                space = [(-v if v_on else v) for v, v_on in point.items()]
                yield Or(*space)

    @cached_property
    def maxterms(self):
        """The product of sums of N literals"""
        return {term for term in self.iter_maxterms()}

    def is_sop(self):
        """Return whether this expression is a sum of products."""
        return False

    def to_sop(self):
        """Return the expression as a sum of products.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_sop()
        a' * b' * c + a' * b * c' + a * b' * c' + a * b * c
        >>> Xnor(a, b, c).to_sop()
        a' * b' * c' + a' * b * c + a * b' * c + a * b * c'
        """
        return self.factor()._flatten(And).absorb()

    def to_csop(self):
        """Return the expression as a sum of products of N literals."""
        return Or(*[term for term in self.iter_minterms()])

    def is_pos(self):
        """Return whether this expression is a products of sums."""
        return False

    def to_pos(self):
        """Return the expression as a product of sums.

        >>> a, b, c = map(var, "abc")
        >>> Xor(a, b, c).to_pos()
        (a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)
        >>> Xnor(a, b, c).to_pos()
        (a + b + c') * (a + b' + c) * (a' + b + c) * (a' + b' + c')
        """
        return self.factor()._flatten(Or).absorb()

    def to_cpos(self):
        """Return the expression as a product of sums of N literals."""
        return And(*[term for term in self.iter_maxterms()])

    @cached_property
    def min_indices(self):
        """Return the minterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).min_indices
        set([3, 5, 6, 7])
        """
        return {term.minterm_index for term in self.iter_minterms()}

    @cached_property
    def max_indices(self):
        """Return the maxterm indices.

        >>> a, b, c = map(var, "abc")
        >>> (a * b + a * c + b * c).max_indices
        set([0, 1, 2, 4])
        """
        return {term.maxterm_index for term in self.iter_maxterms()}

    def equals(self, other):
        """Return whether this expression is equivalent to another.

        NOTE: This algorithm uses exponential time and memory.
        """
        if self.support == other.support:
            return self.min_indices == other.min_indices
        else:
            return False

    def _get_replace(self, constraints):
        replace = dict()
        for i, arg in enumerate(self.args):
            new_arg = arg.restrict(constraints)
            if id(new_arg) != id(arg):
                replace[i] = new_arg
        return replace


class Literal(Expression):
    """An instance of a variable or of its complement"""

    # From Expression
    @property
    def depth(self):
        return 0

    def factor(self):
        return self

    # Specific to Literal
    @property
    def args(self):
        return {self}

    @property
    def _oidx(self):
        """Return an index for ordering comparison."""
        return (-1 if self.index is None else self.index)


class _Variable(Variable, Literal):
    """Boolean variable (expression)"""

    def __init__(self, name, index=None):
        Variable.__init__(self, name, index)
        Literal.__init__(self)

    # From Function
    def restrict(self, constraints):
        try:
            return boolify(constraints[self])
        except KeyError:
            return self

    def compose(self, constraints):
        try:
            return constraints[self]
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, Literal):
            return (self.name < other.name or
                    self.name == other.name and self._oidx < other._oidx)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return comp(self)

    def iter_vars(self):
        yield self

    # Specific to _Variable
    @property
    def minterm_index(self):
        return 1

    @property
    def maxterm_index(self):
        return 0


class _Complement(Literal):
    """Boolean complement"""

    # Postfix symbol used in string representation
    OP = "'"

    def __init__(self, v):
        self._var = v

    # From Function
    def restrict(self, constraints):
        try:
            return Not(constraints[self._var])
        except KeyError:
            return self

    def compose(self, constraints):
        try:
            return Not(constraints[self._var])
        except KeyError:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, _Variable):
            return (self.name < other.name or
                    self.name == other.name and self._oidx <= other._oidx)
        if isinstance(other, _Complement):
            return (self.name < other.name or
                    self.name == other.name and self._oidx < other._oidx)
        if isinstance(other, Expression):
            return True
        return id(self) < id(other)

    def invert(self):
        return self._var

    def iter_vars(self):
        yield self._var

    # Specific to _Complement
    def __str__(self):
        return str(self._var) + self.OP

    @property
    def var(self):
        return self._var

    @property
    def name(self):
        return self._var.name

    @property
    def index(self):
        return self._var.index

    # Specific to _Complement
    @property
    def minterm_index(self):
        return 0

    @property
    def maxterm_index(self):
        return 1


class OrAnd(Expression):
    """Base class for Boolean OR/AND expressions"""

    def __new__(cls, *args):
        temps, args = list(args), list()
        while temps:
            arg = temps.pop()
            if isinstance(arg, Expression):
                # associative
                if isinstance(arg, cls):
                    temps.extend(arg.args)
                # complement
                elif -arg in args:
                    return cls.DOMINATOR
                # idempotent
                elif arg not in args:
                    args.append(arg)
            else:
                num = boolify(arg)
                # domination
                if num == cls.DOMINATOR:
                    return cls.DOMINATOR

        if len(args) == 0:
            return cls.IDENTITY
        if len(args) == 1:
            return args[0]

        self = super(OrAnd, cls).__new__(cls)
        self.args = args
        return self

    # From Function
    def restrict(self, constraints):
        replace = self._get_replace(constraints)
        if replace:
            args = self.args[:]
            for i, new_arg in replace.items():
                # speed hack
                if new_arg == self.DOMINATOR:
                    return self.DOMINATOR
                else:
                    args[i] = new_arg
            return self.__class__(*args)
        else:
            return self

    def compose(self, constraints):
        replace = self._get_replace(constraints)
        if replace:
            args = self.args[:]
            for i, new_arg in replace.items():
                args[i] = new_arg
            return self.__class__(*args)
        else:
            return self

    # From Expression
    def __lt__(self, other):
        if isinstance(other, Literal):
            return self.support < other.support
        if isinstance(other, self.__class__) and self.depth == other.depth == 1:
            # min/max term
            if self.support == other.support:
                return self.term_index < other.term_index
            else:
                # support containment
                if self.support < other.support:
                    return True
                if other.support < self.support:
                    return False
                # support disjoint
                v = sorted(self.support ^ other.support)[0]
                if v in self.support:
                    return True
                if v in other.support:
                    return False
        return id(self) < id(other)

    @cached_property
    def depth(self):
        return max(arg.depth + 1 for arg in self.args)

    def invert(self):
        return self.DUAL(*[Not(arg) for arg in self.args])

    def factor(self):
        return self.__class__(*[arg.factor() for arg in self.args])

    def iter_vars(self):
        for arg in self.args:
            for v in arg.iter_vars():
                yield v

    # Specific to OrAnd
    def absorb(self):
        """Return the OR/AND expression after absorption.

        x + (x * y) = x
        x * (x + y) = x

        The reason this is not included as an automatic simplification is that
        it is too expensive to put into the constructor. We have to check
        whether each term is a subset of another term, which is N^3.
        """
        clauses, args = list(), list()
        for arg in self.args:
            if isinstance(arg, Literal) or arg.depth == 1:
                clauses.append(arg)
            else:
                args.append(arg)

        # Drop all clauses that are a subset of other clauses
        while clauses:
            fst, rst, clauses = clauses[0], clauses[1:], list()
            drop_fst = False
            for term in rst:
                drop_clause = False
                if fst.equals(term):
                    drop_clause = True
                else:
                    if all(any(farg.equals(targ) for targ in term.args)
                           for farg in fst.args):
                        drop_clause = True
                    if all(any(farg.equals(targ) for targ in fst.args)
                           for farg in term.args):
                        drop_fst = True
                if not drop_clause:
                    clauses.append(term)
            if not drop_fst:
                args.append(fst)

        return self.__class__(*args)

    def _flatten(self, op):
        """Return a flattened OR/AND expression.

        Use the distributive law to flatten all nested expressions:
        x + (y * z) = (x + y) * (x + z)
        x * (y + z) = (x * y) + (x * z)

        NOTE: This function assumes the expression is already factored. Do NOT
              call this method directly -- use the "to_sop" or "to_pos" methods
              instead.
        """
        if isinstance(self, op):
            for i, arg in enumerate(self.args):
                if isinstance(arg, self.DUAL):
                    others = self.args[:i] + self.args[i+1:]
                    expr = op.DUAL(*[op(a, *others) for a in arg.args])
                    if isinstance(expr, OrAnd):
                        return expr._flatten(op)
                    else:
                        return expr
            else:
                return self
        else:
            nested, others = list(), list()
            for arg in self.args:
                if arg.depth > 1:
                    nested.append(arg)
                else:
                    others.append(arg)
            args = [arg._flatten(op) for arg in nested] + others
            return op.DUAL(*args)


class Or(OrAnd):
    """Boolean addition (or) operator

    >>> a, b, c = map(var, "abc")
    >>> Or(), Or(a)
    (0, a)
    >>> a + 1, a + b + 1, a + 0
    (1, 1, a)
    >>> -a + a, -a + a + b
    (1, 1)
    >>> Or.DUAL is And
    True
    """

    # Infix symbol used in string representation
    OP = "+"

    IDENTITY = 0
    DOMINATOR = 1

    def __str__(self):
        sep = " " + self.OP + " "
        return sep.join(str(arg) for arg in sorted(self.args))

    def is_sop(self):
        return self.depth == 1

    # Specific to Or
    @property
    def term_index(self):
        return self.maxterm_index

    @cached_property
    def maxterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if -v in self.args:
                index |= 1 << (n - i)
        return index


class And(OrAnd):
    """Boolean multiplication (and) operator

    >>> a, b, c = map(var, "abc")
    >>> And(), And(a)
    (1, a)
    >>> a * 0, a * b * 0, a * 1
    (0, 0, a)
    >>> -a * a, -a * a * b
    (0, 0)
    >>> And.DUAL is Or
    True
    """

    # Infix symbol used in string representation
    OP = "*"

    IDENTITY = 1
    DOMINATOR = 0

    def __str__(self):
        s = list()
        for arg in sorted(self.args):
            if isinstance(arg, Or):
                s.append("(" + str(arg) + ")")
            else:
                s.append(str(arg))
        sep = " " + self.OP + " "
        return sep.join(s)

    def is_pos(self):
        return self.depth == 1

    # Specific to And
    @property
    def term_index(self):
        return self.minterm_index

    @cached_property
    def minterm_index(self):
        if self.depth > 1:
            return None
        n = self.degree - 1
        index = 0
        for i, v in enumerate(self.inputs):
            if v in self.args:
                index |= 1 << (n - i)
        return index


Or.DUAL = And
And.DUAL = Or


class BufNot(Expression):
    """Base class for BUF/NOT operators"""

    def __init__(self, arg):
        self.arg = arg

    # From Function
    def compose(self, constraints):
        expr = self.arg.restrict(constraints)
        if id(expr) == id(self.arg):
            return self
        else:
            return self.__class__(expr)

    # From Expression
    @property
    def depth(self):
        return self.arg.depth

    def iter_vars(self):
        for v in self.arg.iter_vars():
            yield v

    # Specific to BufNot
    @property
    def args(self):
        return {self.arg}


class Buf(BufNot):
    """buffer operator

    >>> a = var('a')
    >>> Buf(0), Buf(1)
    (0, 1)
    >>> Buf(-a), Buf(a)
    (a', a)
    >>> Buf(Buf(a)), Buf(Buf(Buf(a))), Buf(Buf(Buf(Buf(a))))
    (a, a, a)
    >>> Buf(a + -a), Buf(a * -a)
    (1, 0)
    """

    def __new__(cls, arg):
        # Auto-simplify numbers and literals
        if isinstance(arg, Expression):
            if isinstance(arg, Literal):
                return arg
            else:
                return super(Buf, cls).__new__(cls)
        else:
            return boolify(arg)

    def __str__(self):
        return "Buf({0.arg})".format(self)

    # From Function
    def restrict(self, constraints):
        arg = self.arg.restrict(constraints)
        # speed hack
        if arg in {0, 1}:
            return arg
        elif id(arg) == id(self.arg):
            return self
        else:
            return self.__class__(arg)

    # From Expression
    def invert(self):
        return Not(self.arg)

    def factor(self):
        return self.arg.factor()


class Not(BufNot):
    """Boolean NOT operator

    >>> a = var('a')
    >>> Not(0), Not(1)
    (1, 0)
    >>> Not(-a), Not(a)
    (a, a')
    >>> -(-a), -(-(-a)), -(-(-(-a)))
    (a, a', a)
    >>> Not(a + -a), Not(a * -a)
    (0, 1)
    """

    def __new__(cls, arg):
        # Auto-simplify numbers and literals
        if isinstance(arg, Expression):
            if isinstance(arg, Literal):
                return arg.invert()
            else:
                return super(Not, cls).__new__(cls)
        else:
            return 1 - boolify(arg)

    def __str__(self):
        return "Not({0.arg})".format(self)

    # From Function
    def restrict(self, constraints):
        arg = self.arg.restrict(constraints)
        # speed hack
        if arg in {0, 1}:
            return 1 - arg
        elif id(arg) == id(self.arg):
            return self
        else:
            return self.__class__(arg)

    # From Expression
    def invert(self):
        return self.arg

    def factor(self):
        return self.arg.invert().factor()


class Exclusive(Expression):
    """Boolean exclusive (XOR, XNOR) operator"""

    IDENTITY = 0

    def __new__(cls, *args):
        parity = cls.PARITY
        temps, args = list(args), list()
        while temps:
            arg = temps.pop()
            if isinstance(arg, Expression):
                # associative
                if isinstance(arg, cls):
                    temps.extend(arg.args)
                # XOR(x, x') = 1
                elif -arg in args:
                    args.remove(-arg)
                    parity ^= 1
                # XOR(x, x) = 0
                elif arg in args:
                    args.remove(arg)
                else:
                    args.append(arg)
            else:
                parity ^= boolify(arg)

        if len(args) == 0:
            return Not(cls.IDENTITY) if parity else cls.IDENTITY
        if len(args) == 1:
            return Not(args[0]) if parity else args[0]

        self = super(Exclusive, cls).__new__(cls)
        self.args = args
        self._parity = parity
        return self

    def __str__(self):
        args = ", ".join(str(arg) for arg in self.args)
        if self._parity:
            return "Xnor(" + args + ")"
        else:
            return "Xor(" + args + ")"

    # From Function
    def restrict(self, constraints):
        return self.compose(constraints)

    def compose(self, constraints):
        replace = self._get_replace(constraints)
        if replace:
            args = self.args[:]
            for i, new_arg in replace.items():
                args[i] = new_arg
            return Xnor(*args) if self._parity else Xor(*args)
        else:
            return self

    # From Expression
    @property
    def depth(self):
        """
        >>> a, b, c, d, e = map(var, "abcde")
        >>> Xor(a, b, c).depth
        2
        >>> Xor(a, b, c + d).depth
        3
        >>> Xor(a, b, c + Xor(d, e)).depth
        5
        """
        return max(arg.depth + 2 for arg in self.args)

    def invert(self):
        if self._parity == Xor.PARITY:
            return Xnor(*self.args)
        else:
            return Xor(*self.args)

    def factor(self):
        arg, args = self.args[0], self.args[1:]
        if self._parity == Xor.PARITY:
            return Or(And(Not(arg), Xor(*args)), And(arg, Xnor(*args))).factor()
        else:
            return Or(And(Not(arg), Xnor(*args)), And(arg, Xor(*args))).factor()

    def iter_vars(self):
        for arg in self.args:
            for v in arg.iter_vars():
                yield v


class Xor(Exclusive):
    """Boolean Exclusive OR (XOR) operator

    >>> a, b, c = map(var, "abc")
    >>> Xor(), Xor(a)
    (0, a)
    >>> Xor(0, 0), Xor(0, 1), Xor(1, 0), Xor(1, 1)
    (0, 1, 1, 0)
    >>> Xor(a, a), Xor(a, -a)
    (0, 1)
    """
    PARITY = 0

class Xnor(Exclusive):
    """Boolean Exclusive NOR (XNOR) operator

    >>> a, b, c = map(var, "abc")
    >>> Xnor(), Xnor(a)
    (1, a')
    >>> Xnor(0, 0), Xnor(0, 1), Xnor(1, 0), Xnor(1, 1)
    (1, 0, 0, 1)
    >>> Xnor(a, a), Xnor(a, -a)
    (1, 0)
    """
    PARITY = 1


def _less_equal(*args):
    """Return factored form of Boolean less than or equal operator."""
    if len(args) == 1:
        return args[0]
    else:
        return Or(Not(args[0]), _less_equal(*args[1:]))

def _greater_equal(*args):
    """Return factored form of Boolean greater than or equal operator."""
    if len(args) == 1:
        return Not(args[0])
    else:
        return Or(args[0], _greater_equal(*args[1:]))

def naive_sat_one(expr):
    """
    >>> a, b = map(var, "ab")
    >>> point = (-a * b).satisfy_one(algorithm='naive')
    >>> point[a], point[b]
    (0, 1)
    >>> (-a * -b + -a * b + a * -b + a * b).satisfy_one(algorithm='naive')
    {}
    >>> (a * b * (-a + -b)).satisfy_one(algorithm='naive')
    """
    fst, rst = expr.inputs[0], expr.inputs[1:]
    cf0, cf1 = expr.cofactors(fst)
    if cf0 == 0:
        if cf1 == 0:
            point = None
        elif cf1 == 1:
            point = {fst: 1}
        else:
            point = naive_sat_one(cf1)
            if point is not None:
                point[fst] = 1
    elif cf0 == 1:
        if cf1 == 1:
            point = {}
        else:
            point = {fst: 0}
    else:
        point = naive_sat_one(cf0)
        if point is not None:
            point[fst] = 0
    return point
