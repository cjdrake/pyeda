/*
** Filename: exprnodemodule.c
**
** Python wrapper for C expression nodes
*/

#include <Python.h>

#include <stdbool.h>
#include "boolexpr.h"

#define NODE(x) (((ExprNode *) x)->ex)


/* Globals */
static const char *ASTOPS[] = {
    "const",
    "lit",

    "or",
    "and",
    "xor",
    "eq",
    "not",
    "impl",
    "ite",
};


PyDoc_STRVAR(Error_doc,
    "Classify all ExprNode errors"
);

static PyObject *Error;


PyDoc_STRVAR(ExprNode_doc,
    "A node in an expression tree.\n\
\n\
    This is a light-weight wrapper around the C BoolExpr data type.\n\
    "
);

typedef struct {
    PyObject_HEAD

    struct BoolExpr *ex;
    struct BX_Iter *it;
} ExprNode;


static ExprNode *Zero;
static ExprNode *One;


static struct BX_Vector *lits;


static PyObject *
ExprNode_iter(ExprNode *self)
{
    self->it = BX_Iter_New(self->ex);
    if (self->it == NULL)
        return NULL;

    Py_INCREF((PyObject *) self);

    return (PyObject *) self;
}


static PyObject * ExprNode_next(ExprNode *self);


/* ExprNode.restrict() */
PyDoc_STRVAR(restrict_doc,
    "this is the ExprNode.restrict() docstring"
);

static PyObject *
ExprNode_restrict(ExprNode *self, PyObject *args);


/* ExprNode.compose() */
PyDoc_STRVAR(compose_doc,
    "this is the ExprNode.compose() docstring"
);

static PyObject *
ExprNode_compose(ExprNode *self, PyObject *args);


/* ExprNode.id() */
PyDoc_STRVAR(id_doc,
    "Return the int id of the expression."
);

static PyObject *
ExprNode_id(ExprNode *self)
{
    return PyLong_FromLong((long) self->ex);
}


/* Recursive component of ExprNode_to_ast */
static PyObject *
_node2ast(struct BoolExpr *ex)
{
    PyObject *ast;

    if (BX_IS_CONST(ex)) {
        PyObject *s, *l;

        s = PyUnicode_FromString(ASTOPS[0]);
        if (s == NULL)
            return NULL;

        l = PyLong_FromLong((long) ex->kind);
        if (l == NULL) {
            Py_DECREF(s);
            return NULL;
        }

        ast = PyTuple_New(2);
        if (ast == NULL) {
            Py_DECREF(s);
            Py_DECREF(l);
            return NULL;
        }

        PyTuple_SET_ITEM(ast, 0, s);
        PyTuple_SET_ITEM(ast, 1, l);
    }
    else if (BX_IS_LIT(ex)) {
        PyObject *s, *l;

        s = PyUnicode_FromString(ASTOPS[1]);
        if (s == NULL)
            return NULL;

        l = PyLong_FromLong(ex->data.lit.uniqid);
        if (l == NULL) {
            Py_DECREF(s);
            return NULL;
        }

        ast = PyTuple_New(2);
        if (ast == NULL) {
            Py_DECREF(s);
            Py_DECREF(l);
            return NULL;
        }

        PyTuple_SET_ITEM(ast, 0, s);
        PyTuple_SET_ITEM(ast, 1, l);
    }
    else {
        int i, j;
        PyObject *s;

        /* FIXME: magic number: 6 */
        s = PyUnicode_FromString(ASTOPS[(int) (ex->kind - 6)]);
        if (s == NULL)
            return NULL;

        PyObject **asts;

        asts = (PyObject **) PyMem_Malloc(ex->data.xs->length * sizeof(PyObject *));
        if (asts == NULL) {
            Py_DECREF(s);
            return NULL;
        }

        for (i = 0; i < ex->data.xs->length; ++i) {
            asts[i] = _node2ast(ex->data.xs->items[i]);
            if (asts[i] == NULL) {
                Py_DECREF(s);
                for (j = 0; j < i; ++j)
                    Py_DECREF(asts[j]);
                PyMem_Free(asts);
                return NULL;
            }
        }

        ast = PyTuple_New(1 + ex->data.xs->length);
        if (ast == NULL) {
            Py_DECREF(s);
            for (i = 0; i < ex->data.xs->length; ++i)
                Py_DECREF(asts[i]);
            PyMem_Free(asts);
            return NULL;
        }

        PyTuple_SET_ITEM(ast, 0, s);
        for (i = 0; i < ex->data.xs->length; ++i)
            PyTuple_SET_ITEM(ast, i+1, asts[i]);

        PyMem_Free(asts);
    }

    return ast;
}


/* ExprNode.to_ast() */
PyDoc_STRVAR(to_ast_doc,
    "Convert this node to an abstract syntax tree."
);

static PyObject *
ExprNode_to_ast(ExprNode *self)
{
    return _node2ast(self->ex);
}


/* ExprNode.kind() */
PyDoc_STRVAR(kind_doc,
    "Return the int kind of the expression."
);

static PyObject *
ExprNode_kind(ExprNode *self)
{
    return PyLong_FromLong((long) self->ex->kind);
}


/* ExprNode.data() */
PyDoc_STRVAR(data_doc,
    "Return the node's data payload.\n\
\n\
    For constants, return the int positional cube notation.\n\
    For literals, return the int uniqid.\n\
    For operators, return a tuple of argument nodes.\n\
    "
);

static PyObject *
ExprNode_data(ExprNode *self);


/* ExprNode.depth() */
PyDoc_STRVAR(depth_doc,
    "Return the depth of the expression.\n\
\n\
    Expression depth is defined recursively:\n\
\n\
    1. An atom node (constant or literal) has zero depth.\n\
    2. A branch node (operator) has depth equal to the maximum depth of\n\
       its children (arguments) plus one.\n\
    "
);

static PyObject *
ExprNode_depth(ExprNode *self)
{
    return PyLong_FromLong((long) BX_Depth(self->ex));
}


/* ExprNode.size() */
PyDoc_STRVAR(size_doc,
    "Return the size of the expression.\n\
\n\
    1. An atom node (constant or literal) has size one.\n\
    2. A branch node (operator) has size equal to the sum of its children's\n\
       sizes plus one.\n\
    "
);

static PyObject *
ExprNode_size(ExprNode *self)
{
    return PyLong_FromLong((long) BX_Size(self->ex));
}


/* ExprNode.is_dnf() */
PyDoc_STRVAR(is_dnf_doc,
    "Return True if the expression is in disjunctive normal form."
);

static PyObject *
ExprNode_is_dnf(ExprNode *self)
{
    return PyBool_FromLong((long) BX_IsDNF(self->ex));
}


/* ExprNode.is_cnf() */
PyDoc_STRVAR(is_cnf_doc,
    "Return True if the expression is in conjunctive normal form."
);

static PyObject *
ExprNode_is_cnf(ExprNode *self)
{
    return PyBool_FromLong((long) BX_IsCNF(self->ex));
}


/* ExprNode.pushdown_not() */
PyDoc_STRVAR(pushdown_not_doc,
    "Return a simplified expression.\n\
\n\
    Simplification eliminates constants, and all sub-expressions that can be\n\
    easily converted to constants.\n\
    "
);

static PyObject *
ExprNode_pushdown_not(ExprNode *self);


/* ExprNode.simplify() */
PyDoc_STRVAR(simplify_doc,
    "Return a simplified expression.\n\
\n\
    Simplification eliminates constants, and all sub-expressions that can be\n\
    easily converted to constants.\n\
    "
);

static PyObject *
ExprNode_simplify(ExprNode *self);


/* ExprNode.to_binary() */
PyDoc_STRVAR(to_binary_doc,
    "Convert all N-ary arguments to binary arguments."
);

static PyObject *
ExprNode_to_binary(ExprNode *self);


/* ExprNode.simple() */
PyDoc_STRVAR(simple_doc,
    "Return True if this node is simple."
);

static PyObject *
ExprNode_simple(ExprNode *self)
{
    return PyBool_FromLong((long) self->ex->flags & BX_SIMPLE);
}


/* ExprNode.to_nnf() */
PyDoc_STRVAR(to_nnf_doc,
    "Return an expression in negation normal form."
);

static PyObject *
ExprNode_to_nnf(ExprNode *self);


/* ExprNode.to_dnf() */
PyDoc_STRVAR(to_dnf_doc,
    "Return an expression in disjunctive normal form."
);

static PyObject *
ExprNode_to_dnf(ExprNode *self);


/* ExprNode.to_cnf() */
PyDoc_STRVAR(to_cnf_doc,
    "Return an expression in conjunctive normal form."
);

static PyObject *
ExprNode_to_cnf(ExprNode *self);


/* ExprNode.complete_sum() */
PyDoc_STRVAR(complete_sum_doc,
    "Return a DNF expression that contains all prime implicants."
);

static PyObject *
ExprNode_complete_sum(ExprNode *self);


static PyMethodDef
ExprNode_methods[] = {
    {"restrict", (PyCFunction) ExprNode_restrict, METH_VARARGS, restrict_doc},
    {"compose",  (PyCFunction) ExprNode_compose,  METH_VARARGS, compose_doc},

    {"id",           (PyCFunction) ExprNode_id,           METH_NOARGS, id_doc},
    {"to_ast",       (PyCFunction) ExprNode_to_ast,       METH_NOARGS, to_ast_doc},
    {"kind",         (PyCFunction) ExprNode_kind,         METH_NOARGS, kind_doc},
    {"data",         (PyCFunction) ExprNode_data,         METH_NOARGS, data_doc},
    {"depth",        (PyCFunction) ExprNode_depth,        METH_NOARGS, depth_doc},
    {"size",         (PyCFunction) ExprNode_size,         METH_NOARGS, size_doc},
    {"is_dnf",       (PyCFunction) ExprNode_is_dnf,       METH_NOARGS, is_dnf_doc},
    {"is_cnf",       (PyCFunction) ExprNode_is_cnf,       METH_NOARGS, is_cnf_doc},
    {"pushdown_not", (PyCFunction) ExprNode_pushdown_not, METH_NOARGS, pushdown_not_doc},
    {"simplify",     (PyCFunction) ExprNode_simplify,     METH_NOARGS, simplify_doc},
    {"simple",       (PyCFunction) ExprNode_simple,       METH_NOARGS, simple_doc},
    {"to_binary",    (PyCFunction) ExprNode_to_binary,    METH_NOARGS, to_binary_doc},
    {"to_nnf",       (PyCFunction) ExprNode_to_nnf,       METH_NOARGS, to_nnf_doc},
    {"to_dnf",       (PyCFunction) ExprNode_to_dnf,       METH_NOARGS, to_dnf_doc},
    {"to_cnf",       (PyCFunction) ExprNode_to_cnf,       METH_NOARGS, to_cnf_doc},
    {"complete_sum", (PyCFunction) ExprNode_complete_sum, METH_NOARGS, complete_sum_doc},

    {NULL}  /* sentinel */
};


static void
ExprNode_dealloc(ExprNode *self)
{
    BX_DecRef(self->ex);
    Py_TYPE(self)->tp_free((PyObject *) self);
}


static PyObject *
ExprNode_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    ExprNode *self = (ExprNode *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}


static int
ExprNode_init(ExprNode *self, PyObject *args, PyObject *kwargs)
{
    self->it = (struct BX_Iter *) NULL;
    return 0;
}


static PyTypeObject
ExprNode_T = {
    PyVarObject_HEAD_INIT(NULL, 0)

    "exprnode.ExprNode",        /* tp_name */
    sizeof(ExprNode),           /* tp_basicsize */
    0,                          /* tp_itemsize */
    (destructor)
        ExprNode_dealloc,       /* tp_dealloc */
    0,                          /* tp_print */
    0,                          /* tp_getattr */
    0,                          /* tp_setattr */
    0,                          /* tp_reserved */
    0,                          /* tp_repr */
    0,                          /* tp_as_number */
    0,                          /* tp_as_sequence */
    0,                          /* tp_as_mapping */
    0,                          /* tp_hash  */
    0,                          /* tp_call */
    0,                          /* tp_str */
    0,                          /* tp_getattro */
    0,                          /* tp_setattro */
    0,                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,         /* tp_flags */
    ExprNode_doc,               /* tp_doc */
    0,                          /* tp_traverse */
    0,                          /* tp_clear */
    0,                          /* tp_richcompare */
    0,                          /* tp_weaklistoffset */
    (getiterfunc)
        ExprNode_iter,          /* tp_iter */
    (iternextfunc)
        ExprNode_next,          /* tp_iternext */
    ExprNode_methods,           /* tp_methods */
    0,                          /* tp_members */
    0,                          /* tp_getset */
    0,                          /* tp_base */
    0,                          /* tp_dict */
    0,                          /* tp_descr_get */
    0,                          /* tp_descr_set */
    0,                          /* tp_dictoffset */
    (initproc)
        ExprNode_init,          /* tp_init */
    0,                          /* tp_alloc */
    (newfunc)
        ExprNode_new,           /* tp_new */
};


static PyObject *
ExprNode_next(ExprNode *self)
{
    ExprNode *node;

    if (self->it->done) {
        BX_Iter_Del(self->it);
        /* StopIteration */
        return NULL;
    }

    node = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (node == NULL) {
        BX_Iter_Del(self->it);
        return NULL;
    }
    node->ex = BX_IncRef(self->it->item);

    BX_Iter_Next(self->it);

    return (PyObject *) node;
}


/* ExprNode.restrict() */
static PyObject *
ExprNode_restrict(ExprNode *self, PyObject *args)
{
    PyObject *point;
    struct BoolExpr *ex;

    Py_ssize_t pos = 0;
    PyObject *key, *val;

    struct BX_Dict *var2ex;

    if (!PyArg_ParseTuple(args, "O", &point))
        return NULL;

    if (!PyDict_Check(point)) {
        PyErr_SetString(PyExc_TypeError, "expected point to be a dict");
        return NULL;
    }

    var2ex = BX_Dict_New();
    /* FIXME: check var2ex == NULL */
    while (PyDict_Next(point, &pos, &key, &val)) {
        BX_Dict_Insert(var2ex, NODE(key), NODE(val));
    }

    if ((ex = BX_Restrict(self->ex, var2ex)) == NULL) {
        BX_Dict_Del(var2ex);
        PyErr_SetString(Error, "BX_Restrict failed");
        return NULL;
    }

    BX_Dict_Del(var2ex);

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


/* ExprNode.compose() */
static PyObject *
ExprNode_compose(ExprNode *self, PyObject *args)
{
    PyObject *mapping;
    struct BoolExpr *ex;

    Py_ssize_t pos = 0;
    PyObject *key, *val;

    struct BX_Dict *var2ex;

    if (!PyArg_ParseTuple(args, "O", &mapping))
        return NULL;

    if (!PyDict_Check(mapping)) {
        PyErr_SetString(PyExc_TypeError, "expected mapping to be a dict");
        return NULL;
    }

    var2ex = BX_Dict_New();
    /* FIXME: check var2ex == NULL */
    while (PyDict_Next(mapping, &pos, &key, &val)) {
        BX_Dict_Insert(var2ex, NODE(key), NODE(val));
    }

    if ((ex = BX_Compose(self->ex, var2ex)) == NULL) {
        BX_Dict_Del(var2ex);
        PyErr_SetString(Error, "BX_Compose failed");
        return NULL;
    }

    BX_Dict_Del(var2ex);

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


/* ExprNode.data() */
static PyObject *
ExprNode_data(ExprNode *self)
{
    if (BX_IS_CONST(self->ex))
        return PyLong_FromLong((long) self->ex->data.pcval);

    if (BX_IS_LIT(self->ex))
        return PyLong_FromLong(self->ex->data.lit.uniqid);

    if (BX_IS_OP(self->ex)) {
        int i, j;
        ExprNode **nodes;
        PyObject *xs;

        nodes = (ExprNode **) PyMem_Malloc(self->ex->data.xs->length * sizeof(ExprNode *));
        if (nodes == NULL)
            return NULL;

        for (i = 0; i < self->ex->data.xs->length; ++i) {
            nodes[i] = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
            if (nodes[i] == NULL) {
                for (j = 0; j < i; ++j)
                    Py_DECREF(nodes[j]);
                PyMem_Free(nodes);
                return NULL;
            }
            nodes[i]->ex = BX_IncRef(self->ex->data.xs->items[i]);
        }

        xs = PyTuple_New(self->ex->data.xs->length);
        if (xs == NULL) {
            for (i = 0; i < self->ex->data.xs->length; ++i)
                Py_DECREF(nodes[i]);
            PyMem_Free(nodes);
            return NULL;
        }

        for (i = 0; i < self->ex->data.xs->length; ++i)
            PyTuple_SET_ITEM(xs, i, (PyObject *) nodes[i]);

        PyMem_Free(nodes);

        return xs;
    }

    Py_RETURN_NONE;
}


/* ExprNode.pushdown_not() */
static PyObject *
ExprNode_pushdown_not(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_PushDownNot(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_PushDownNot failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


/* ExprNode.simplify() */
static PyObject *
ExprNode_simplify(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_Simplify(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_Simplify failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


/* ExprNode.to_binary() */
static PyObject *
ExprNode_to_binary(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_ToBinary(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_ToBinary failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


static PyObject *
ExprNode_to_nnf(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_ToNNF(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_ToNNF failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


static PyObject *
ExprNode_to_dnf(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_ToDNF(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_ToDNF failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


static PyObject *
ExprNode_to_cnf(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_ToCNF(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_ToCNF failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


static PyObject *
ExprNode_complete_sum(ExprNode *self)
{
    struct BoolExpr *ex;

    if ((ex = BX_CompleteSum(self->ex)) == NULL) {
        PyErr_SetString(Error, "BX_CompleteSum failed");
        return NULL;
    }

    if (ex == self->ex) {
        BX_DecRef(ex);
        Py_INCREF((PyObject *) self);
        return (PyObject *) self;
    }

    ExprNode *pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;
    return (PyObject *) pyex;
}


/* exprnode.lit */
PyDoc_STRVAR(lit_doc,
    "\n\
    Return a literal expression node.\n\
\n\
    Parameters\n\
    ----------\n\
    uniqid : nonzero int\n\
        A unique, nonzero integer identifier.\n\
        A positive integer is a variable,\n\
        and a negative integer is the complement of its inverse.\n\
    "
);

static PyObject *
lit(PyObject *self, PyObject *args)
{
    long uniqid;
    struct BoolExpr *ex;
    ExprNode *pyex;

    if (!PyArg_ParseTuple(args, "l", &uniqid))
        return NULL;

    if (uniqid == 0) {
        PyErr_SetString(PyExc_ValueError, "expected uniqid != 0");
        return NULL;
    }

    if ((ex = BX_Literal(lits, uniqid)) == NULL) {
        PyErr_SetString(Error, "BX_Literal failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;

    return (PyObject *) pyex;
}


/* exprnode.not_ */
PyDoc_STRVAR(not_doc,
    "\n\
    Return the inverse of an expression node.\n\
\n\
    For atomic nodes (constants & literals), the inverse is also an atomic node.\n\
    For all other nodes, the inverse will be a NOT operator node.\n\
\n\
    Parameters\n\
    ----------\n\
    x : ExprNode\n\
    "
);

static PyObject *
not_(PyObject *self, PyObject *args)
{
    PyObject *x;
    struct BoolExpr *ex;
    ExprNode *pyex;

    if (!PyArg_ParseTuple(args, "O", &x))
        return NULL;

    if (!PyObject_IsInstance(x, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected x to be an ExprNode");
        return NULL;
    }

    if ((ex = BX_Not(NODE(x))) == NULL) {
        PyErr_SetString(Error, "BX_Not failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;

    return (PyObject *) pyex;
}


static struct BoolExpr **
_parse_args(int n, PyObject *args)
{
    int i;
    PyObject *iter, *item;
    struct BoolExpr **xs;

    xs = (struct BoolExpr **) PyMem_Malloc(n * sizeof(struct BoolExpr *));
    if (xs == NULL)
        return NULL;

    iter = PyObject_GetIter(args);
    if (iter == NULL) {
        PyMem_Free(xs);
        return NULL;
    }

    /* for arg in args */
    for (i = 0; (item = PyIter_Next(iter)); ++i) {
        if (!PyObject_IsInstance(item, (PyObject *) &ExprNode_T)) {
            PyErr_SetString(PyExc_TypeError, "expected x to be an ExprNode");
            PyMem_Free(xs);
            return NULL;
        }
        xs[i] = NODE(item);
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) {
        PyMem_Free(xs);
        return NULL;
    }

    return xs;
}


/* exprnode.or_ */
PyDoc_STRVAR(or_doc,
    "\n\
    Return an OR operator node.\n\
\n\
    Parameters\n\
    ----------\n\
    *xs : tuple(ExprNode)\n\
        The operator arguments\n\
    "
);

static PyObject *
or_(PyObject *self, PyObject *args)
{
    int n = PyTuple_Size(args);
    struct BoolExpr **xs;
    ExprNode *pyex;
    struct BoolExpr *ex;

    xs = _parse_args(n, args);
    if (xs == NULL)
        return NULL;

    if ((ex = BX_Or(n, xs)) == NULL) {
        PyMem_Free(xs);
        PyErr_SetString(Error, "BX_Or failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        PyMem_Free(xs);
        return NULL;
    }
    pyex->ex = ex;

    PyMem_Free(xs);

    return (PyObject *) pyex;
}


/* exprnode.and_ */
PyDoc_STRVAR(and_doc,
    "\n\
    Return an AND operator node.\n\
\n\
    Parameters\n\
    ----------\n\
    *xs : tuple(ExprNode)\n\
        The operator arguments\n\
    "
);

static PyObject *
and_(PyObject *self, PyObject *args)
{
    int n = PyTuple_Size(args);
    struct BoolExpr **xs;
    ExprNode *pyex;
    struct BoolExpr *ex;

    xs = _parse_args(n, args);
    if (xs == NULL)
        return NULL;

    if ((ex = BX_And(n, xs)) == NULL) {
        PyMem_Free(xs);
        PyErr_SetString(Error, "BX_And failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        PyMem_Free(xs);
        return NULL;
    }
    pyex->ex = ex;

    PyMem_Free(xs);

    return (PyObject *) pyex;
}


/* exprnode.xor */
PyDoc_STRVAR(xor_doc,
    "\n\
    Return an XOR operator node.\n\
\n\
    Parameters\n\
    ----------\n\
    *xs : tuple(ExprNode)\n\
        The operator arguments\n\
    "
);

static PyObject *
xor_(PyObject *self, PyObject *args)
{
    int n = PyTuple_Size(args);
    struct BoolExpr **xs;
    ExprNode *pyex;
    struct BoolExpr *ex;

    xs = _parse_args(n, args);
    if (xs == NULL)
        return NULL;

    if ((ex = BX_Xor(n, xs)) == NULL) {
        PyMem_Free(xs);
        PyErr_SetString(Error, "BX_Xor failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        PyMem_Free(xs);
        return NULL;
    }
    pyex->ex = ex;

    PyMem_Free(xs);

    return (PyObject *) pyex;
}


/* exprnode.eq */
PyDoc_STRVAR(eq_doc,
    "\n\
    Return an EQ (equal) operator node.\n\
\n\
    Parameters\n\
    ----------\n\
    *xs : tuple(ExprNode)\n\
        The operator arguments\n\
    "
);

static PyObject *
eq(PyObject *self, PyObject *args)
{
    int n = PyTuple_Size(args);
    struct BoolExpr **xs;
    ExprNode *pyex;
    struct BoolExpr *ex;

    xs = _parse_args(n, args);
    if (xs == NULL)
        return NULL;

    if ((ex = BX_Equal(n, xs)) == NULL) {
        PyMem_Free(xs);
        PyErr_SetString(Error, "BX_Equal failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        PyMem_Free(xs);
        return NULL;
    }
    pyex->ex = ex;

    PyMem_Free(xs);

    return (PyObject *) pyex;
}


/* exprnode.impl */
PyDoc_STRVAR(impl_doc,
    "\n\
    Return an IMPL (implies) operator node, p => q.\n\
\n\
    Parameters\n\
    ----------\n\
    p : ExprNode\n\
        The antecedent\n\
\n\
    q : ExprNode\n\
        The consequence\n\
    "
);

static PyObject *
impl(PyObject *self, PyObject *args)
{
    PyObject *p, *q;
    struct BoolExpr *ex;
    ExprNode *pyex;

    if (!PyArg_ParseTuple(args, "OO", &p, &q))
        return NULL;

    if (!PyObject_IsInstance(p, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected p to be an ExprNode");
        return NULL;
    }
    if (!PyObject_IsInstance(q, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected q to be an ExprNode");
        return NULL;
    }

    if ((ex = BX_Implies(NODE(p), NODE(q))) == NULL) {
        PyErr_SetString(Error, "BX_Implies failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;

    return (PyObject *) pyex;
}


/* exprnode.ite */
PyDoc_STRVAR(ite_doc,
    "\n\
    Return an ITE (if-then-else) operator node, s ? d1 : d0.\n\
\n\
    Parameters\n\
    ----------\n\
    s : ExprNode\n\
        The select\n\
\n\
    d1 : ExprNode\n\
        The output data if select == 1\n\
\n\
    d0 : ExprNode\n\
        The output data if select == 0\n\
    "
);

static PyObject *
ite(PyObject *self, PyObject *args)
{
    PyObject *s, *d1, *d0;
    struct BoolExpr *ex;
    ExprNode *pyex;

    if (!PyArg_ParseTuple(args, "OOO", &s, &d1, &d0))
        return NULL;

    if (!PyObject_IsInstance(s, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected s to be an ExprNode");
        return NULL;
    }

    if (!PyObject_IsInstance(d1, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected d1 to be an ExprNode");
        return NULL;
    }

    if (!PyObject_IsInstance(d0, (PyObject *) &ExprNode_T)) {
        PyErr_SetString(PyExc_TypeError, "expected d0 to be an ExprNode");
        return NULL;
    }

    if ((ex = BX_ITE(NODE(s), NODE(d1), NODE(d0))) == NULL) {
        PyErr_SetString(Error, "BX_ITE failed");
        return NULL;
    }

    pyex = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (pyex == NULL) {
        BX_DecRef(ex);
        return NULL;
    }
    pyex->ex = ex;

    return (PyObject *) pyex;
}


/* exprnode module definition */
PyDoc_STRVAR(m_doc,
"\n\
The :mod:`pyeda.boolalg.exprnode` module is a Python layer to the\n\
`boolexpr` C API.\n\
Logic expressions are implemented as a tree structure.\n\
\n\
Data Types:\n\
\n\
abstract syntax tree\n\
   A nested tuple of entries that represents an expression node.\n\
   It is defined recursively::\n\
\n\
      ast := ('const', bool)\n\
           | ('lit', int)\n\
           | (op, ast, ...)\n\
\n\
      bool := 0 | 1 | 2 | 3\n\
\n\
      op := 'not' | 'or' | 'and' | 'xor' | 'eq' | 'impl' | 'ite'\n\
"
);

static PyMethodDef m_methods[] = {
    {"lit",  (PyCFunction) lit,  METH_VARARGS, lit_doc},
    {"not_", (PyCFunction) not_, METH_VARARGS, not_doc},
    {"or_",  (PyCFunction) or_,  METH_VARARGS, or_doc},
    {"and_", (PyCFunction) and_, METH_VARARGS, and_doc},
    {"xor",  (PyCFunction) xor_, METH_VARARGS, xor_doc},
    {"eq",   (PyCFunction) eq,   METH_VARARGS, eq_doc},
    {"impl", (PyCFunction) impl, METH_VARARGS, impl_doc},
    {"ite",  (PyCFunction) ite,  METH_VARARGS, ite_doc},

    /* sentinel */
    {NULL, NULL, 0, NULL}
};

static PyModuleDef _module = {
    PyModuleDef_HEAD_INIT,

    "exprnode", /* m_name */
    m_doc,      /* m_doc */
    -1,         /* m_size */
    m_methods,  /* m_methods */
};


PyMODINIT_FUNC
PyInit_exprnode(void)
{
    PyObject *m;

    /* Create exprnode */
    m = PyModule_Create(&_module);
    if (m == NULL)
        goto error;

    /* Create exprnode.Error */
    Error = PyErr_NewExceptionWithDoc("exprnode.Error", Error_doc, NULL, NULL);
    if (Error == NULL)
        goto error;
    Py_INCREF(Error);
    if (PyModule_AddObject(m, "Error", Error) < 0)
        goto decref_Error;

    /* Create exprnode.ExprNode */
    if (PyType_Ready(&ExprNode_T) < 0)
        goto decref_Error;
    Py_INCREF((PyObject *) &ExprNode_T);
    if (PyModule_AddObject(m, "ExprNode", (PyObject *) &ExprNode_T) < 0)
        goto decref_ExprNode;

    /* Create constants */
    Zero = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (Zero == NULL)
        goto decref_ExprNode;
    Zero->ex = BX_IncRef(&BX_Zero);
    if (PyModule_AddObject(m, "Zero", (PyObject *) Zero) < 0)
        goto decref_Zero;

    /* Create exprnode.One */
    One = (ExprNode *) PyObject_CallObject((PyObject *) &ExprNode_T, NULL);
    if (One == NULL)
        goto decref_Zero;
    One->ex = BX_IncRef(&BX_One);
    if (PyModule_AddObject(m, "One", (PyObject *) One) < 0)
        goto decref_One;

    /* Create module-level literal vector */
    lits = BX_Vector_New();
    if (lits == NULL)
        goto decref_One;

    /* Create constants */
    if (PyModule_AddIntConstant(m, "ZERO", BX_ZERO))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "ONE", BX_ONE))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "COMP", BX_COMP))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "VAR", BX_VAR))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_OR", BX_OP_OR))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_AND", BX_OP_AND))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_XOR", BX_OP_XOR))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_EQ", BX_OP_EQ))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_NOT", BX_OP_NOT))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_IMPL", BX_OP_IMPL))
        goto undo_all;
    if (PyModule_AddIntConstant(m, "OP_ITE", BX_OP_ITE))
        goto undo_all;

    /* Success! */
    return m;

/* Error! */
undo_all:

    BX_Vector_Del(lits);

decref_One:
    Py_DECREF(One);
decref_Zero:
    Py_DECREF(Zero);
decref_ExprNode:
    Py_DECREF((PyObject *) &ExprNode_T);
decref_Error:
    Py_DECREF(Error);

error:
    return NULL;
}

