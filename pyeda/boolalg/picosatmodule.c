/*
** Filename: picosatmodule.c
**
** Interface to PicoSAT SAT solver C extension
**
** Constants:
**     PICOSAT_VERSION
**     PICOSAT_COPYRIGHT
**
** Exceptions:
**     PicosatError
**
** Interface Functions:
**     satisfy_one
**     satisfy_all
*/

#include <Python.h>
#include <math.h>

#include "picosat.h"

/*
** Python exception definition: picosat.PicosatError
*/
PyDoc_STRVAR(_picosat_error_docstring, "PicoSAT Error");

static PyObject *_picosat_error;

/* Pass these functions to picosat_minit to use Python's memory manager. */
inline static void *
_pymalloc(void *pmgr, size_t nbytes)
{
    return PyMem_Malloc(nbytes);
}

inline static void *
_pyrealloc(void *pmgr, void *p, size_t old, size_t new)
{
    return PyMem_Realloc(p, new);
}

inline static void
_pyfree(void *pmgr, void *p, size_t nbytes)
{
    PyMem_Free(p);
}

/*
** Add all clause literals to a PicoSAT instance.
**
** Returns
** -------
**     0 : Exception
**     1 : Success
*/
static int
_add_clauses(PicoSAT *picosat, PyObject *clauses)
{
    int nvars;
    PyObject *pyclauses, *pyclause;
    PyObject *pylits, *pylit;
    int lit;

    nvars = picosat_variables(picosat);

    pyclauses = PyObject_GetIter(clauses);
    if (pyclauses == NULL)
        goto error;

    while ((pyclause = PyIter_Next(pyclauses)) != 0) {
        pylits = PyObject_GetIter(pyclause);
        if (pylits == NULL)
            goto decref_pyclauses;

        while ((pylit = PyIter_Next(pylits)) != 0) {
            if (!PyLong_Check(pylit)) {
                PyErr_SetString(PyExc_TypeError, "expected clause literal to be an int");
                goto decref_pylits;
            }
            lit = PyLong_AsLong(pylit);
            if (lit == 0 || abs(lit) > nvars) {
                PyErr_Format(
                    PyExc_ValueError,
                    "expected clause literal in range [-%d, 0), (0, %d], got: %d",
                    nvars, nvars, lit
                );
                goto decref_pylits;
            }

            /* Add clause literal */
            picosat_add(picosat, lit);

            Py_DECREF(pylit);
        } /* for pylit in pylits */
        Py_DECREF(pylits);

        if (PyErr_Occurred())
            goto decref_pyclauses;

        /* Terminate clause */
        picosat_add(picosat, 0);

        Py_DECREF(pyclause);
    } /* for pyclause in pyclauses */
    Py_DECREF(pyclauses);

    if (PyErr_Occurred())
        goto error;

    /* Success! */
    return 1;

decref_pylits:
    Py_DECREF(pylit);
    Py_DECREF(pylits);

decref_pyclauses:
    Py_DECREF(pyclause);
    Py_DECREF(pyclauses);

error:
    return 0;
}

/*
** Add all assumptions to a PicoSAT instance.
**
** Returns:
**     0 : Exception
**     1 : Success
*/
static int
_add_assumptions(PicoSAT *picosat, PyObject *assumptions)
{
    int nvars;
    PyObject *pylits, *pylit;
    int lit;

    nvars = picosat_variables(picosat);

    pylits = PyObject_GetIter(assumptions);
    if (pylits == NULL)
        goto error;

    while ((pylit = PyIter_Next(pylits)) != 0) {
        if (!PyLong_Check(pylit)) {
            PyErr_SetString(PyExc_TypeError, "expected assumption literal to be an int");
            goto decref_pylits;
        }
        lit = PyLong_AsLong(pylit);
        if (lit == 0 || abs(lit) > nvars) {
            PyErr_Format(
                PyExc_ValueError,
                "expected assumption literal in range [-%d, 0), (0, %d], got: %d",
                nvars, nvars, lit
            );
            goto decref_pylits;
        }

        /* Add assumption literal */
        picosat_assume(picosat, lit);

        Py_DECREF(pylit);
    } /* for pylit in pylits */
    Py_DECREF(pylits);

    if (PyErr_Occurred())
        goto error;

    /* Success! */
    return 1;

decref_pylits:
    Py_DECREF(pylit);
    Py_DECREF(pylits);

error:
    return 0;
}

/*
** Retrieve a solution from PicoSAT, and convert it to a Python tuple.
** Return NULL if an error happens.
**
** The tuple items map to Boolean values as follows:
**     -1 : 0
**      0 : unknown
**      1 : 1
*/
static PyObject *
_get_soln(PicoSAT *picosat)
{
    int i;
    int nvars;
    PyObject *pytuple, *pylong;

    nvars = picosat_variables(picosat);

    pytuple = PyTuple_New(nvars);
    if (pytuple == NULL)
        goto error;

    for (i = 1; i <= nvars; i++) {
        pylong = PyLong_FromLong((long) picosat_deref(picosat, i));
        if (pylong == NULL)
            goto decref_pytuple;
        if (PyTuple_SetItem(pytuple, i - 1, pylong) < 0)
            goto decref_pylong;
    }

    /* Success! */
    return pytuple;

decref_pylong:
    Py_DECREF(pylong);

decref_pytuple:
    Py_DECREF(pytuple);

error:
    return NULL;
}

/*
** Add the inverse of the current solution to the clauses.
** Prevents repetition when finding all solutions.
**
** NOTE: Copied from PicoSAT "app.c".
*/
static int
_block_soln(PicoSAT *picosat, signed char *soln)
{
    int i;
    int nvars;

    nvars = picosat_variables(picosat);

    for (i = 1; i <= nvars; i++)
        soln[i] = (picosat_deref(picosat, i) > 0) ? 1 : -1;

    for (i = 1; i <= nvars; i++)
        picosat_add(picosat, (soln[i] < 0) ? i : -i);

    picosat_add(picosat, 0);

    return 1;
}

/*
** Python function definition: picosat.satisfy_one()
*/
PyDoc_STRVAR(_satisfy_one_docstring,
    "\n\
    If the input CNF is satisfiable, return a satisfying input point.\n\
    A contradiction will return None.\n\
\n\
    Parameters\n\
    ----------\n\
    nvars : posint\n\
        Number of variables in the CNF\n\
\n\
    clauses : iter of iter of (nonzero) int\n\
        The CNF clauses\n\
\n\
    verbosity : int, optional\n\
        Set verbosity level. A verbosity level of 1 and above prints more and\n\
        more detailed progress reports to stdout.\n\
\n\
    default_phase : {0, 1, 2, 3}\n\
        Set default initial phase:\n\
            0 = false\n\
            1 = true\n\
            2 = Jeroslow-Wang (default)\n\
            3 = random\n\
\n\
    progagation_limit : int\n\
        Set a limit on the number of propagations. A negative value sets no\n\
        propagation limit.\n\
\n\
    decision_limit : int\n\
        Set a limit on the number of decisions. A negative value sets no\n\
        decision limit.\n\
\n\
    assumptions : iter of (nonzero) int\n\
        Add assumptions (unit clauses) to the CNF\n\
\n\
    Returns\n\
    -------\n\
    tuple of {-1, 0, 1}\n\
        -1 : zero\n\
         0 : dont-care\n\
         1 : one\n\
    "
);

static PyObject *
_satisfy_one(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "nvars", "clauses",
        "verbosity", "default_phase", "propagation_limit", "decision_limit",
        "assumptions",
        NULL
    };

    /* PicoSAT instance */
    PicoSAT *picosat;

    /* PicoSAT input parameters */
    int nvars = 0;
    PyObject *clauses;
    int verbosity = 0;
    int default_phase = 2; /* Jeroslow-Wang */
    int propagation_limit = -1;
    int decision_limit = -1;
    PyObject *assumptions = NULL;

    /* PicoSAT return value */
    int result;

    /* Python return value */
    PyObject *pyret = NULL;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iO|iiiiO:satisfy_one", keywords,
            &nvars, &clauses,
            &verbosity, &default_phase, &propagation_limit, &decision_limit,
            &assumptions))
        goto done;

    if (nvars < 0) {
        PyErr_Format(PyExc_ValueError, "expected nvars >= 0, got: %d", nvars);
        goto done;
    }
    if (default_phase < 0 || default_phase > 3) {
        PyErr_Format(PyExc_ValueError, "expected default_phase in {0, 1, 2, 3}, got: %d", default_phase);
        goto done;
    }

    picosat = picosat_minit(NULL, _pymalloc, _pyrealloc, _pyfree);
    if (picosat == NULL) {
        PyErr_SetString(_picosat_error, "could not initialize PicoSAT");
        goto done;
    }

    picosat_set_verbosity(picosat, verbosity);
    picosat_set_global_default_phase(picosat, default_phase);
    picosat_set_propagation_limit(picosat, propagation_limit);

    picosat_adjust(picosat, nvars);

    if (!_add_clauses(picosat, clauses))
        goto reset_picosat;

    if (assumptions != NULL && assumptions != Py_None) {
        if (!_add_assumptions(picosat, assumptions))
            goto reset_picosat;
    }

    /* picosat_set_seed(picosat, seed); */

    /* Do the damn thing */
    Py_BEGIN_ALLOW_THREADS
    result = picosat_sat(picosat, decision_limit);
    Py_END_ALLOW_THREADS

    /* Prepare Python return value */
    if (result == PICOSAT_UNSATISFIABLE) {
        Py_RETURN_NONE;
    }
    else if (result == PICOSAT_SATISFIABLE) {
        /* Might be NULL */
        pyret = _get_soln(picosat);
    }
    else if (result == PICOSAT_UNKNOWN) {
        PyErr_SetString(_picosat_error, "PicoSAT returned UNKNOWN");
    }
    else {
        PyErr_Format(_picosat_error, "PicoSAT returned: %d", result);
    }

reset_picosat:
    picosat_reset(picosat);

done:
    return pyret;
}

/*
** Python iterator definition: picosat.satisfy_all()
*/
PyDoc_STRVAR(_satisfy_all_docstring,
    "\n\
    Iterate through all satisfying input points.\n\
\n\
    Parameters\n\
    ----------\n\
    nvars : posint\n\
        Number of variables in the CNF\n\
\n\
    clauses : iter of iter of (nonzero) int\n\
        The CNF clauses\n\
\n\
    verbosity : int, optional\n\
        Set verbosity level. A verbosity level of 1 and above prints more and\n\
        more detailed progress reports to stdout.\n\
\n\
    default_phase : {0, 1, 2, 3}\n\
        Set default initial phase:\n\
            0 = false\n\
            1 = true\n\
            2 = Jeroslow-Wang (default)\n\
            3 = random\n\
\n\
    progagation_limit : int\n\
        Set a limit on the number of propagations. A negative value sets no\n\
        propagation limit.\n\
\n\
    decision_limit : int\n\
        Set a limit on the number of decisions. A negative value sets no\n\
        decision limit.\n\
\n\
    Returns\n\
    -------\n\
    iter of tuple of {-1, 0, 1}\n\
        -1 : zero\n\
         0 : dont-care\n\
         1 : one\n\
    "
);

/* satisfy_all state */
typedef struct {
    PyObject_HEAD

    PicoSAT *picosat;
    int decision_limit;
    signed char *soln;
} _satisfy_all_state;

/* satisfy_all.tp_new */
static PyObject *
_satisfy_all_new(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "nvars", "clauses",
        "verbosity", "default_phase", "propagation_limit", "decision_limit",
        NULL
    };

    /* PicoSAT instance */
    PicoSAT *picosat;

    /* PicoSAT input parameters */
    int nvars = 0;
    PyObject *clauses;
    int verbosity = 0;
    int default_phase = 2; /* Jeroslow-Wang */
    int propagation_limit = -1;
    int decision_limit = -1;

    /* Python return value */
    _satisfy_all_state *state;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iO|iiii:satisfy_all", keywords,
            &nvars, &clauses,
            &verbosity, &default_phase, &propagation_limit, &decision_limit))
        goto error;

    if (nvars < 0) {
        PyErr_Format(PyExc_ValueError, "expected nvars >= 0, got: %d", nvars);
        goto error;
    }
    if (default_phase < 0 || default_phase > 3) {
        PyErr_Format(PyExc_ValueError, "expected default_phase in {0, 1, 2, 3}, got: %d", default_phase);
        goto error;
    }

    picosat = picosat_minit(NULL, _pymalloc, _pyrealloc, _pyfree);
    if (picosat == NULL) {
        PyErr_SetString(_picosat_error, "could not initialize PicoSAT");
        goto error;
    }

    picosat_set_verbosity(picosat, verbosity);
    picosat_set_global_default_phase(picosat, default_phase);
    picosat_set_propagation_limit(picosat, propagation_limit);

    picosat_adjust(picosat, nvars);

    if (!_add_clauses(picosat, clauses))
        goto reset_picosat;

    /* picosat_set_seed(picosat, seed); */

    /* Initialize iterator state */
    state = (_satisfy_all_state *) cls->tp_alloc(cls, 0);
    if (state == NULL)
        goto reset_picosat;

    state->picosat = picosat;
    state->decision_limit = decision_limit;
    state->soln = PyMem_Malloc(nvars + 1);
    if (state->soln == NULL) {
        PyErr_NoMemory();
        goto reset_picosat;
    }

    /* Success! */
    return (PyObject *) state;

reset_picosat:
    picosat_reset(picosat);

error:
    return NULL;
}

/* satisfy_all.tp_dealloc */
static void
_satisfy_all_dealloc(_satisfy_all_state *state)
{
    PyMem_Free(state->soln);
    Py_TYPE(state)->tp_free(state);

    picosat_reset(state->picosat);
}

/* satisfy_all.tp_iternext */
static PyObject *
_satisfy_all_next(_satisfy_all_state *state)
{
    PyObject *pysoln;

    /* PicoSAT return value */
    int result;

    /* Python return value */
    PyObject *pyret = NULL;

    /* Do the damn thing */
    Py_BEGIN_ALLOW_THREADS
    result = picosat_sat(state->picosat, state->decision_limit);
    Py_END_ALLOW_THREADS

    /* Prepare Python return value */
    if (result == PICOSAT_UNSATISFIABLE) {
        /* No solution */
    }
    else if (result == PICOSAT_SATISFIABLE) {
        /* Might be NULL */
        pysoln = _get_soln(state->picosat);
        if (pysoln != NULL) {
            _block_soln(state->picosat, state->soln);
            pyret = pysoln;
        }
    }
    else if (result == PICOSAT_UNKNOWN) {
        /* No more solutions */
    }
    else {
        PyErr_Format(_picosat_error, "PicoSAT returned: %d", result);
    }

    return pyret;
}

/* satisfy_all.__class__ */
static PyTypeObject
_satisfy_all_type = {
    PyVarObject_HEAD_INIT(NULL, 0)

    "satisfy_all",                      /* tp_name */
    sizeof(_satisfy_all_state),         /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor) _satisfy_all_dealloc,  /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_reserved */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    _satisfy_all_docstring,             /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    PyObject_SelfIter,                  /* tp_iter */
    (iternextfunc) _satisfy_all_next,   /* tp_iternext */
    0,                                  /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    PyType_GenericAlloc,                /* tp_alloc */
    (newfunc) _satisfy_all_new,         /* tp_new */
};

/*
** Python module definition: picosat
*/
PyDoc_STRVAR(_module_docstring,
"\n\
Interface to PicoSAT SAT solver C extension\n\
\n\
Constants:\n\
    PICOSAT_VERSION\n\
    PICOSAT_COPYRIGHT\n\
\n\
Exceptions:\n\
    PicosatError\n\
\n\
Interface Functions:\n\
    satisfy_one\n\
    satisfy_all\n\
"
);

static PyMethodDef _module_methods[] = {
    {"satisfy_one", (PyCFunction) _satisfy_one, METH_VARARGS | METH_KEYWORDS, _satisfy_one_docstring},

    /* sentinel */
    {NULL, NULL, 0, NULL}
};

static PyModuleDef _module = {
    PyModuleDef_HEAD_INIT,

    "picosat",          /* m_name */
    _module_docstring,  /* m_doc */
    -1,                 /* m_size */
    _module_methods,    /* m_methods */
};

PyMODINIT_FUNC
PyInit_picosat(void)
{
    PyObject *pymodule;

    /* Create module */
    pymodule = PyModule_Create(&_module);
    if (pymodule == NULL)
        goto error;

    /* Create constants */
    if (PyModule_AddStringConstant(pymodule, "PICOSAT_VERSION", "957") < 0)
        goto error;

    if (PyModule_AddStringConstant(pymodule, "PICOSAT_COPYRIGHT", picosat_copyright()) < 0)
        goto error;

    /* Create PicosatError */
    _picosat_error = PyErr_NewExceptionWithDoc("picosat.PicosatError",
                                               _picosat_error_docstring,
                                               NULL, NULL);
    if (_picosat_error == NULL)
        goto error;

    Py_INCREF(_picosat_error);
    if (PyModule_AddObject(pymodule, "PicosatError", _picosat_error) < 0) {
        Py_DECREF(_picosat_error);
        goto error;
    }

    /* Create satisfy_all */
    if (PyType_Ready(&_satisfy_all_type) < 0)
        goto error;

    Py_INCREF((PyObject *) &_satisfy_all_type);
    if (PyModule_AddObject(pymodule, "satisfy_all", (PyObject *) &_satisfy_all_type) < 0) {
        Py_DECREF((PyObject *) &_satisfy_all_type);
        goto error;
    }

    /* Success! */
    return pymodule;

error:
    return NULL;
}

