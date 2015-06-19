/*
** Filename: dict.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* Maximum load allowed before enlargement */
#define MAX_LOAD 1.5

/* Min/Max indices in the primes table */
#define MIN_IDX 4
#define MAX_IDX 30


/* Define static size_t _primes[] */
#include "primes-inl.c"


static size_t
_hash(struct BX_Dict *dict, struct BoolExpr *key)
{
    return (size_t) key % _primes[dict->_pridx];
}


static bool
_eq(struct BoolExpr *key1, struct BoolExpr *key2)
{
    return key1 == key2;
}


static void
_list_del(struct BX_DictItem *list)
{
    if (list) {
        _list_del(list->tail);
        BX_DecRef(list->key);
        BX_DecRef(list->val);
        free(list);
    }
}


static struct BoolExpr *
_list_search(struct BX_DictItem *list, struct BoolExpr *key)
{
    if (!list)
        return (struct BoolExpr *) NULL;

    if (_eq(list->key, key))
        return list->val;

    return _list_search(list->tail, key);
}


struct BX_Dict *
BX_Dict_New(void)
{
    struct BX_Dict *dict;
    size_t width = _primes[MIN_IDX];

    dict = malloc(sizeof(struct BX_Dict));
    if (dict == NULL)
        return NULL; // LCOV_EXCL_LINE

    dict->_pridx = MIN_IDX;
    dict->length = 0;
    dict->items = malloc(width * sizeof(struct BX_DictItem *));
    if (dict->items == NULL) {
        free(dict);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    /* Initialize items to NULL */
    for (size_t i = 0; i < width; ++i)
        dict->items[i] = (struct BX_DictItem *) NULL;

    return dict;
}


void
BX_Dict_Del(struct BX_Dict *dict)
{
    for (size_t i = 0; i < _primes[dict->_pridx]; ++i)
        _list_del(dict->items[i]);
    free(dict->items);
    free(dict);
}


static bool
_dict_insert(struct BX_Dict *dict, struct BoolExpr *key, struct BoolExpr *val)
{
    size_t index = _hash(dict, key);
    struct BX_DictItem *item;
    struct BX_DictItem **tail;

    tail = &dict->items[index];
    for (item = dict->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BX_DecRef(item->key);
            BX_DecRef(item->val);
            item->key = BX_IncRef(key);
            item->val = BX_IncRef(val);
            return true;
        }
        tail = &item->tail;
    }

    item = malloc(sizeof(struct BX_DictItem));
    if (item == NULL)
        return false; // LCOV_EXCL_LINE

    item->key = BX_IncRef(key);
    item->val = BX_IncRef(val);
    item->tail = (struct BX_DictItem *) NULL;

    *tail = item;

    dict->length += 1;

    return true;
}


static bool
_enlarge(struct BX_Dict *dict)
{
    struct BX_DictItem *item;

    size_t pridx = dict->_pridx;
    size_t length = dict->length;
    struct BX_DictItem **items = dict->items;

    size_t old_width = _primes[pridx];
    size_t new_width = _primes[pridx + 1];

    dict->_pridx += 1;
    dict->length = 0;
    dict->items = malloc(new_width * sizeof(struct BX_DictItem *));
    if (dict->items == NULL)
        return false; // LCOV_EXCL_LINE

    for (size_t i = 0; i < new_width; ++i)
        dict->items[i] = (struct BX_DictItem *) NULL;

    for (size_t i = 0; i < old_width; ++i) {
        for (item = items[i]; item; item = item->tail) {
            if (!_dict_insert(dict, item->key, item->val)) {
                /* LCOV_EXCL_START */
                for (size_t j = 0; j < i; ++j)
                    _list_del(dict->items[j]);
                free(dict->items);
                dict->_pridx = pridx;
                dict->length = length;
                dict->items = items;
                return false;
                /* LCOV_EXCL_STOP */
            }
        }
    }

    for (size_t i = 0; i < old_width; ++i)
        _list_del(items[i]);
    free(items);

    return true;
}


bool
BX_Dict_Insert(struct BX_Dict *dict, struct BoolExpr *key, struct BoolExpr *val)
{
    double load;

    if (!_dict_insert(dict, key, val))
        return false; // LCOV_EXCL_LINE

    load = (double) dict->length / (double) _primes[dict->_pridx];

    if (dict->_pridx < MAX_IDX && load > MAX_LOAD) {
        if (!_enlarge(dict))
            return false; // LCOV_EXCL_LINE
    }

    return true;
}


bool
BX_Dict_Remove(struct BX_Dict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);
    struct BX_DictItem *item;
    struct BX_DictItem **tail;

    tail = &dict->items[index];
    for (item = dict->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BX_DecRef(item->key);
            BX_DecRef(item->val);
            *tail = item->tail;
            free(item);
            dict->length -= 1;
            return true;
        }
        tail = &item->tail;
    }

    return false;
}


struct BoolExpr *
BX_Dict_Search(struct BX_Dict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key);
}


bool
BX_Dict_Contains(struct BX_Dict *dict, struct BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key) != (struct BoolExpr *) NULL;
}


void
BX_Dict_Clear(struct BX_Dict *dict)
{
    for (size_t i = 0; i < _primes[dict->_pridx]; ++i) {
        if (dict->items[i]) {
            _list_del(dict->items[i]);
            dict->items[i] = (struct BX_DictItem *) NULL;
        }
    }

    dict->length = 0;
}


bool
BX_Dict_Equal(struct BX_Dict *self, struct BX_Dict *other)
{
    if (self->length != other->length)
        return false;

    struct BX_DictItem *item;

    /* All items in self must also be in other (and vice versa) */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (item->val != BX_Dict_Search(other, item->key))
                return false;
        }
    }

    return true;
}

