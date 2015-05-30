/*
** Filename: dict.h
*/


#ifndef DICT_H
#define DICT_H


/* Maximum load allowed before enlargement */
#define MAX_LOAD 1.5

/* Min/Max indices in the primes table */
#define MIN_IDX 4
#define MAX_IDX 30


struct BoolExprDictItem {
    struct BoolExpr *key;
    struct BoolExpr *val;
    struct BoolExprDictItem *tail;
};


#endif /* DICT_H */

