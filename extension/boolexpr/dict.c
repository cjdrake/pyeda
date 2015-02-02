/*
** Filename: dict.c
*/


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


struct _BoolExprDictItem {
    BoolExpr *key;
    BoolExpr *val;
    BoolExprDictItem *tail;
};


static void
_list_del(BoolExprDictItem *list)
{
    if (list != (BoolExprDictItem *) NULL) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);
        BoolExpr_DecRef(list->val);

        free(list);
    }
}


static BoolExpr *
_list_search(BoolExprDictItem *list, BoolExpr *key)
{
    if (list == (BoolExprDictItem *) NULL)
        return (BoolExpr *) NULL;
    else if (list->key == key)
        return list->val;
    else
        return _list_search(list->tail, key);
}


BoolExprDict *
BoolExprDict_New(size_t (*prehash)(BoolExpr *))
{
    BoolExprDict *dict;
    size_t pridx = _MIN_IDX;
    size_t width = _primes[pridx];

    dict = (BoolExprDict *) malloc(sizeof(BoolExprDict));

    /* LCOV_EXCL_START */
    if (dict == NULL)
        return NULL;
    /* LCOV_EXCL_STOP */

    dict->items = (BoolExprDictItem **) malloc(width * sizeof(BoolExprDictItem *));

    /* LCOV_EXCL_START */
    if (dict->items == NULL) {
        free(dict);
        return NULL;
    }
    /* LCOV_EXCL_STOP */

    for (size_t i = 0; i < width; ++i)
        dict->items[i] = (BoolExprDictItem *) NULL;

    dict->prehash = prehash;
    dict->length = 0;
    dict->pridx = pridx;

    return dict;
}


static size_t
_var2int(BoolExpr *var)
{
    return (size_t) (var->data.lit.uniqid - 1);
}


/* {var: ex} mapping */
BoolExprDict *
BoolExprVarMap_New(void)
{
    return BoolExprDict_New(_var2int);
}


static size_t
_lit2int(BoolExpr *lit)
{
    return (size_t) (lit->data.lit.uniqid < 0 ? -2 * lit->data.lit.uniqid - 2
                                              :  2 * lit->data.lit.uniqid - 1);
}


/* {lit: ex} mapping */
BoolExprDict *
BoolExprLitMap_New(void)
{
    return BoolExprDict_New(_lit2int);
}


void
BoolExprDict_Del(BoolExprDict *dict)
{
    for (size_t i = 0; i < _primes[dict->pridx]; ++i)
        _list_del(dict->items[i]);

    free(dict->items);
    free(dict);
}


static size_t
_hash(BoolExprDict *dict, BoolExpr *key)
{
    return dict->prehash(key) % _primes[dict->pridx];
}


static bool
_insert(BoolExprDict *dict, BoolExpr *key, BoolExpr *val)
{
    size_t index = _hash(dict, key);;
    BoolExprDictItem *item = dict->items[index];

    while (item != (BoolExprDictItem *) NULL) {
        if (item->key == key) {
            BoolExpr_DecRef(item->key);
            BoolExpr_DecRef(item->val);
            item->key = BoolExpr_IncRef(key);
            item->val = BoolExpr_IncRef(val);
            return true;
        }
        item = item->tail;
    }

    item = (BoolExprDictItem *) malloc(sizeof(BoolExprDictItem));

    /* LCOV_EXCL_START */
    if (item == NULL)
        return false;
    /* LCOV_EXCL_STOP */

    item->key = BoolExpr_IncRef(key);
    item->val = BoolExpr_IncRef(val);
    item->tail = dict->items[index];

    dict->items[index] = item;
    dict->length += 1;

    return true;
}


static bool
_enlarge(BoolExprDict *dict)
{
    BoolExprDictItem *item;

    size_t pridx = dict->pridx;
    BoolExprDictItem **items = dict->items;

    dict->length = 0;
    dict->pridx += 1;
    dict->items = (BoolExprDictItem **) malloc(_primes[dict->pridx] * sizeof(BoolExprDictItem *));
    for (size_t i = 0; i < _primes[dict->pridx]; ++i)
        dict->items[i] = (BoolExprDictItem *) NULL;

    for (size_t i = 0; i < _primes[pridx]; ++i) {
        item = items[i];
        while (item != (BoolExprDictItem *) NULL) {
            /* LCOV_EXCL_START */
            if (!_insert(dict, item->key, item->val)) {
                for (size_t j = 0; j < i; ++j)
                    _list_del(items[j]);
                free(items);
                return false;
            }
            /* LCOV_EXCL_STOP */
            item = item->tail;
        }
        _list_del(items[i]);
    }
    free(items);

    return true;
}


bool
BoolExprDict_Insert(BoolExprDict *dict, BoolExpr *key, BoolExpr *val)
{
    double load;

    /* LCOV_EXCL_START */
    if (!_insert(dict, key, val))
        return false;
    /* LCOV_EXCL_STOP */

    load = (double) dict->length / (double) _primes[dict->pridx];

    if (dict->pridx < _MAX_IDX && load > MAX_LOAD) {
        /* LCOV_EXCL_START */
        if (!_enlarge(dict))
            return false;
        /* LCOV_EXCL_STOP */
    }

    return true;
}


bool
BoolExprDict_Remove(BoolExprDict *dict, BoolExpr *key)
{
    size_t index = _hash(dict, key);
    BoolExprDictItem **p = &dict->items[index];
    BoolExprDictItem *item = dict->items[index];

    while (item != (BoolExprDictItem *) NULL) {
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


BoolExpr *
BoolExprDict_Search(BoolExprDict *dict, BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key);
}


bool
BoolExprDict_Contains(BoolExprDict *dict, BoolExpr *key)
{
    size_t index = _hash(dict, key);

    return _list_search(dict->items[index], key) != (BoolExpr *) NULL;
}

