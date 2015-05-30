/*
** Filename: dict.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "dict.h"
#include "boolexpr.h"


#include "primes-inl.c"


static size_t
_hash(struct BoolExprDict *dict, struct BoolExpr *key)
{
    return (size_t) key % _primes[dict->_pridx];
}


static bool
_eq(struct BoolExpr *key1, struct BoolExpr *key2)
{
    return key1 == key2;
}


static void
_list_del(struct BoolExprDictItem *list)
{
    if (list) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);
        BoolExpr_DecRef(list->val);
        free(list);
    }
}


static struct BoolExpr *
_list_search(struct BoolExprDictItem *list, struct BoolExpr *key)
{
    if (!list)
        return (struct BoolExpr *) NULL;

    if (_eq(list->key, key))
        return list->val;

    return _list_search(list->tail, key);
}


struct BoolExprDict *
BoolExprDict_New(void)
{
    struct BoolExprDict *dict;
    size_t width = _primes[MIN_IDX];

    dict = malloc(sizeof(struct BoolExprDict));
    if (dict == NULL)
        return NULL; // LCOV_EXCL_LINE

    dict->_pridx = MIN_IDX;
    dict->length = 0;
    dict->items = malloc(width * sizeof(struct BoolExprDictItem *));
    if (dict->items == NULL) {
        free(dict);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    /* Initialize items to NULL */
    for (size_t i = 0; i < width; ++i)
        dict->items[i] = (struct BoolExprDictItem *) NULL;

    return dict;
}


void
BoolExprDict_Del(struct BoolExprDict *dict)
{
    for (size_t i = 0; i < _primes[dict->_pridx]; ++i)
        _list_del(dict->items[i]);
    free(dict->items);
    free(dict);
}


static bool
_insert(struct BoolExprDict *dict, struct BoolExpr *key, struct BoolExpr *val)
{
    size_t index = _hash(dict, key);
    struct BoolExprDictItem *item;

    for (item = dict->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BoolExpr_DecRef(item->key);
            BoolExpr_DecRef(item->val);
            item->key = BoolExpr_IncRef(key);
            item->val = BoolExpr_IncRef(val);
            return true;
        }
    }

    item = malloc(sizeof(struct BoolExprDictItem));
    if (item == NULL)
        return false; // LCOV_EXCL_LINE

    item->key = BoolExpr_IncRef(key);
    item->val = BoolExpr_IncRef(val);
    item->tail = dict->items[index];

    dict->items[index] = item;
    dict->length += 1;

    return true;
}


static bool
_enlarge(struct BoolExprDict *dict)
{
    struct BoolExprDictItem *item;
    size_t pridx = dict->_pridx;
    struct BoolExprDictItem **items = dict->items;

    dict->_pridx += 1;
    dict->length = 0;
    dict->items = malloc(_primes[dict->_pridx] * sizeof(struct BoolExprDictItem *));
    if (dict->items == NULL)
        return false; // LCOV_EXCL_LINE

    for (size_t i = 0; i < _primes[dict->_pridx]; ++i)
        dict->items[i] = (struct BoolExprDictItem *) NULL;

    for (size_t i = 0; i < _primes[pridx]; ++i) {
        for (item = items[i]; item; item = item->tail) {
            if (!_insert(dict, item->key, item->val)) {
                /* LCOV_EXCL_START */
                for (size_t j = 0; j < i; ++j)
                    _list_del(items[j]);
                free(items);
                return false;
                /* LCOV_EXCL_STOP */
            }
        }
        _list_del(items[i]);
    }
    free(items);

    return true;
}


bool
BoolExprDict_Insert(struct BoolExprDict *dict, struct BoolExpr *key, struct BoolExpr *val)
{
    double load;

    if (!_insert(dict, key, val))
        return false; // LCOV_EXCL_LINE

    load = (double) dict->length / (double) _primes[dict->_pridx];

    if (dict->_pridx < MAX_IDX && load > MAX_LOAD) {
        if (!_enlarge(dict))
            return false; // LCOV_EXCL_LINE
    }

    return true;
}


bool
BoolExprDict_Remove(struct BoolExprDict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);

    struct BoolExprDictItem **p = &dict->items[index];
    struct BoolExprDictItem *item = dict->items[index];

    while (item) {
        if (_eq(item->key, key)) {
            BoolExpr_DecRef(item->key);
            BoolExpr_DecRef(item->val);
            *p = item->tail;
            free(item);
            dict->length -= 1;

            return true;
        }
        p = &item->tail;
        item = item->tail;
    }

    return false;
}


struct BoolExpr *
BoolExprDict_Search(struct BoolExprDict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key);
}


bool
BoolExprDict_Contains(struct BoolExprDict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key) != (struct BoolExpr *) NULL;
}


void
BoolExprDict_Clear(struct BoolExprDict *dict)
{
    for (size_t i = 0; i < _primes[dict->_pridx]; ++i) {
        if (dict->items[i]) {
            _list_del(dict->items[i]);
            dict->items[i] = (struct BoolExprDictItem *) NULL;
        }
    }

    dict->length = 0;
}

