/*
** Filename: boolexpr.h
*/


#ifndef BOOLEXPR_H
#define BOOLEXPR_H


#ifdef __cplusplus
extern "C" {
#endif


/* bool, false, true */
#include <stdbool.h>

/* size_t */
#include <stddef.h>

/* NULL, malloc, realloc, free, labs */
#include <stdlib.h>


#define CHECK_NULL(y, x) \
do { \
    if ((y = x) == NULL) \
        return NULL; \
} while (0)


#define CHECK_NULL_1(y, x, temp) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(temp); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_2(y, x, t0, t1) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(t0); \
        BoolExpr_DecRef(t1); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_3(y, x, t0, t1, t2) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(t0); \
        BoolExpr_DecRef(t1); \
        BoolExpr_DecRef(t2); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_N(y, x, n, temps) \
do { \
    if ((y = x) == NULL) { \
        for (size_t i = 0; i < n; ++i) \
            BoolExpr_DecRef(temps[i]); \
        return NULL; \
    } \
} while (0)


/* Type checks */
#define IS_ZERO(ex)  (((ex)->type) == ZERO)
#define IS_ONE(ex)   (((ex)->type) == ONE)
#define IS_COMP(ex)  (((ex)->type) == COMP)
#define IS_VAR(ex)   (((ex)->type) == VAR)
#define IS_OR(ex)    (((ex)->type) == OP_OR)
#define IS_AND(ex)   (((ex)->type) == OP_AND)
#define IS_XOR(ex)   (((ex)->type) == OP_XOR)
#define IS_EQ(ex)    (((ex)->type) == OP_EQ)
#define IS_NOT(ex)   (((ex)->type) == OP_NOT)
#define IS_IMPL(ex)  (((ex)->type) == OP_IMPL)
#define IS_ITE(ex)   (((ex)->type) == OP_ITE)


/* Category checks */
#define IS_ATOM(ex)   (((ex)->type) >> 3 == 0x0) // 0000_0***
#define IS_CONST(ex)  (((ex)->type) >> 2 == 0x0) // 0000_00**
#define IS_LIT(ex)    (((ex)->type) >> 1 == 0x2) // 0000_010*
#define IS_OP(ex)     (((ex)->type) >> 3 == 0x1) // 0000_1***


/* Flag definitions */
#define SIMPLE 0x01
#define NNF    0x02


/* Flag checks */
#define IS_SIMPLE(ex) (((ex)->flags) & SIMPLE)
#define IS_NNF(ex)    (((ex)->flags) & NNF)


/* Other */
#define COMPLEMENTARY(x, y) \
    (IS_LIT(x) && IS_LIT(y) && \
     ((x)->data.lit.uniqid == -((y)->data.lit.uniqid)))

#define DUAL(t) (OP_OR + OP_AND - t)


/* Boolean expression definition */
typedef struct _BoolExpr BoolExpr;


/* Expression types */
typedef enum {
    ZERO = 0x00,
    ONE  = 0x01,

    LOGICAL   = 0x02,
    ILLOGICAL = 0x03,

    COMP = 0x04,
    VAR  = 0x05,

    OP_OR  = 0x08,
    OP_AND = 0x09,
    OP_XOR = 0x0A,
    OP_EQ  = 0x0B,

    OP_NOT  = 0x0C,
    OP_IMPL = 0x0D,
    OP_ITE  = 0x0E,
} BoolExprType;


/* Expression flags */
typedef unsigned char BoolExprFlags;


/* Array(s) of expressions */
typedef struct _BoolExprArray BoolExprArray;
typedef struct _BoolExprArray2 BoolExprArray2;


/* Vector of expressions */
typedef struct _BoolExprVector BoolExprVector;


/* Dict of expressions */
typedef struct _BoolExprDictItem BoolExprDictItem;
typedef struct _BoolExprDict BoolExprDict;


/* Set of expressions */
typedef struct _BoolExprSetItem BoolExprSetItem;
typedef struct _BoolExprSet BoolExprSet;


/* Expression iterator */
typedef struct _BoolExprIter BoolExprIter;


struct _BoolExpr {
    int refcount;

    BoolExprType type;

    union {
        /* constant */
        unsigned int pcval;

        /* literal */
        struct {
            BoolExprVector *lits;
            long uniqid;
        } lit;

        /* operator */
        BoolExprArray *xs;
    } data;

    BoolExprFlags flags;
};


struct _BoolExprArray {
    size_t length;
    BoolExpr **items;
};


struct _BoolExprArray2 {
    size_t length;
    BoolExprArray **items;
};


struct _BoolExprVector {
    size_t length;
    size_t capacity;
    BoolExpr **items;
};


struct _BoolExprDict {
    size_t (*prehash)(BoolExpr *);
    size_t length;
    size_t pridx;
    BoolExprDictItem **items;
};


struct _BoolExprSet {
    size_t (*prehash)(BoolExpr *);
    size_t length;
    size_t pridx;
    BoolExprSetItem **items;
};


struct _BoolExprIter {
    bool done;
    BoolExpr *ex;
    size_t index;
    BoolExprIter *it;
};


/* Return a new array of Boolean expressions. */
BoolExprArray * BoolExprArray_New(size_t length, BoolExpr **items);

/* Delete an array of Boolean expressions. */
void BoolExprArray_Del(BoolExprArray *);

/* Return true if two arrays are equal. */
bool BoolExprArray_Equal(BoolExprArray *, BoolExprArray *);


/* Return a new 2d array of Boolean expressions. */
BoolExprArray2 * BoolExprArray2_New(size_t length, size_t *lengths, BoolExpr ***items);

/* Delete a two-dimensional array of Boolean expressions. */
void BoolExprArray2_Del(BoolExprArray2 *);

/* Return true if two 2d arrays are equal. */
bool BoolExprArray2_Equal(BoolExprArray2 *, BoolExprArray2 *);

/* Return the cartesian product of two 2d arrays */
BoolExprArray * BoolExprArray2_Product(BoolExprArray2 *, BoolExprType t);


/*
** Return a new vector of Boolean expressions.
**
** All items will be initialized to NULL.
*/
BoolExprVector * BoolExprVector_New(void);

/* Delete a vector of Boolean expressions. */
void BoolExprVector_Del(BoolExprVector *);

bool BoolExprVector_Insert(BoolExprVector *, size_t index, BoolExpr *ex);

bool BoolExprVector_Append(BoolExprVector *, BoolExpr *ex);


/*
** Return a new dictionary of Boolean expressions.
*/
BoolExprDict * BoolExprDict_New(size_t (*prehash)(BoolExpr *));

/* Return a mapping from variables to arbitrary expressions. */
BoolExprDict * BoolExprVarMap_New(void);

/* Return a mapping from literals to arbitrary expressions. */
BoolExprDict * BoolExprLitMap_New(void);

/* Delete a dictionary of Boolean expressions. */
void BoolExprDict_Del(BoolExprDict *);

/* Insert an expression into the dictionary. */
bool BoolExprDict_Insert(BoolExprDict *, BoolExpr *key, BoolExpr *val);

/* Delete an expression from the dictionary. */
bool BoolExprDict_Remove(BoolExprDict *, BoolExpr *key);

BoolExpr * BoolExprDict_Search(BoolExprDict *, BoolExpr *key);

bool BoolExprDict_Contains(BoolExprDict *, BoolExpr *key);


/*
** Return a new set of Boolean expressions.
*/
BoolExprSet * BoolExprSet_New(size_t (*prehash)(BoolExpr *));

/* Return a set of variables */
BoolExprSet * BoolExprVarSet_New(void);

/* Return a set of literals */
BoolExprSet * BoolExprLitSet_New(void);

void BoolExprSet_Del(BoolExprSet *);

bool BoolExprSet_Insert(BoolExprSet *, BoolExpr *key);

bool BoolExprSet_Remove(BoolExprSet *, BoolExpr *key);

bool BoolExprSet_Contains(BoolExprSet *, BoolExpr *key);


/* Return a new Boolean expression iterator. */
BoolExprIter * BoolExprIter_New(BoolExpr *ex);

/* Delete a Boolean expression iterator. */
void BoolExprIter_Del(BoolExprIter *);

/* Return the next Boolean expression in an iteration. */
BoolExpr * BoolExprIter_Next(BoolExprIter *);


/* Constant expressions */
extern BoolExpr Zero;
extern BoolExpr One;
extern BoolExpr Logical;
extern BoolExpr Illogical;

extern BoolExpr * IDENTITY[16];
extern BoolExpr * DOMINATOR[16];


/*
** Return a literal expression.
**
** NOTE: Returns a new reference.
*/
BoolExpr * Literal(BoolExprVector *lits, long uniqid);


/*
** Return an operator expression.
**
** NOTE: Returns a new reference.
*/
BoolExpr * Or(size_t n, BoolExpr **xs);
BoolExpr * Nor(size_t n, BoolExpr **xs);
BoolExpr * And(size_t n, BoolExpr **xs);
BoolExpr * Nand(size_t n, BoolExpr **xs);
BoolExpr * Xor(size_t n, BoolExpr **xs);
BoolExpr * Xnor(size_t n, BoolExpr **xs);
BoolExpr * Equal(size_t n, BoolExpr **xs);
BoolExpr * Unequal(size_t n, BoolExpr **xs);

BoolExpr * OrN(size_t n, ...);
BoolExpr * NorN(size_t n, ...);
BoolExpr * AndN(size_t n, ...);
BoolExpr * NandN(size_t n, ...);
BoolExpr * XorN(size_t n, ...);
BoolExpr * XnorN(size_t n, ...);
BoolExpr * EqualN(size_t n, ...);
BoolExpr * UnequalN(size_t n, ...);

BoolExpr * Not(BoolExpr *x);
BoolExpr * Implies(BoolExpr *p, BoolExpr *q);
BoolExpr * ITE(BoolExpr *s, BoolExpr *d1, BoolExpr *d0);


/*
** Increment the reference count of an expression.
*/
BoolExpr * BoolExpr_IncRef(BoolExpr *);


/*
** Decrement the reference count of an expression.
*/
void BoolExpr_DecRef(BoolExpr *);


/*
** Return the depth of an expression tree.
**
** 1. An atom node (constant or literal) has zero depth.
** 2. A branch node (operator) has depth equal to the maximum depth of
**    its children (arguments) plus one.
*/
unsigned long BoolExpr_Depth(BoolExpr *);


/*
** Return the size of an expression tree.
**
** 1. An atom node (constant or literal) has size one.
** 2. A branch node (operator) has size equal to the sum of its children's
**    sizes plus one.
*/
unsigned long BoolExpr_Size(BoolExpr *);


/* Return the number of atomic nodes in an expression tree. */
unsigned long BoolExpr_AtomCount(BoolExpr *);


/* Return the number of operators in an expression tree. */
unsigned long BoolExpr_OpCount(BoolExpr *);


/* Return true if the expression is in disjunctive normal form. */
bool BoolExpr_IsDNF(BoolExpr *);

/* Return true if the expression is in conjunctive normal form. */
bool BoolExpr_IsCNF(BoolExpr *);


/*
** Return an expression with NOT operators pushed down through dual operators.
**
** Specifically, perform the following transformations:
**     ~(a | b | c ...) <=> ~a & ~b & ~c ...
**     ~(a & b & c ...) <=> ~a | ~b | ~c ...
**     ~(s ? d1 : d0) <=> s ? ~d1 : ~d0
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_PushDownNot(BoolExpr *);


/*
** Return a simplified expression.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_Simplify(BoolExpr *);


/*
** Convert all N-ary operators to binary operators.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_ToBinary(BoolExpr *ex);


/*
** Return an expression in negation normal form.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_ToNNF(BoolExpr *);


/*
** Return an expression in disjunctive normal form.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_ToDNF(BoolExpr *);


/*
** Return an expression in conjunctive normal form.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_ToCNF(BoolExpr *);


/*
** Return a DNF expression that contains all prime implicants.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_CompleteSum(BoolExpr *);


/*
** Substitute a subset of support variables with other Boolean expressions.
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_Compose(BoolExpr *, BoolExprDict *var2ex);


/*
** Restrict a subset of support variables to {0, 1}
**
** NOTE: Returns a new reference.
*/
BoolExpr * BoolExpr_Restrict(BoolExpr *, BoolExprDict *var2const);


#ifdef __cplusplus
}
#endif


#endif /* BOOLEXPR_H */

