/*
** Filename: espressomodule.c
**
** Interface to Espresso logic minimization engine
**
** Constants:
**
** Exceptions:
**     EspressoError
**
** Interface Functions:
**     espresso
*/

/* FIXME: Add better error handling */

#include <Python.h>

#include "espresso.h"

/*
** Python exception definition: espresso.EspressoError
*/
PyDoc_STRVAR(_espresso_error_docstring, "Espresso Error");

static PyObject *_espresso_error;

/*
**
*/
static PyObject *
_get_soln(set_family_t *F, int num_inputs, int num_outputs)
{
    int i;

    PyObject *pyret;
    PyObject *pylong, *pyins, *pyouts, *pyimpl;

    set *last, *p;

    pyret = PySet_New(0);

    foreach_set(F, last, p) {
        pyins = PyTuple_New(num_inputs);
        pyouts = PyTuple_New(num_outputs);
        pyimpl = PyTuple_New(2);

        for (i = 0; i < num_inputs; i++) {
            pylong = PyLong_FromLong((long) GETINPUT(p, i));
            PyTuple_SetItem(pyins, i, pylong);
        }

        for (i = 0; i < num_outputs; i++) {
            pylong = PyLong_FromLong((long) GETOUTPUT(p, i));
            PyTuple_SetItem(pyouts, i, pylong);
        }

        PyTuple_SetItem(pyimpl, 0, pyins);
        PyTuple_SetItem(pyimpl, 1, pyouts);

        PySet_Add(pyret, pyimpl);
    }

    return pyret;
}

/*
** Python function definition: espresso.espresso()
*/
PyDoc_STRVAR(_espresso_docstring,
    "\n\
\n\
\n\
    "
);

static PyObject *
_espresso(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "num_inputs", "num_outputs", "implicants", "intype",
        NULL
    };

    int i, j;
    int index;
    int val, maxval;
    int err;

    int num_inputs, num_outputs;
    PyObject *implicants;
    int intype = F_type | D_type;

    PyObject *pyrows, *pyrow, *pyins, *pyouts, *pyitem;

    /* Python return value */
    PyObject *pyret = NULL;

    set *cf, *cd, *cr;
    set_family_t *F, *Fsave;
    set_family_t *D;
    set_family_t *R;
    int savef, saved, saver;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iiO|i:espresso", keywords,
            &num_inputs, &num_outputs, &implicants, &intype))
        goto error;

    if (num_inputs <= 0) {
        PyErr_Format(PyExc_ValueError, "expected num_inputs > 0, got: %d", num_inputs);
        goto error;
    }
    if (num_outputs <= 0) {
        PyErr_Format(PyExc_ValueError, "expected num_outputs > 0, got: %d", num_outputs);
        goto error;
    }

    /* Initialize global CUBE dimensions */
    CUBE.num_binary_vars = num_inputs;
    CUBE.num_vars = num_inputs + 1;
    CUBE.part_size = (int *) malloc(CUBE.num_vars * sizeof(int));
    CUBE.part_size[CUBE.num_vars-1] = num_outputs;
    cube_setup();

    /* Initialize F^on, F^dc, F^off */
    F = sf_new(10, CUBE.size);
    D = sf_new(10, CUBE.size);
    R = sf_new(10, CUBE.size);

    /* Read cubes */
    cf = CUBE.temp[0];
    cd = CUBE.temp[1];
    cr = CUBE.temp[2];

    pyrows = PyObject_GetIter(implicants);
    if (pyrows == NULL)
        goto free_espresso;

    while ((pyrow = PyIter_Next(pyrows)) != 0) {
        val = PySequence_Length(pyrow);
        if (val != 2) {
            PyErr_Format(PyExc_ValueError, "expected row vector with length 2, got %d", val);
            goto decref_pyrows;
        }
        pyins = PySequence_GetItem(pyrow, 0);
        val = PySequence_Length(pyins);
        if (val != num_inputs) {
            PyErr_Format(PyExc_ValueError, "expected %d inputs, got %d", num_inputs, val);
            Py_DECREF(pyins);
            goto decref_pyrows;
        }
        set_clear(cf, CUBE.size);
        index = 0;
        for (i = 0; i < num_inputs; i++) {
            pyitem = PySequence_GetItem(pyins, i);
            if (!PyLong_Check(pyitem)) {
                PyErr_SetString(PyExc_TypeError, "expected input to be an int");
                Py_DECREF(pyins);
                goto decref_pyitem;
            }

            val = PyLong_AsLong(pyitem);
            maxval = (1 << CUBE.part_size[i]) - 1;
            if (val < 0 || val > maxval) {
                PyErr_Format(PyExc_ValueError, "expected input in range [0, %d], got: %d", maxval, val);
                Py_DECREF(pyins);
                goto decref_pyitem;
            }

            for (j = 0; j < CUBE.part_size[i]; j++, index++) {
                if (val & (1 << j))
                    set_insert(cf, index);
            }

            Py_DECREF(pyitem);
        } /* for (i = 0; i < num_inputs; i++) */
        Py_DECREF(pyins);

        set_copy(cd, cf);
        set_copy(cr, cf);

        pyouts = PySequence_GetItem(pyrow, 1);
        val = PySequence_Length(pyouts);
        if (val != num_outputs) {
            PyErr_Format(PyExc_ValueError, "expected %d outputs, got %d", num_outputs, val);
            goto decref_pyrows;
        }

        savef = saved = saver = 0;
        for (i = 0; i < num_outputs; i++, index++) {
            pyitem = PySequence_GetItem(pyouts, i);
            if (!PyLong_Check(pyitem)) {
                PyErr_SetString(PyExc_TypeError, "expected output to be an int");
                Py_DECREF(pyouts);
                goto decref_pyitem;
            }
            val = PyLong_AsLong(pyitem);
            switch (val) {
            /* on */
            case 1:
                if (intype & F_type) {
                    set_insert(cf, index);
                    savef = 1;
                }
                break;
            /* don't care */
            case 2:
                if (intype & D_type) {
                    set_insert(cd, index);
                    saved = 1;
                }
                break;
            /* off */
            case 0:
                if (intype & R_type) {
                    set_insert(cr, index);
                    saver = 1;
                }
                break;
            default:
                PyErr_Format(PyExc_ValueError, "expected output in {0, 1, 2}, got %d", val);
                Py_DECREF(pyouts);
                goto decref_pyitem;
            }

            Py_DECREF(pyitem);
        } /* for (i = 0; i < num_outputs; i++) */
        Py_DECREF(pyouts);

        if (savef) F = sf_addset(F, cf);
        if (saved) D = sf_addset(D, cd);
        if (saver) R = sf_addset(R, cr);

        Py_DECREF(pyrow);
    } /* for pyrow in pyrows */
    Py_DECREF(pyrows);

    if (intype == F_type || intype == FD_type) {
        sf_free(R);
        R = complement(cube2list(F, D));
    }
    else if (intype == FR_type) {
        sf_free(D);
        D = complement(cube2list(F, R));
    }
    else if (intype == R_type || intype == DR_type) {
        sf_free(F);
        F = complement(cube2list(D, R));
    }

    Fsave = sf_save(F);
    F = espresso(F, D, R);
    err = verify(F, Fsave, D);
    if (err) {
        PyErr_SetString(_espresso_error, "Espresso result verify failed");
        sf_free(Fsave);
        goto free_espresso;
    }
    sf_free(Fsave);

    /* Prepare return value */
    pyret = _get_soln(F, num_inputs, num_outputs);

    return pyret;

decref_pyitem:
    Py_DECREF(pyitem);

decref_pyrows:
    Py_DECREF(pyrow);
    Py_DECREF(pyrows);

free_espresso:
    sf_free(F);
    sf_free(D);
    sf_free(R);
    sf_cleanup();
    sm_cleanup();
    cube_setdown();
    free(CUBE.part_size);

error:
    return NULL;
}

/*
** Python module definition: espresso
*/

PyDoc_STRVAR(_module_docstring,
"\n\
Interface to Espresso logic minimization engine\n\
\n\
Exceptions:\n\
    EspressoError\n\
\n\
Interface Functions:\n\
    espresso\n\
"
);

static PyMethodDef _module_methods[] = {
    {"espresso", (PyCFunction) _espresso, METH_VARARGS | METH_KEYWORDS, _espresso_docstring},

    /* sentinel */
    {NULL, NULL, 0, NULL}
};

static PyModuleDef _module = {
    PyModuleDef_HEAD_INIT,

    "espresso",         /* m_name */
    _module_docstring,  /* m_doc */
    -1,                 /* m_size */
    _module_methods,    /* m_methods */
};

PyMODINIT_FUNC
PyInit_espresso(void)
{
    PyObject *pymodule;

    /* Create module */
    pymodule = PyModule_Create(&_module);
    if (pymodule == NULL)
        goto error;

    /* Create constants */
    if (PyModule_AddIntConstant(pymodule, "FTYPE", F_type))
        goto error;
    if (PyModule_AddIntConstant(pymodule, "DTYPE", D_type))
        goto error;
    if (PyModule_AddIntConstant(pymodule, "RTYPE", R_type))
        goto error;

    /* Create EspressoError */
    _espresso_error = PyErr_NewExceptionWithDoc("espresso.EspressoError",
                                                _espresso_error_docstring,
                                                NULL, NULL);
    if (_espresso_error == NULL)
        goto error;

    Py_INCREF(_espresso_error);
    if (PyModule_AddObject(pymodule, "EspressoError", _espresso_error) < 0) {
        Py_DECREF(_espresso_error);
        goto error;
    }

    /* Success! */
    return pymodule;

error:
    return NULL;
}

