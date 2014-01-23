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

#include <Python.h>

#include "espresso.h"

/*
** Python exception definition: espresso.EspressoError
*/
PyDoc_STRVAR(_espresso_error_docstring, "Espresso Error");

static PyObject *_espresso_error;

/*
** Python module definition: espresso
*/

PyDoc_STRVAR(_module_docstring,
"\n\
Interface to Espresso logic minimization engine\n\
\n\
Exceptions:\n\
    EspressoError\n\
"
);

static PyMethodDef _module_methods[] = {

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

