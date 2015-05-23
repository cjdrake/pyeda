/*
** Filename: set.c
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


struct BoolExprSetItem {
    struct BoolExpr *key;
    struct BoolExprSetItem *tail;
};


static size_t
_hash(struct BoolExprSet *set, struct BoolExpr *key)
{
    return (size_t) key % _primes[set->pridx];
}


static bool
_eq(struct BoolExpr *key1, struct BoolExpr *key2)
{
    return key1 == key2;
}


static void
_list_del(struct BoolExprSetItem *list)
{
    if (list != (struct BoolExprSetItem *) NULL) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);

        free(list);
    }
}


static bool
_list_contains(struct BoolExprSetItem *list, struct BoolExpr *key)
{
    if (list == (struct BoolExprSetItem *) NULL)
        return false;
    else if (_eq(list->key, key))
        return true;
    else
        return _list_contains(list->tail, key);
}


struct BoolExprSet *
BoolExprSet_New(void)
{
    struct BoolExprSet *set;
    size_t pridx = _MIN_IDX;
    size_t width = _primes[pridx];

    set = (struct BoolExprSet *) malloc(sizeof(struct BoolExprSet));
    if (set == NULL)
        return NULL; // LCOV_EXCL_LINE

    set->items = (struct BoolExprSetItem **) malloc(width * sizeof(struct BoolExprSetItem *));
    if (set->items == NULL) {
        free(set);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    for (size_t i = 0; i < width; ++i)
        set->items[i] = (struct BoolExprSetItem *) NULL;

    set->length = 0;
    set->pridx = pridx;

    return set;
}


void
BoolExprSet_Del(struct BoolExprSet *set)
{
    for (size_t i = 0; i < _primes[set->pridx]; ++i)
        _list_del(set->items[i]);

    free(set->items);
    free(set);
}


static bool
_insert(struct BoolExprSet *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);

    struct BoolExprSetItem *item;

    for (item = set->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BoolExpr_DecRef(item->key);
            item->key = BoolExpr_IncRef(key);
            return true;
        }
    }

    item = (struct BoolExprSetItem *) malloc(sizeof(struct BoolExprSetItem));
    if (item == NULL)
        return false; // LCOV_EXCL_LINE

    item->key = BoolExpr_IncRef(key);
    item->tail = set->items[index];

    set->items[index] = item;
    set->length += 1;

    return true;
}


static bool
_enlarge(struct BoolExprSet *set)
{
    struct BoolExprSetItem *item;

    size_t pridx = set->pridx;
    struct BoolExprSetItem **items = set->items;

    set->length = 0;
    set->pridx += 1;
    set->items = (struct BoolExprSetItem **) malloc(_primes[set->pridx] * sizeof(struct BoolExprSetItem *));
    for (size_t i = 0; i < _primes[set->pridx]; ++i)
        set->items[i] = (struct BoolExprSetItem *) NULL;

    for (size_t i = 0; i < _primes[pridx]; ++i) {
        for (item = items[i]; item; item = item->tail) {
            if (!_insert(set, item->key)) {
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
BoolExprSet_Insert(struct BoolExprSet *set, struct BoolExpr *key)
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
BoolExprSet_Remove(struct BoolExprSet *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);

    struct BoolExprSetItem **p = &set->items[index];
    struct BoolExprSetItem *item = set->items[index];

    while (item) {
        if (_eq(item->key, key)) {
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
BoolExprSet_Contains(struct BoolExprSet *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);

    return _list_contains(set->items[index], key);
}


bool
BoolExprSet_Equal(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length != other->length)
        return false;

    struct BoolExprSetItem *item;

    for (size_t i = 0; i < _primes[self->pridx]; ++i)
        for (item = self->items[i]; item; item = item->tail)
            if (!BoolExprSet_Contains(other, item->key))
                return false;

    return true;
}


void
BoolExprSet_Clear(struct BoolExprSet *set)
{
    for (size_t i = 0; i < _primes[set->pridx]; ++i) {
        if (set->items[i] != (struct BoolExprSetItem *) NULL) {
            _list_del(set->items[i]);
            set->items[i] = (struct BoolExprSetItem *) NULL;
        }
    }

    set->length = 0;
}

