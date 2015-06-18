/*
** Filename: set.c
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
_hash(struct BX_Set *set, struct BoolExpr *key)
{
    return (size_t) key % _primes[set->_pridx];
}


static bool
_eq(struct BoolExpr *key1, struct BoolExpr *key2)
{
    return key1 == key2;
}


static void
_list_del(struct BX_SetItem *list)
{
    if (list) {
        _list_del(list->tail);
        BX_DecRef(list->key);
        free(list);
    }
}


static bool
_list_contains(struct BX_SetItem *list, struct BoolExpr *key)
{
    if (!list)
        return false;

    if (_eq(list->key, key))
        return true;

    return _list_contains(list->tail, key);
}


struct BX_Set *
BX_Set_New(void)
{
    struct BX_Set *set;
    size_t width = _primes[MIN_IDX];

    set = malloc(sizeof(struct BX_Set));
    if (set == NULL)
        return NULL; // LCOV_EXCL_LINE

    set->_pridx = MIN_IDX;
    set->length = 0;
    set->items = malloc(width * sizeof(struct BX_SetItem *));
    if (set->items == NULL) {
        free(set);   // LCOV_EXCL_LINE
        return NULL; // LCOV_EXCL_LINE
    }

    /* Initialize items to NULL */
    for (size_t i = 0; i < width; ++i)
        set->items[i] = (struct BX_SetItem *) NULL;

    return set;
}


void
BX_Set_Del(struct BX_Set *set)
{
    for (size_t i = 0; i < _primes[set->_pridx]; ++i)
        _list_del(set->items[i]);
    free(set->items);
    free(set);
}


void
BX_SetIter_Init(struct BX_SetIter *it, struct BX_Set *set)
{
    it->_set = set;
    it->item = (struct BX_SetItem *) NULL;
    it->done = true;

    for (it->_index = 0; it->_index < _primes[set->_pridx]; it->_index += 1) {
        if (set->items[it->_index]) {
            it->item = set->items[it->_index];
            it->done = false;
            break;
        }
    }
}


void
BX_SetIter_Next(struct BX_SetIter *it)
{
    if (it->done)
        return;

    if (it->item->tail) {
        it->item = it->item->tail;
        return;
    }

    for (it->_index += 1; it->_index < _primes[it->_set->_pridx]; it->_index += 1) {
        if (it->_set->items[it->_index]) {
            it->item = it->_set->items[it->_index];
            return;
        }
    }

    it->item = (struct BX_SetItem *) NULL;
    it->done = true;
}


static bool
_set_insert(struct BX_Set *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);
    struct BX_SetItem *item;
    struct BX_SetItem **tail;

    tail = &set->items[index];
    for (item = set->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BX_DecRef(item->key);
            item->key = BX_IncRef(key);
            return true;
        }
        tail = &item->tail;
    }

    item = malloc(sizeof(struct BX_SetItem));
    if (item == NULL)
        return false; // LCOV_EXCL_LINE

    item->key = BX_IncRef(key);
    item->tail = (struct BX_SetItem *) NULL;

    *tail = item;

    set->length += 1;

    return true;
}


static bool
_enlarge(struct BX_Set *set)
{
    struct BX_SetItem *item;

    size_t pridx = set->_pridx;
    size_t length = set->length;
    struct BX_SetItem **items = set->items;

    size_t old_width = _primes[pridx];
    size_t new_width = _primes[pridx + 1];

    set->_pridx += 1;
    set->length = 0;
    set->items = malloc(new_width * sizeof(struct BX_SetItem *));
    if (set->items == NULL)
        return false; // LCOV_EXCL_LINE

    for (size_t i = 0; i < new_width; ++i)
        set->items[i] = (struct BX_SetItem *) NULL;

    for (size_t i = 0; i < old_width; ++i) {
        for (item = items[i]; item; item = item->tail) {
            if (!_set_insert(set, item->key)) {
                /* LCOV_EXCL_START */
                for (size_t j = 0; j < i; ++j)
                    _list_del(set->items[j]);
                free(set->items);
                set->_pridx = pridx;
                set->length = length;
                set->items = items;
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
BX_Set_Insert(struct BX_Set *set, struct BoolExpr *key)
{
    double load;

    if (!_set_insert(set, key))
        return false; // LCOV_EXCL_LINE

    load = (double) set->length / (double) _primes[set->_pridx];

    if (set->_pridx < MAX_IDX && load > MAX_LOAD) {
        if (!_enlarge(set))
            return false; // LCOV_EXCL_LINE
    }

    return true;
}


bool
BX_Set_Remove(struct BX_Set *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);
    struct BX_SetItem *item;
    struct BX_SetItem **tail;

    tail = &set->items[index];
    for (item = set->items[index]; item; item = item->tail) {
        if (_eq(item->key, key)) {
            BX_DecRef(item->key);
            *tail = item->tail;
            free(item);
            set->length -= 1;
            return true;
        }
        tail = &item->tail;
    }

    return false;
}


bool
BX_Set_Contains(struct BX_Set *set, struct BoolExpr *key)
{
    size_t index = _hash(set, key);

    return _list_contains(set->items[index], key);
}


bool
BX_Set_EQ(struct BX_Set *self, struct BX_Set *other)
{
    if (self->length != other->length)
        return false;

    struct BX_SetItem *item;

    /* All items in self must also be in other (and vice versa) */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BX_Set_Contains(other, item->key))
                return false; // LCOV_EXCL_LINE
        }
    }

    return true;
}


bool
BX_Set_NE(struct BX_Set *self, struct BX_Set *other)
{
    return !BX_Set_EQ(self, other);
}


bool
BX_Set_LTE(struct BX_Set *self, struct BX_Set *other)
{
    if (self->length > other->length)
        return false;

    struct BX_SetItem *item;

    /* All items in self must also be in other */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BX_Set_Contains(other, item->key))
                return false;
        }
    }

    return true;
}


bool
BX_Set_GT(struct BX_Set *self, struct BX_Set *other)
{
    if (self->length <= other->length)
        return false;

    struct BX_SetItem *item;

    /* All items in other must also be in self */
    for (size_t i = 0; i < _primes[other->_pridx]; ++i) {
        for (item = other->items[i]; item; item = item->tail) {
            if (!BX_Set_Contains(self, item->key))
                return false;
        }
    }

    return true;
}


bool
BX_Set_GTE(struct BX_Set *self, struct BX_Set *other)
{
    if (self->length < other->length)
        return false;

    struct BX_SetItem *item;

    /* All items in other must also be in self */
    for (size_t i = 0; i < _primes[other->_pridx]; ++i) {
        for (item = other->items[i]; item; item = item->tail) {
            if (!BX_Set_Contains(self, item->key))
                return false;
        }
    }

    return true;
}


bool
BX_Set_LT(struct BX_Set *self, struct BX_Set *other)
{
    if (self->length >= self->length)
        return false;

    struct BX_SetItem *item;

    /* All items in self must also be in other */
    for (size_t i = 0; i < _primes[self->_pridx]; ++i) {
        for (item = self->items[i]; item; item = item->tail) {
            if (!BX_Set_Contains(other, item->key))
                return false;
        }
    }

    return true;
}


void
BX_Set_Clear(struct BX_Set *set)
{
    for (size_t i = 0; i < _primes[set->_pridx]; ++i) {
        if (set->items[i]) {
            _list_del(set->items[i]);
            set->items[i] = (struct BX_SetItem *) NULL;
        }
    }

    set->length = 0;
}


struct BoolExpr **
BX_Set_ToExprs(struct BX_Set *set)
{
    struct BoolExpr **exprs;

    exprs = malloc(set->length * sizeof(struct BoolExpr *));
    if (exprs == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0, index = 0; i < _primes[set->_pridx]; ++i) {
        for (struct BX_SetItem *item = set->items[i]; item; item = item->tail)
            exprs[index++] = item->key;
    }

    return exprs;
}

