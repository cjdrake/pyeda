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

#define MIN_IDX 4
#define MAX_IDX 30

static size_t _primes[] = {
    0, 0, 0, 0,

    /* (2^4,  2^5)  */ 23,
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


static size_t
_hash(struct BoolExprSet *set, struct BoolExpr *key)
{
    return (size_t) key % _primes[set->_pridx];
}


static bool
_eq(struct BoolExpr *key1, struct BoolExpr *key2)
{
    return key1 == key2;
}


static void
_list_del(struct BoolExprSetItem *list)
{
    if (list) {
        _list_del(list->tail);
        BoolExpr_DecRef(list->key);
        free(list);
    }
}


static bool
_list_contains(struct BoolExprSetItem *list, struct BoolExpr *key)
{
    if (!list)
        return false;

    if (_eq(list->key, key))
        return true;

    return _list_contains(list->tail, key);
}


struct BoolExprSet *
BoolExprSet_New(void)
{
    struct BoolExprSet *set;
    size_t width = _primes[MIN_IDX];

    set = malloc(sizeof(struct BoolExprSet));
    if (set == NULL)
        return NULL; // LCOV_EXCL_LINE

    set->_pridx = MIN_IDX;
    set->length = 0;
    set->items = malloc(width * sizeof(struct BoolExprSetItem *));
    if (set->items == NULL) {
        free(set);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    /* Initialize items to NULL */
    for (size_t i = 0; i < width; ++i)
        set->items[i] = (struct BoolExprSetItem *) NULL;

    return set;
}


void
BoolExprSet_Del(struct BoolExprSet *set)
{
    for (size_t i = 0; i < _primes[set->_pridx]; ++i)
        _list_del(set->items[i]);
    free(set->items);
    free(set);
}


struct BoolExprSetIter *
BoolExprSetIter_New(struct BoolExprSet *set)
{
    struct BoolExprSetIter *it;

    it = malloc(sizeof(struct BoolExprSetIter));
    if (it == NULL)
        return NULL; // LCOV_EXCL_LINE

    it->_set = set;
    it->_item = (struct BoolExprSetItem *) NULL;
    it->done = true;

    for (it->_index = 0; it->_index < _primes[set->_pridx]; it->_index += 1) {
        if (set->items[it->_index]) {
            it->_item = set->items[it->_index];
            it->done = false;
            break;
        }
    }

    return it;
}


void
BoolExprSetIter_Del(struct BoolExprSetIter *it)
{
    free(it);
}


void
BoolExprSetIter_Next(struct BoolExprSetIter *it)
{
    if (it->done)
        return;

    if (it->_item->tail) {
        it->_item = it->_item->tail;
        return;
    }

    for (it->_index += 1; it->_index < _primes[it->_set->_pridx]; it->_index += 1) {
        if (it->_set->items[it->_index]) {
            it->_item = it->_set->items[it->_index];
            return;
        }
    }

    it->done = true;
}


struct BoolExpr *
BoolExprSetIter_Key(struct BoolExprSetIter *it)
{
    return it->_item->key;
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

    item = malloc(sizeof(struct BoolExprSetItem));
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
    size_t pridx = set->_pridx;
    struct BoolExprSetItem **items = set->items;

    set->_pridx += 1;
    set->length = 0;
    set->items = malloc(_primes[set->_pridx] * sizeof(struct BoolExprSetItem *));
    if (set->items == NULL)
        return false; // LCOV_EXCL_LINE

    for (size_t i = 0; i < _primes[set->_pridx]; ++i)
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

    load = (double) set->length / (double) _primes[set->_pridx];

    if (set->_pridx < MAX_IDX && load > MAX_LOAD) {
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
BoolExprSet_EQ(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length != other->length)
        return false;

    struct BoolExprSetItem *item;

    /* All items in self must also be in other (and vice versa) */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BoolExprSet_Contains(other, item->key))
                return false; // LCOV_EXCL_LINE
        }
    }

    return true;
}


bool
BoolExprSet_NE(struct BoolExprSet *self, struct BoolExprSet *other)
{
    return !BoolExprSet_EQ(self, other);
}


bool
BoolExprSet_LTE(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length > other->length)
        return false;

    struct BoolExprSetItem *item;

    /* All items in self must also be in other */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BoolExprSet_Contains(other, item->key))
                return false;
        }
    }

    return true;
}


bool
BoolExprSet_GT(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length <= other->length)
        return false;

    struct BoolExprSetItem *item;

    /* All items in other must also be in self */
    for (size_t i = 0; i < _primes[other->_pridx]; ++i) {
        for (item = other->items[i]; item; item = item->tail) {
            if (!BoolExprSet_Contains(self, item->key))
                return false;
        }
    }

    return true;
}


bool
BoolExprSet_GTE(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length < other->length)
        return false;

    struct BoolExprSetItem *item;

    /* All items in other must also be in self */
    for (size_t i = 0; i < _primes[other->_pridx]; ++i) {
        for (item = other->items[i]; item; item = item->tail) {
            if (!BoolExprSet_Contains(self, item->key))
                return false;
        }
    }

    return true;
}


bool
BoolExprSet_LT(struct BoolExprSet *self, struct BoolExprSet *other)
{
    if (self->length >= self->length)
        return false;

    struct BoolExprSetItem *item;

    /* All items in self must also be in other */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BoolExprSet_Contains(other, item->key))
                return false;
        }
    }

    return true;
}


void
BoolExprSet_Clear(struct BoolExprSet *set)
{
    for (size_t i = 0; i < _primes[set->_pridx]; ++i) {
        if (set->items[i]) {
            _list_del(set->items[i]);
            set->items[i] = (struct BoolExprSetItem *) NULL;
        }
    }

    set->length = 0;
}

