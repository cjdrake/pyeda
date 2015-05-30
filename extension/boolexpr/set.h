/*
** Filename: set.h
*/


#ifndef SET_H
#define SET_H


/* Maximum load allowed before enlargement */
#define MAX_LOAD 1.5

/* Min/Max indices in the primes table */
#define MIN_IDX 4
#define MAX_IDX 30


struct BoolExprSetItem {
    struct BoolExpr *key;
    struct BoolExprSetItem *tail;
};


#endif /* SET_H */

