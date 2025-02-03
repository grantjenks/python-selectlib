/* selectlib.c */
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
*/
static void
swap_items(PyObject *list, Py_ssize_t i, Py_ssize_t j, PyObject **keys)
{
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
   Standard in-place three-way partition (Dutch National Flag style) based on a given pivot.
   Rearranges the list (and keys array if present) so that all elements whose key is less than
   pivot come first, followed by those equal to pivot, then those greater.
   Upon return, *low is the first index of the "equal" section and *mid is one past the end.
*/
static int
partition_by_pivot(PyObject *list, PyObject **keys, Py_ssize_t n, PyObject *pivot,
                   Py_ssize_t *low, Py_ssize_t *mid)
{
    Py_ssize_t i = 0, j = 0, k = n - 1;
    int cmp_lt, cmp_gt;
    while (j <= k) {
        PyObject *current = keys ? keys[j] : PyList_GET_ITEM(list, j);
        cmp_lt = less_than(current, pivot);
        cmp_gt = less_than(pivot, current);
        if (cmp_lt < 0 || cmp_gt < 0)
            return -1;
        if (cmp_lt == 1) {  /* current < pivot */
            swap_items(list, i, j, keys);
            i++; j++;
        }
        else if (cmp_lt == 0 && cmp_gt == 0) {  /* current == pivot */
            j++;
        }
        else {  /* current > pivot */
            swap_items(list, j, k, keys);
            k--;
        }
    }
    *low = i;
    *mid = j;
    return 0;
}

/*
   Original in-place quickselect implementation.
   It partitions the list (and keys array if provided) so that
   the element at index k is in its final sorted position.
*/
static int
quickselect_inplace(PyObject *list, PyObject **keys,
                    Py_ssize_t left, Py_ssize_t right, Py_ssize_t k)
{
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned)time(NULL));
        seeded = 1;
    }

    while (left < right) {
        Py_ssize_t pivot_index = left + rand() % (right - left + 1);
        Py_ssize_t pos;
        /* Use partition function similar to before.
           We reuse the swap_items function and keys if available.
         */
        /* Move pivot to the end */
        swap_items(list, pivot_index, right, keys);
        PyObject *pivot_val = keys ? keys[right] : PyList_GET_ITEM(list, right);
        pos = left;
        for (Py_ssize_t i = left; i < right; i++) {
            PyObject *current = keys ? keys[i] : PyList_GET_ITEM(list, i);
            int cmp = less_than(current, pivot_val);
            if (cmp < 0)
                return -1;
            if (cmp == 1) {
                swap_items(list, i, pos, keys);
                pos++;
            }
        }
        swap_items(list, pos, right, keys);
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
   Partition the list in-place so that the element at the given index is in its
   final sorted position. An optional key function may be provided.
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

    PyObject **keys = NULL;
    if (use_key) {
        keys = PyMem_New(PyObject *, n);
        if (keys == NULL) {
            PyErr_NoMemory();
            return NULL;
        }
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *item = PyList_GET_ITEM(values, i);
            PyObject *keyval = PyObject_CallFunctionObjArgs(key, item, NULL);
            if (keyval == NULL) {
                for (Py_ssize_t j = 0; j < i; j++)
                    Py_DECREF(keys[j]);
                PyMem_Free(keys);
                return NULL;
            }
            keys[i] = keyval;
        }
    }

    if (n > 0) {
        if (quickselect_inplace(values, keys, 0, n - 1, target_index) < 0) {
            if (keys) {
                for (Py_ssize_t i = 0; i < n; i++)
                    Py_DECREF(keys[i]);
                PyMem_Free(keys);
            }
            return NULL;
        }
    }
    if (keys) {
        for (Py_ssize_t i = 0; i < n; i++)
            Py_DECREF(keys[i]);
        PyMem_Free(keys);
    }

    Py_RETURN_NONE;
}

/* ---------- New heapselect implementation ---------- */

/* Structure to hold an element for the heap.
   Each HeapItem contains a pointer to the list element (value) and
   the corresponding key (if any; if not, key==value).
*/
typedef struct {
    PyObject *value;
    PyObject *key;
} HeapItem;

/* Max-heap helper: Restore the max-heap property for heap[i] assuming
   that the trees rooted at its children are valid.
*/
static void
max_heapify(HeapItem *heap, Py_ssize_t heap_size, Py_ssize_t i)
{
    Py_ssize_t largest = i;
    Py_ssize_t left = 2 * i + 1;
    Py_ssize_t right = 2 * i + 2;
    int cmp;

    if (left < heap_size) {
        cmp = less_than(heap[largest].key, heap[left].key);
        if (cmp == 1) {
            largest = left;
        }
    }
    if (right < heap_size) {
        cmp = less_than(heap[largest].key, heap[right].key);
        if (cmp == 1) {
            largest = right;
        }
    }
    if (largest != i) {
        HeapItem temp = heap[i];
        heap[i] = heap[largest];
        heap[largest] = temp;
        max_heapify(heap, heap_size, largest);
    }
}

/* Build a max-heap from an array of HeapItem of size heap_size */
static void
build_max_heap(HeapItem *heap, Py_ssize_t heap_size)
{
    for (Py_ssize_t i = (heap_size / 2) - 1; i >= 0; i--) {
        max_heapify(heap, heap_size, i);
    }
}

/*
   heapselect(values: list[Any], index: int, key=None) -> None
   Partition the list in-place so that the element at the given index (k) is in its
   final sorted position. This implementation uses a heap strategy (specifically,
   building a fixed-size max-heap on the first k+1 elements, then processing the rest)
   to determine the kth smallest element.
*/
static PyObject *
selectlib_heapselect(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"values", "index", "key", NULL};
    PyObject *values;
    Py_ssize_t target_index;
    PyObject *key = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "On|O:heapselect",
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

    /* If a key function is given, precompute keys for the entire list.
       (This mirrors the approach in quickselect.)
    */
    PyObject **keys = NULL;
    if (use_key) {
        keys = PyMem_New(PyObject *, n);
        if (keys == NULL) {
            PyErr_NoMemory();
            return NULL;
        }
        for (Py_ssize_t i = 0; i < n; i++) {
            PyObject *item = PyList_GET_ITEM(values, i);
            PyObject *keyval = PyObject_CallFunctionObjArgs(key, item, NULL);
            if (keyval == NULL) {
                for (Py_ssize_t j = 0; j < i; j++)
                    Py_DECREF(keys[j]);
                PyMem_Free(keys);
                return NULL;
            }
            keys[i] = keyval;
        }
    }

    /* Heap selection:
       We want the kth smallest element (where k = target_index). Build a max-heap
       of the first (target_index+1) items so that the heap’s root is the largest among
       them (and hence the kth smallest overall so far). Then for each subsequent item,
       if its key is less than the root, update the root and restore the heap.
    */
    Py_ssize_t heap_size = target_index + 1;
    HeapItem *heap = PyMem_New(HeapItem, heap_size);
    if (heap == NULL) {
        if (keys) {
            for (Py_ssize_t i = 0; i < n; i++)
                Py_DECREF(keys[i]);
            PyMem_Free(keys);
        }
        PyErr_NoMemory();
        return NULL;
    }

    for (Py_ssize_t i = 0; i < heap_size; i++) {
        heap[i].value = PyList_GET_ITEM(values, i);
        if (use_key)
            heap[i].key = keys[i];
        else
            heap[i].key = PyList_GET_ITEM(values, i);
    }
    build_max_heap(heap, heap_size);

    for (Py_ssize_t i = heap_size; i < n; i++) {
        PyObject *current_key = use_key ? keys[i] : PyList_GET_ITEM(values, i);
        int cmp = less_than(current_key, heap[0].key);
        if (cmp < 0) {
            /* Propagate error */
            PyMem_Free(heap);
            if (keys) {
                for (Py_ssize_t j = 0; j < n; j++)
                    Py_DECREF(keys[j]);
                PyMem_Free(keys);
            }
            return NULL;
        }
        if (cmp == 1) {  /* current < heap root */
            /* Replace the root with current and re-heapify */
            heap[0].value = PyList_GET_ITEM(values, i);
            heap[0].key = current_key;
            max_heapify(heap, heap_size, 0);
        }
    }

    /* The kth smallest element candidate is now at the root of the heap. */
    PyObject *pivot = heap[0].value;
    PyObject *pivot_key = heap[0].key;

    PyMem_Free(heap);

    /* Partition the entire list around the pivot value (using pivot_key).
       After partitioning, the block of elements equal to the pivot should contain
       the target_index.
    */
    Py_ssize_t low, mid;
    if (partition_by_pivot(values, keys, n, pivot_key, &low, &mid) < 0) {
        if (keys) {
            for (Py_ssize_t i = 0; i < n; i++)
                Py_DECREF(keys[i]);
            PyMem_Free(keys);
        }
        return NULL;
    }

    /* Verify that target_index lies in the "equal" partition.
       (In a correct run this must be true.)
    */
    if (!(target_index >= low && target_index < mid)) {
        if (keys) {
            for (Py_ssize_t i = 0; i < n; i++)
                Py_DECREF(keys[i]);
            PyMem_Free(keys);
        }
        PyErr_SetString(PyExc_RuntimeError, "heapselect partition failed to locate the target index");
        return NULL;
    }

    if (keys) {
        for (Py_ssize_t i = 0; i < n; i++)
            Py_DECREF(keys[i]);
        PyMem_Free(keys);
    }

    Py_RETURN_NONE;
}

/* ---------- Module method definitions ---------- */
static PyMethodDef selectlib_methods[] = {
    {"quickselect", (PyCFunction)selectlib_quickselect,
     METH_VARARGS | METH_KEYWORDS,
     "quickselect(values: list[Any], index: int, key=None) -> None\n\n"
     "Partition the list in-place so that the element at the given index is in its final sorted position."},
    {"heapselect", (PyCFunction)selectlib_heapselect,
     METH_VARARGS | METH_KEYWORDS,
     "heapselect(values: list[Any], index: int, key=None) -> None\n\n"
     "Partition the list in-place using a heap strategy so that the element at the given index is in its final sorted position."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef selectlibmodule = {
    PyModuleDef_HEAD_INIT,
    "selectlib",
    "Module that implements the quickselect and heapselect algorithms.",
    -1,
    selectlib_methods,
};

PyMODINIT_FUNC
PyInit_selectlib(void)
{
    PyObject *m = PyModule_Create(&selectlibmodule);
    if (m == NULL)
        return NULL;
    if (PyModule_AddStringConstant(m, "__version__", SELECTLIB_VERSION) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
