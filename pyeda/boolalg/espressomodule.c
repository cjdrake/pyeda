/*
** Filename: espressomodule.c
**
** Interface to Espresso logic minimization engine
**
** Constants:
**     FTYPE
**     DTYPE
**     RTYPE
**
** Exceptions:
**     EspressoError
**
** Interface Functions:
**     espresso
*/

#include <Python.h>

#include "espresso.h"

/*
** Python exception definition: espresso.EspressoError
*/
PyDoc_STRVAR(_espresso_error_docstring, "Espresso Error");

static PyObject *_espresso_error;

/*
** Convert a Python set(((int), (int))) to an Espresso cover
*/

static int
_pycov2esprcov(
    set_family_t *F, set_family_t *D, set_family_t *R,
    int ninputs, int noutputs, PyObject *cover, int intype)
{
    int i, j;
    int index;
    int val, maxval;
    int savef, saved, saver;

    set *cf, *cd, *cr;

    PyObject *pyrows, *pyrow, *pyins, *pyouts, *pylong;

    /* Read cubes */
    cf = CUBE.temp[0];
    cd = CUBE.temp[1];
    cr = CUBE.temp[2];

    pyrows = PyObject_GetIter(cover);
    if (pyrows == NULL)
        goto error;

    while ((pyrow = PyIter_Next(pyrows)) != 0) {
        val = PySequence_Length(pyrow);
        if (val != 2) {
            PyErr_Format(PyExc_ValueError, "expected row vector with length 2, got %d", val);
            Py_DECREF(pyrow);
            Py_DECREF(pyrows);
            goto error;
        }
        pyins = PySequence_GetItem(pyrow, 0);
        val = PySequence_Length(pyins);
        if (val != ninputs) {
            PyErr_Format(PyExc_ValueError, "expected %d inputs, got %d", ninputs, val);
            Py_DECREF(pyins);
            Py_DECREF(pyrow);
            Py_DECREF(pyrows);
            goto error;
        }
        set_clear(cf, CUBE.size);
        index = 0;
        for (i = 0; i < ninputs; i++) {
            pylong = PySequence_GetItem(pyins, i);
            if (!PyLong_Check(pylong)) {
                PyErr_SetString(PyExc_TypeError, "expected input to be an int");
                Py_DECREF(pylong);
                Py_DECREF(pyins);
                Py_DECREF(pyrow);
                Py_DECREF(pyrows);
                goto error;
            }

            val = PyLong_AsLong(pylong);
            maxval = (1 << CUBE.part_size[i]) - 1;
            if (val < 0 || val > maxval) {
                PyErr_Format(PyExc_ValueError, "expected input in range [0, %d], got: %d", maxval, val);
                Py_DECREF(pylong);
                Py_DECREF(pyins);
                Py_DECREF(pyrow);
                Py_DECREF(pyrows);
                goto error;
            }

            for (j = 0; j < CUBE.part_size[i]; j++, index++) {
                if (val & (1 << j))
                    set_insert(cf, index);
            }

            Py_DECREF(pylong);
        } /* for (i = 0; i < ninputs; i++) */
        Py_DECREF(pyins);

        set_copy(cd, cf);
        set_copy(cr, cf);

        pyouts = PySequence_GetItem(pyrow, 1);
        val = PySequence_Length(pyouts);
        if (val != noutputs) {
            PyErr_Format(PyExc_ValueError, "expected %d outputs, got %d", noutputs, val);
            Py_DECREF(pyrow);
            Py_DECREF(pyrows);
            goto error;
        }

        savef = saved = saver = 0;
        for (i = 0; i < noutputs; i++, index++) {
            pylong = PySequence_GetItem(pyouts, i);
            if (!PyLong_Check(pylong)) {
                PyErr_SetString(PyExc_TypeError, "expected output to be an int");
                Py_DECREF(pylong);
                Py_DECREF(pyouts);
                Py_DECREF(pyrow);
                Py_DECREF(pyrows);
                goto error;
            }
            val = PyLong_AsLong(pylong);
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
                Py_DECREF(pylong);
                Py_DECREF(pyouts);
                Py_DECREF(pyrow);
                Py_DECREF(pyrows);
                goto error;
            }

            Py_DECREF(pylong);
        } /* for (i = 0; i < noutputs; i++) */
        Py_DECREF(pyouts);

        if (savef) F = sf_addset(F, cf);
        if (saved) D = sf_addset(D, cd);
        if (saver) R = sf_addset(R, cr);

        Py_DECREF(pyrow);
    } /* for pyrow in pyrows */
    Py_DECREF(pyrows);

    if (PyErr_Occurred())
        goto error;

    /* Success */
    return 1;

error:
    return 0;
}

/*
** Convert an Espresso cover to a Python set(((int), (int)))
*/
static PyObject *
_esprcov2pycov(int ninputs, int noutputs, set_family_t *F)
{
    int i;

    PyObject *pyset, *pyimpl, *pyins, *pyouts, *pylong;

    set *last, *p;

    pyset = PySet_New(0);
    if (pyset == NULL)
        goto error;

    foreach_set(F, last, p) {
        pyins = PyTuple_New(ninputs);
        if (pyins == NULL)
            goto decref_pyset;
        for (i = 0; i < ninputs; i++) {
            pylong = PyLong_FromLong((long) GETINPUT(p, i));
            if (PyTuple_SetItem(pyins, i, pylong) < 0) {
                Py_DECREF(pylong);
                Py_DECREF(pyins);
                goto decref_pyset;
            }
        }

        pyouts = PyTuple_New(noutputs);
        if (pyouts == NULL) {
            Py_DECREF(pyins);
            goto decref_pyset;
        }
        for (i = 0; i < noutputs; i++) {
            pylong = PyLong_FromLong((long) GETOUTPUT(p, i));
            if (PyTuple_SetItem(pyouts, i, pylong) < 0) {
                Py_DECREF(pylong);
                goto decref_pyins_pyouts;
            }
        }

        pyimpl = PyTuple_New(2);
        if (pyimpl == NULL)
            goto decref_pyins_pyouts;
        if (PyTuple_SetItem(pyimpl, 0, pyins) < 0) {
            Py_DECREF(pyimpl);
            goto decref_pyins_pyouts;
        }
        if (PyTuple_SetItem(pyimpl, 1, pyouts) < 0) {
            Py_DECREF(pyimpl);
            Py_DECREF(pyouts);
            goto decref_pyset;
        }
        if (PySet_Add(pyset, pyimpl) < 0) {
            Py_DECREF(pyimpl);
            goto decref_pyset;
        }
    }

    /* Success! */
    return pyset;

decref_pyins_pyouts:
    Py_DECREF(pyins);
    Py_DECREF(pyouts);

decref_pyset:
    Py_DECREF(pyset);

error:
    return NULL;
}

/*
** Python function definition: espresso.get_config()
*/
PyDoc_STRVAR(_get_config_docstring,
    "Return a dict of Espresso global configuration values."
);

static PyObject *
_get_config(PyObject *self)
{
    return Py_BuildValue(
               "{s:i, s:i, s:i, s:i, s:i, s:i, s:i}",

               "single_expand",     single_expand,
               "remove_essential",  remove_essential,
               "force_irredundant", force_irredundant,
               "unwrap_onset",      unwrap_onset,
               "recompute_onset",   recompute_onset,
               "use_super_gasp",    use_super_gasp,

               "skip_make_sparse",  skip_make_sparse
           );
}

/*
** Python function definition: espresso.set_config()
*/
PyDoc_STRVAR(_set_config_docstring,
    "Set Espresso global configuration values.\n\
\n\
    Parameters\n\
    ----------\n\
    single_expand : bool\n\
        stop after first expand/irredundant\n\
\n\
    remove_essential : bool\n\
        remove essential primes\n\
\n\
    force_irredundant : bool\n\
        iterate make_sparse to force a minimal solution\n\
\n\
    unwrap_onset : bool\n\
        unwrap the function output part before first expand\n\
\n\
    recompute_onset : bool\n\
        recompute onset using the complement before starting\n\
\n\
    use_super_gasp : bool\n\
        use the super_gasp strategy rather than last_gasp\n\
\n\
    skip_make_sparse : bool\n\
        skip the make_sparse step\n\
    "
);

static PyObject *
_set_config(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "remove_essential", "single_expand", "use_super_gasp",
        "recompute_onset", "unwrap_onset", "force_irredundant",
        "skip_make_sparse",
        NULL
    };

    PyArg_ParseTupleAndKeywords(
        args, kwargs, "|iiiiiii:set_config", keywords,
        &remove_essential, &single_expand, &use_super_gasp,
        &recompute_onset, &unwrap_onset, &force_irredundant,
        &skip_make_sparse
    );

    Py_RETURN_NONE;
}

/*
** Python function definition: espresso.espresso()
*/
PyDoc_STRVAR(_espresso_docstring,
    "\n\
    Return a logically equivalent, (near) minimal cost set of product-terms\n\
    to represent the ON-set and optionally minterms that lie in the DC-set,\n\
    without containing any minterms of the OFF-set.\n\
\n\
    Parameters\n\
    ----------\n\
    ninputs : posint\n\
        Number of inputs in the implicant in-part vector.\n\
\n\
    noutputs : posint\n\
        Number of outputs in the implicant out-part vector.\n\
\n\
    cover : iter(((int), (int)))\n\
        The iterator over multi-output implicants.\n\
        A multi-output implicant is a pair of row vectors of dimension\n\
        *ninputs*, and *noutputs*, respectively.\n\
        The input part contains integers in positional cube notation,\n\
        and the output part contains entries in {0, 1, 2}.\n\
\n\
        '0' means 0 for R-type covers, otherwise has no meaning.\n\
        '1' means 1 for F-type covers, otherwise has no meaning.\n\
        '2' means \"don't care\" for D-type covers, otherwise has no meaning.\n\
\n\
    intype : int\n\
        A flag field that indicates the type of the input cover.\n\
        F-type = 1, D-type = 2, R-type = 4\n\
\n\
    Returns\n\
    -------\n\
    set of implicants in the same format as the input cover\n\
    "
);

static PyObject *
_espresso(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {
        "ninputs", "noutputs", "cover", "intype",
        NULL
    };

    int err;

    int ninputs, noutputs;
    PyObject *cover;
    int intype = F_type | D_type;

    set_family_t *F, *Fsave;
    set_family_t *D;
    set_family_t *R;

    PyObject *pyret = NULL;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "iiO|i:espresso", keywords,
            &ninputs, &noutputs, &cover, &intype))
        goto error;

    if (ninputs <= 0) {
        PyErr_Format(PyExc_ValueError, "expected ninputs > 0, got: %d", ninputs);
        goto error;
    }
    if (noutputs <= 0) {
        PyErr_Format(PyExc_ValueError, "expected noutputs > 0, got: %d", noutputs);
        goto error;
    }
    if (!(intype & FR_type)) {
        PyErr_SetString(PyExc_ValueError, "expected intype in {f, r, fd, fr, dr, fdr}");
        goto error;
    }

    /* Initialize global CUBE dimensions */
    CUBE.num_binary_vars = ninputs;
    CUBE.num_vars = ninputs + 1;
    CUBE.part_size = (int *) malloc(CUBE.num_vars * sizeof(int));
    CUBE.part_size[CUBE.num_vars-1] = noutputs;
    cube_setup();

    /* Initialize F^on, F^dc, F^off */
    F = sf_new(10, CUBE.size);
    D = sf_new(10, CUBE.size);
    R = sf_new(10, CUBE.size);

    if (!_pycov2esprcov(F, D, R, ninputs, noutputs, cover, intype))
        goto free_espresso;

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

    /* Might return NULL */
    pyret = _esprcov2pycov(ninputs, noutputs, F);

free_espresso:
    sf_free(F);
    sf_free(D);
    sf_free(R);
    sf_cleanup();
    sm_cleanup();
    cube_setdown();
    free(CUBE.part_size);

error:
    return pyret;
}

/*
** Python module definition: espresso
*/

PyDoc_STRVAR(_module_docstring,
"\n\
Interface to Espresso logic minimization engine\n\
\n\
Constants:\n\
    FTYPE\n\
    DTYPE\n\
    RTYPE\n\
\n\
Exceptions:\n\
    EspressoError\n\
\n\
Interface Functions:\n\
    espresso\n\
"
);

static PyMethodDef _module_methods[] = {
    {"get_config", (PyCFunction) _get_config, METH_NOARGS,                  _get_config_docstring},
    {"set_config", (PyCFunction) _set_config, METH_VARARGS | METH_KEYWORDS, _set_config_docstring},
    {"espresso",   (PyCFunction) _espresso,   METH_VARARGS | METH_KEYWORDS, _espresso_docstring},

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

