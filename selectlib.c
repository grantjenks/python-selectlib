#include <Python.h>
#include <listobject.h>
#include <stdlib.h>
#include <time.h>

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

#ifndef SELECTLIB_VERSION
#define SELECTLIB_VERSION "1.0.0"
#endif

/*
   Helper function that compares two PyObject*s using the < operator.
   Returns 1 if a < b, 0 if not, or -1 if an error occurred.
*/
static int
less_than(PyObject *a, PyObject *b)
{
    int cmp = PyObject_RichCompareBool(a, b, Py_LT);
    return cmp;
}

/*
   Swap the elements at indices i and j in the Python list.
   If keys is not NULL, also swap the corresponding keys.
   This function directly manipulates the list internals.
*/
static void
swap_items(PyObject *list, Py_ssize_t i, Py_ssize_t j, PyObject **keys)
{
    /* Cast to PyListObject to access the internal array */
    PyListObject *lst = (PyListObject *)list;
    PyObject *temp = lst->ob_item[i];
    lst->ob_item[i] = lst->ob_item[j];
    lst->ob_item[j] = temp;
    
    if (keys != NULL) {
        PyObject *temp_key = keys[i];
        keys[i] = keys[j];
        keys[j] = temp_key;
    }
}

/*
   Partition the subarray [left, right] around a pivot.
   The pivot is initially at pivot_index. After partitioning,
   the pivot is placed at new_pivot_index (returned via pointer).
   Returns 0 on success or -1 if an error occurred.
*/
static int
partition(PyObject *list, PyObject **keys, Py_ssize_t left, Py_ssize_t right,
          Py_ssize_t pivot_index, Py_ssize_t *new_pivot_index)
{
    /* Move pivot to the end */
    swap_items(list, pivot_index, right, keys);

    PyObject *pivot_val;
    if (keys != NULL)
        pivot_val = keys[right];
    else
        pivot_val = PyList_GET_ITEM(list, right);

    Py_ssize_t store_index = left;
    for (Py_ssize_t i = left; i < right; i++) {
        PyObject *current;
        if (keys != NULL)
            current = keys[i];
        else
            current = PyList_GET_ITEM(list, i);

        int cmp = less_than(current, pivot_val);
        if (cmp < 0)
            return -1;
        if (cmp) {
            swap_items(list, i, store_index, keys);
            store_index++;
        }
    }
    swap_items(list, store_index, right, keys);
    *new_pivot_index = store_index;
    return 0;
}

/*
   In-place quickselect algorithm on the list.
   It partitions the list (and the keys array if provided) so that 
   the element at index k is in its final sorted position.
   Operates on indices in [left, right].
   Returns 0 on success or -1 on error.
*/
static int
quickselect_inplace(PyObject *list, PyObject **keys,
                    Py_ssize_t left, Py_ssize_t right, Py_ssize_t k)
{
    /* Seed the random number generator once (if needed) */
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned)time(NULL));
        seeded = 1;
    }
    
    while (left < right) {
        /* Choose a random pivot_index between left and right (inclusive) */
        Py_ssize_t pivot_index = left + rand() % (right - left + 1);
        Py_ssize_t pos;
        if (partition(list, keys, left, right, pivot_index, &pos) < 0)
            return -1;
        if (pos == k)
            return 0;
        else if (k < pos)
            right = pos - 1;
        else
            left = pos + 1;
    }
    return 0;
}

/*
   quickselect(values: list[Any], index: int, key=None) -> None

   Partition the list in-place such that the element in the specified
   index is the one that would be there in a sorted list. An optional
   key function may be provided to extract a comparison key from each element.
*/
static PyObject *
selectlib_quickselect(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"values", "index", "key", NULL};
    PyObject *values;
    Py_ssize_t target_index;
    PyObject *key = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "On|O:quickselect",
                                     kwlist, &values, &target_index, &key))
        return NULL;

    if (!PyList_Check(values)) {
        PyErr_SetString(PyExc_TypeError, "values must be a list");
        return NULL;
    }

    Py_ssize_t n = PyList_Size(values);
    if (target_index < 0 || target_index >= n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    int use_key = 0;
    if (key != Py_None) {
        if (!PyCallable_Check(key)) {
            PyErr_SetString(PyExc_TypeError, "key must be callable");
            return NULL;
        }
        use_key = 1;
    }

    PyObject **keys_arr = NULL;
    if (use_key) {
        keys_arr = PyMem_New(PyObject *, n);
        if (keys_arr == NULL) {
            PyErr_NoMemory();
            return NULL;
        }
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *item = PyList_GET_ITEM(values, i);
            PyObject *key_val = PyObject_CallFunctionObjArgs(key, item, NULL);
            if (key_val == NULL) {
                for (Py_ssize_t j = 0; j < i; j++)
                    Py_DECREF(keys_arr[j]);
                PyMem_Free(keys_arr);
                return NULL;
            }
            keys_arr[i] = key_val;
        }
    }

    if (n > 0) {
        if (quickselect_inplace(values, keys_arr, 0, n - 1, target_index) < 0) {
            if (use_key) {
                for (Py_ssize_t i = 0; i < n; i++)
                    Py_DECREF(keys_arr[i]);
                PyMem_Free(keys_arr);
            }
            return NULL;
        }
    }

    if (use_key) {
        for (Py_ssize_t i = 0; i < n; i++)
            Py_DECREF(keys_arr[i]);
        PyMem_Free(keys_arr);
    }

    Py_RETURN_NONE;
}

static PyMethodDef selectlib_methods[] = {
    {"quickselect", (PyCFunction)selectlib_quickselect,
     METH_VARARGS | METH_KEYWORDS,
     "quickselect(values: list[Any], index: int, key=None) -> None\n\n"
     "Partition the list in-place so that the element at the given index is in its "
     "final sorted position."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef selectlibmodule = {
    PyModuleDef_HEAD_INIT,
    "selectlib",
    "Module that implements the quickselect algorithm.",
    -1,
    selectlib_methods,
};

PyMODINIT_FUNC
PyInit_selectlib(void)
{
    PyObject *m = PyModule_Create(&selectlibmodule);
    if (m == NULL)
        return NULL;
    /* Add the module's version constant */
    if (PyModule_AddStringConstant(m, "__version__", SELECTLIB_VERSION) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
