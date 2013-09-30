// Filename: _picosat.c
//
// Python Interface Functions:
//     solve
//     iter_solve

#include <Python.h>
#include <math.h>
#include "picosat.h"

static PyObject *PicosatError;

PyObject * version(void) {
    return PyUnicode_FromString("957");
}

PyObject * copyright(void) {
    return PyUnicode_FromString(picosat_copyright());
}

inline static void *
py_malloc(void *pmgr, size_t nbytes) {
    return PyMem_Malloc(nbytes);
}

inline static void *
py_realloc(void *pmgr, void *p, size_t old, size_t new) {
    return PyMem_Realloc(p, new);
}

inline static void
py_free(void *pmgr, void *p, size_t nbytes) {
    PyMem_Free(p);
}

//==============================================================================
// Add all clause literals to a PicoSAT instance.
//
// Returns:
//     0 : Exception
//     1 : Success
//==============================================================================

static int
add_clauses(PicoSAT *picosat, PyObject *clauses) {

    int nvars = picosat_variables(picosat);
    PyObject *pyclauses, *pyclause;
    PyObject *pylits, *pylit;
    int lit;

    int ret = 0;

    pyclauses = PyObject_GetIter(clauses);
    if (pyclauses == NULL) {
        goto ADD_LITS_RETURN;
    }
    while ((pyclause = PyIter_Next(pyclauses)) != 0) {
        pylits = PyObject_GetIter(pyclause);
        if (pylits == NULL) {
            goto ADD_LITS_DECREF_PYCLAUSES;
        }
        while ((pylit = PyIter_Next(pylits)) != 0) {
            if (!PyLong_Check(pylit)) {
                PyErr_SetString(PyExc_TypeError, "expected integer clause literal");
                goto ADD_LITS_DECREF_PYLITS;
            }
            lit = PyLong_AsLong(pylit);
            if (lit == 0 || abs(lit) > nvars) {
                PyErr_Format(PyExc_ValueError, "expected clause literal in range (0, %d], got: %d", nvars, lit);
                goto ADD_LITS_DECREF_PYLITS;
            }

            // Add clause literal
            picosat_add(picosat, lit);

            Py_DECREF(pylit);
        } // for pylit in pylits
        Py_DECREF(pylits);

        if (PyErr_Occurred()) {
            goto ADD_LITS_DECREF_PYCLAUSES;
        }

        // Terminate clause
        picosat_add(picosat, 0);

        Py_DECREF(pyclause);
    } // for pyclause in pyclauses
    Py_DECREF(pyclauses);

    if (PyErr_Occurred()) {
        goto ADD_LITS_RETURN;
    }

    // Success!
    ret = 1;
    goto ADD_LITS_RETURN;

ADD_LITS_DECREF_PYLITS:
    Py_DECREF(pylit);
    Py_DECREF(pylits);

ADD_LITS_DECREF_PYCLAUSES:
    Py_DECREF(pyclause);
    Py_DECREF(pyclauses);

ADD_LITS_RETURN:
    return ret;
}

//==============================================================================
// Retrieve a solution from PicoSAT, and convert it to a Python tuple.
// Return NULL if an error happens.
//
// The tuple items map to Boolean values as follows:
//     -1 : 0
//      0 : unknown
//      1 : 1
//==============================================================================

static PyObject *
get_solution(PicoSAT * picosat) {

    int i;
    int nvars = picosat_variables(picosat);
    PyObject *pytuple, *pyitem;
    int lit;

    pytuple = PyTuple_New(nvars);
    if (pytuple == NULL) {
        return NULL;
    }
    for (i = 1; i <= nvars; i++) {
        lit = picosat_deref(picosat, i);
        pyitem = PyLong_FromLong(lit);
        if (pyitem == NULL) {
            Py_DECREF(pytuple);
            return NULL;
        }
        if (PyTuple_SetItem(pytuple, i - 1, pyitem) < 0) {
            Py_DECREF(pyitem);
            Py_DECREF(pytuple);
            return NULL;
        }
    }
    return pytuple;
}

//==============================================================================
// Return a single solution to a CNF instance.
//
// solve(nvars : int, clauses : iter(iter(int)),
//       verbosity=0, default_phase=2, propagation_limit=-1, decision_limit=-1)
//==============================================================================

PyDoc_STRVAR(solve_docstring, "Return the result of a PicoSAT solver.\n\
\n\
If the CNF is satisfiable, return a satisfying input point.\n\
If the CNF is NOT satisfiable, return None.\n\
If PicoSAT encounters an error, raise a PicosatError.");

static PyObject *
solve(PyObject *self, PyObject *args, PyObject *kwargs) {

    static char *keywords[] = {
        "nvars", "clauses",
        "verbosity", "default_phase", "propagation_limit", "decision_limit",
        NULL
    };

    // PicoSAT instance
    PicoSAT *picosat;

    // PicoSAT input parameters
    int nvars = 0;
    PyObject *clauses;
    int verbosity = 0;
    int default_phase = 2; // 0 = false, 1 = true, 2 = Jeroslow-Wang, 3 = random
    int propagation_limit = -1;
    int decision_limit = -1;

    // PicoSAT return value
    int result;

    // Python return value
    PyObject *pyret = NULL;

    picosat = picosat_minit(NULL, py_malloc, py_realloc, py_free);
    if (picosat == NULL) {
        PyErr_SetString(PicosatError, "could not initialize PicoSAT");
        goto SOLVE_RETURN;
    }

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iO|iiii:solve", keywords,
            &nvars, &clauses,
            &verbosity, &default_phase, &propagation_limit, &decision_limit)) {
        goto SOLVE_RESET_PICOSAT;
    }

    picosat_set_verbosity(picosat, verbosity);
    picosat_set_global_default_phase(picosat, default_phase);
    picosat_set_propagation_limit(picosat, propagation_limit);

    picosat_adjust(picosat, nvars);

    if (!add_clauses(picosat, clauses)) {
        goto SOLVE_RESET_PICOSAT;
    }

    // picosat_assume(picosat, lit);
    // picosat_set_seed(picosat, seed);

    // Do the damn thing
    Py_BEGIN_ALLOW_THREADS
    result = picosat_sat(picosat, decision_limit);
    Py_END_ALLOW_THREADS

    // Prepare Python return value
    if (result == PICOSAT_UNSATISFIABLE) {
        Py_INCREF(Py_None);
        pyret = Py_None;
    }
    else if (result == PICOSAT_SATISFIABLE) {
        // Might be NULL
        pyret = get_solution(picosat);
    }
    else if (result == PICOSAT_UNKNOWN) {
        PyErr_SetString(PicosatError, "PicoSAT returned UNKNOWN");
    }
    else {
        PyErr_Format(PicosatError, "PicoSAT returned: %d", result);
    }

SOLVE_RESET_PICOSAT:
    picosat_reset(picosat);

SOLVE_RETURN:
    return pyret;
}

//==============================================================================
// Module Definition
//==============================================================================

static PyMethodDef methods[] = {
    {"solve", (PyCFunction) solve, METH_VARARGS | METH_KEYWORDS, solve_docstring},

    // sentinel
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_docstring, "Python bindings to PicoSAT");

static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,

    // module name
    "_picosat",

    module_docstring,

    // FIXME: I have not idea what this is for
    -1,

    // module methods
    methods,
};

PyDoc_STRVAR(picosaterr_docstring, "PicoSAT Error");

PyMODINIT_FUNC PyInit__picosat(void)
{
    PyObject *pymodule;

    pymodule = PyModule_Create(&module);
    if (pymodule == NULL)
        return NULL;

    PyModule_AddObject(pymodule, "PICOSAT_VERSION", version());
    PyModule_AddObject(pymodule, "PICOSAT_COPYRIGHT", copyright());

    PicosatError = PyErr_NewExceptionWithDoc("_picosat.PicosatError", picosaterr_docstring, NULL, NULL);
    Py_INCREF(PicosatError);
    PyModule_AddObject(pymodule, "PicosatError", PicosatError);

    return pymodule;
}
