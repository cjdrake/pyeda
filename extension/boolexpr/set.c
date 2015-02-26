/*
** Filename: set.c
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


struct _BoolExprSetItem {
    BoolExpr *key;
    BoolExprSetItem *tail;
};


static void
_list_del(BoolExprSetItem *list)
{
    if (list != (BoolExprSetItem *) NULL) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);

        free(list);
    }
}


static bool
_list_contains(BoolExprSetItem *list, BoolExpr *key)
{
    if (list == (BoolExprSetItem *) NULL)
        return false;
    else if (list->key == key)
        return true;
    else
        return _list_contains(list->tail, key);
}


BoolExprSet *
BoolExprSet_New(size_t (*prehash)(BoolExpr *))
{
    BoolExprSet *set;
    size_t pridx = _MIN_IDX;
    size_t width = _primes[pridx];

    set = (BoolExprSet *) malloc(sizeof(BoolExprSet));
    if (set == NULL)
        return NULL; // LCOV_EXCL_LINE

    set->items = (BoolExprSetItem **) malloc(width * sizeof(BoolExprSetItem *));
    if (set->items == NULL) {
        free(set);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    for (size_t i = 0; i < width; ++i)
        set->items[i] = (BoolExprSetItem *) NULL;

    set->prehash = prehash;
    set->length = 0;
    set->pridx = pridx;

    return set;
}


static size_t
_var2int(BoolExpr *var)
{
    return (size_t) (var->data.lit.uniqid - 1);
}


BoolExprSet *
BoolExprVarSet_New(void)
{
    return BoolExprSet_New(_var2int);
}


static size_t
_lit2int(BoolExpr *lit)
{
    return (size_t) (lit->data.lit.uniqid < 0 ? -2 * lit->data.lit.uniqid - 2
                                              :  2 * lit->data.lit.uniqid - 1);
}


BoolExprSet *
BoolExprLitSet_New(void)
{
    return BoolExprSet_New(_lit2int);
}


void
BoolExprSet_Del(BoolExprSet *set)
{
    for (size_t i = 0; i < _primes[set->pridx]; ++i)
        _list_del(set->items[i]);

    free(set->items);
    free(set);
}


static size_t
_hash(BoolExprSet *set, BoolExpr *key)
{
    return set->prehash(key) % _primes[set->pridx];
}


static bool
_insert(BoolExprSet *set, BoolExpr *key)
{
    size_t index = _hash(set, key);;
    BoolExprSetItem *item = set->items[index];

    while (item != (BoolExprSetItem *) NULL) {
        if (item->key == key) {
            BoolExpr_DecRef(item->key);
            item->key = BoolExpr_IncRef(key);
            return true;
        }
        item = item->tail;
    }

    item = (BoolExprSetItem *) malloc(sizeof(BoolExprSetItem));
    if (item == NULL)
        return false; // LCOV_EXCL_LINE

    item->key = BoolExpr_IncRef(key);
    item->tail = set->items[index];

    set->items[index] = item;
    set->length += 1;

    return true;
}


static bool
_enlarge(BoolExprSet *set)
{
    BoolExprSetItem *item;

    size_t pridx = set->pridx;
    BoolExprSetItem **items = set->items;

    set->length = 0;
    set->pridx += 1;
    set->items = (BoolExprSetItem **) malloc(_primes[set->pridx] * sizeof(BoolExprSetItem *));
    for (size_t i = 0; i < _primes[set->pridx]; ++i)
        set->items[i] = (BoolExprSetItem *) NULL;

    for (size_t i = 0; i < _primes[pridx]; ++i) {
        item = items[i];
        while (item != (BoolExprSetItem *) NULL) {
            if (!_insert(set, item->key)) {
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
BoolExprSet_Insert(BoolExprSet *set, BoolExpr *key)
{
    double load;

    if (!_insert(set, key))
        return false; // LCOV_EXCL_LINE

    load = (double) set->length / (double) _primes[set->pridx];

    if (set->pridx < _MAX_IDX && load > MAX_LOAD) {
        if (!_enlarge(set))
            return false; // LCOV_EXCL_LINE
    }

    return true;
}


bool
BoolExprSet_Remove(BoolExprSet *set, BoolExpr *key)
{
    size_t index = _hash(set, key);
    BoolExprSetItem **p = &set->items[index];
    BoolExprSetItem *item = set->items[index];

    while (item != (BoolExprSetItem *) NULL) {
        if (item->key == key) {
            BoolExpr_DecRef(item->key);
            *p = item->tail;
            free(item);
            set->length -= 1;

            return true;
        }

        p = &item->tail;
        item = item->tail;
    }

    return false;
}


bool
BoolExprSet_Contains(BoolExprSet *set, BoolExpr *key)
{
    size_t index = _hash(set, key);

    return _list_contains(set->items[index], key);
}

