/*
** Filename: dict.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


#define MAX_LOAD 1.5


/*
** From: http://planetmath.org/goodhashtableprimes
*/

#define _MIN_IDX 5
#define _MAX_IDX 30

static size_t _primes[] = {
    0, 0, 0, 0, 0,

    /* (2^5,  2^6)  */ 53,
    /* (2^6,  2^7)  */ 97,
    /* (2^7,  2^8)  */ 193,
    /* (2^8,  2^9)  */ 389,
    /* (2^9,  2^10) */ 769,
    /* (2^10, 2^11) */ 1543,
    /* (2^11, 2^12) */ 3079,
    /* (2^12, 2^13) */ 6151,
    /* (2^13, 2^14) */ 12289,
    /* (2^14, 2^15) */ 24593,
    /* (2^15, 2^16) */ 49157,
    /* (2^16, 2^17) */ 98317,
    /* (2^17, 2^18) */ 196613,
    /* (2^18, 2^19) */ 393241,
    /* (2^19, 2^20) */ 786433,
    /* (2^20, 2^21) */ 1572869,
    /* (2^21, 2^22) */ 3145739,
    /* (2^22, 2^23) */ 6291469,
    /* (2^23, 2^24) */ 12582917,
    /* (2^24, 2^25) */ 25165843,
    /* (2^25, 2^26) */ 50331653,
    /* (2^26, 2^27) */ 100663319,
    /* (2^27, 2^28) */ 201326611,
    /* (2^28, 2^29) */ 402653189,
    /* (2^29, 2^30) */ 805306457,
    /* (2^30, 2^31) */ 1610612741,
};


struct BoolExprDictItem {
    struct BoolExpr *key;
    struct BoolExpr *val;
    struct BoolExprDictItem *tail;
};


static void
_list_del(struct BoolExprDictItem *list)
{
    if (list != (struct BoolExprDictItem *) NULL) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);
        BoolExpr_DecRef(list->val);

        free(list);
    }
}


static struct BoolExpr *
_list_search(struct BoolExprDictItem *list, struct BoolExpr *key)
{
    if (list == (struct BoolExprDictItem *) NULL)
        return (struct BoolExpr *) NULL;
    else if (list->key == key)
        return list->val;
    else
        return _list_search(list->tail, key);
}


struct BoolExprDict *
BoolExprDict_New(void)
{
    struct BoolExprDict *dict;
    size_t pridx = _MIN_IDX;
    size_t width = _primes[pridx];

    dict = (struct BoolExprDict *) malloc(sizeof(struct BoolExprDict));
    if (dict == NULL)
        return NULL; // LCOV_EXCL_LINE

    dict->items = (struct BoolExprDictItem **) malloc(width * sizeof(struct BoolExprDictItem *));
    if (dict->items == NULL) {
        free(dict);  // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    for (size_t i = 0; i < width; ++i)
        dict->items[i] = (struct BoolExprDictItem *) NULL;

    dict->length = 0;
    dict->pridx = pridx;

    return dict;
}


void
BoolExprDict_Del(struct BoolExprDict *dict)
{
    for (size_t i = 0; i < _primes[dict->pridx]; ++i)
        _list_del(dict->items[i]);

    free(dict->items);
    free(dict);
}


static size_t
_hash(struct BoolExprDict *dict, struct BoolExpr *key)
{
    return (size_t) key % _primes[dict->pridx];
}


static bool
_insert(struct BoolExprDict *dict, struct BoolExpr *key, struct BoolExpr *val)
{
    size_t index = _hash(dict, key);;
    struct BoolExprDictItem *item = dict->items[index];

    while (item != (struct BoolExprDictItem *) NULL) {
        if (item->key == key) {
            BoolExpr_DecRef(item->key);
            BoolExpr_DecRef(item->val);
            item->key = BoolExpr_IncRef(key);
            item->val = BoolExpr_IncRef(val);
            return true;
        }
        item = item->tail;
    }

    item = (struct BoolExprDictItem *) malloc(sizeof(struct BoolExprDictItem));
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

    size_t pridx = dict->pridx;
    struct BoolExprDictItem **items = dict->items;

    dict->length = 0;
    dict->pridx += 1;
    dict->items = (struct BoolExprDictItem **) malloc(_primes[dict->pridx] * sizeof(struct BoolExprDictItem *));
    for (size_t i = 0; i < _primes[dict->pridx]; ++i)
        dict->items[i] = (struct BoolExprDictItem *) NULL;

    for (size_t i = 0; i < _primes[pridx]; ++i) {
        item = items[i];
        while (item != (struct BoolExprDictItem *) NULL) {
            if (!_insert(dict, item->key, item->val)) {
                /* LCOV_EXCL_START */
                for (size_t j = 0; j < i; ++j)
                    _list_del(items[j]);
                free(items);
                return false;
                /* LCOV_EXCL_STOP */
            }
            item = item->tail;
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

    load = (double) dict->length / (double) _primes[dict->pridx];

    if (dict->pridx < _MAX_IDX && load > MAX_LOAD) {
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

    while (item != (struct BoolExprDictItem *) NULL) {
        if (item->key == key) {
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

