/*
** Filename: boolexpr.h
*/


#ifndef BOOLEXPR_H
#define BOOLEXPR_H


#ifdef __cplusplus
extern "C" {
#endif


/* Kind checks */
#define BX_IS_ZERO(ex)  (((ex)->kind) == BX_ZERO)
#define BX_IS_ONE(ex)   (((ex)->kind) == BX_ONE)
#define BX_IS_COMP(ex)  (((ex)->kind) == BX_COMP)
#define BX_IS_VAR(ex)   (((ex)->kind) == BX_VAR)
#define BX_IS_OR(ex)    (((ex)->kind) == BX_OP_OR)
#define BX_IS_AND(ex)   (((ex)->kind) == BX_OP_AND)
#define BX_IS_XOR(ex)   (((ex)->kind) == BX_OP_XOR)
#define BX_IS_EQ(ex)    (((ex)->kind) == BX_OP_EQ)
#define BX_IS_NOT(ex)   (((ex)->kind) == BX_OP_NOT)
#define BX_IS_IMPL(ex)  (((ex)->kind) == BX_OP_IMPL)
#define BX_IS_ITE(ex)   (((ex)->kind) == BX_OP_ITE)

#define BX_IS_NOR(ex)   (BX_IS_NOT(ex) && BX_IS_OR(ex->data.xs->items[0]))
#define BX_IS_NAND(ex)  (BX_IS_NOT(ex) && BX_IS_AND(ex->data.xs->items[0]))
#define BX_IS_XNOR(ex)  (BX_IS_NOT(ex) && BX_IS_XOR(ex->data.xs->items[0]))
#define BX_IS_UNEQ(ex)  (BX_IS_NOT(ex) && BX_IS_EQ(ex->data.xs->items[0]))


/* Category checks */
#define BX_IS_ATOM(ex)   (((ex)->kind) >> 3 == 0x0) // 0***
#define BX_IS_CONST(ex)  (((ex)->kind) >> 2 == 0x0) // 00**
#define BX_IS_LIT(ex)    (((ex)->kind) >> 1 == 0x2) // 010*
#define BX_IS_OP(ex)     (((ex)->kind) >> 3 == 0x1) // 1***


/* Flag definitions */
#define BX_SIMPLE 0x01
#define BX_NNF    0x02


/* Flag checks */
#define BX_IS_SIMPLE(ex) (((ex)->flags) & BX_SIMPLE)
#define BX_IS_NNF(ex)    (((ex)->flags) & BX_NNF)


/* Expression types */
typedef enum {
    BX_ZERO = 0x00,
    BX_ONE  = 0x01,

    BX_LOGICAL   = 0x02,
    BX_ILLOGICAL = 0x03,

    BX_COMP = 0x04,
    BX_VAR  = 0x05,

    BX_OP_OR  = 0x08,
    BX_OP_AND = 0x09,
    BX_OP_XOR = 0x0A,
    BX_OP_EQ  = 0x0B,

    BX_OP_NOT  = 0x0C,
    BX_OP_IMPL = 0x0D,
    BX_OP_ITE  = 0x0E,
} BX_Kind;


/* Expression flags */
typedef unsigned char BX_Flags;


struct BoolExpr {
    int refcount;

    BX_Kind kind;
    BX_Flags flags;

    union {
        /* constant */
        unsigned int pcval;

        /* literal */
        struct {
            struct BX_Vector *lits;
            long uniqid;
        } lit;

        /* operator */
        struct BX_Array *xs;
    } data;
};


struct BX_Iter {
    struct BoolExpr *_ex;
    size_t _index;
    struct BX_Iter *_it;

    struct BoolExpr *item;
    bool done;
};


struct BX_Array {
    size_t length;
    struct BoolExpr **items;
};


struct BX_Vector {
    size_t length;
    size_t capacity;
    struct BoolExpr **items;
};


struct BX_DictItem {
    struct BoolExpr *key;
    struct BoolExpr *val;
    struct BX_DictItem *tail;
};


struct BX_Dict {
    size_t _pridx;

    size_t length;
    struct BX_DictItem **items;
};


struct BX_DictIter {
    struct BX_Dict *_dict;
    size_t _index;

    struct BX_DictItem *item;
    bool done;
};


struct BX_SetItem {
    struct BoolExpr *key;
    struct BX_SetItem *tail;
};


struct BX_Set {
    size_t _pridx;

    size_t length;
    struct BX_SetItem **items;
};


struct BX_SetIter {
    struct BX_Set *_set;
    size_t _index;

    struct BX_SetItem *item;
    bool done;
};


struct BX_OrAndArgSet {
    BX_Kind kind;
    bool min;
    bool max;
    struct BX_Set *xs;
};


struct BX_XorArgSet {
    bool parity;
    struct BX_Set *xs;
};


struct BX_EqArgSet {
    bool zero;
    bool one;
    struct BX_Set *xs;
};


/* Constant expressions */
extern struct BoolExpr BX_Zero;
extern struct BoolExpr BX_One;
extern struct BoolExpr BX_Logical;
extern struct BoolExpr BX_Illogical;


/*
** Return a literal expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_Literal(struct BX_Vector *lits, long uniqid);


/*
** Return an operator expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_Or(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Nor(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_And(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Nand(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Xor(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Xnor(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Equal(size_t n, struct BoolExpr **xs);
struct BoolExpr * BX_Unequal(size_t n, struct BoolExpr **xs);

struct BoolExpr * BX_Not(struct BoolExpr *x);
struct BoolExpr * BX_Implies(struct BoolExpr *p, struct BoolExpr *q);
struct BoolExpr * BX_ITE(struct BoolExpr *s, struct BoolExpr *d1, struct BoolExpr *d0);

struct BoolExpr * BX_OrN(size_t n, ...);
struct BoolExpr * BX_NorN(size_t n, ...);
struct BoolExpr * BX_AndN(size_t n, ...);
struct BoolExpr * BX_NandN(size_t n, ...);
struct BoolExpr * BX_XorN(size_t n, ...);
struct BoolExpr * BX_XnorN(size_t n, ...);
struct BoolExpr * BX_EqualN(size_t n, ...);
struct BoolExpr * BX_UnequalN(size_t n, ...);


/*
** Increment the reference count of an expression.
*/
struct BoolExpr * BX_IncRef(struct BoolExpr *);


/*
** Decrement the reference count of an expression.
*/
void BX_DecRef(struct BoolExpr *);


/* Return the support set of an expression. */
struct BX_Set * BX_Support(struct BoolExpr *);


/*
** Return the depth of an expression tree.
**
** 1. An atom node (constant or literal) has zero depth.
** 2. A branch node (operator) has depth equal to the maximum depth of
**    its children (arguments) plus one.
*/
unsigned long BX_Depth(struct BoolExpr *);


/*
** Return the size of an expression tree.
**
** 1. An atom node (constant or literal) has size one.
** 2. A branch node (operator) has size equal to the sum of its children's
**    sizes plus one.
*/
unsigned long BX_Size(struct BoolExpr *);


/* Return the number of atoms in an expression tree. */
unsigned long BX_AtomCount(struct BoolExpr *);


/* Return the number of operators in an expression tree. */
unsigned long BX_OpCount(struct BoolExpr *);


/* Return true if the expression is in disjunctive normal form. */
bool BX_IsDNF(struct BoolExpr *);

/* Return true if the expression is in conjunctive normal form. */
bool BX_IsCNF(struct BoolExpr *);


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
struct BoolExpr * BX_PushDownNot(struct BoolExpr *);


/*
** Return a simplified expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_Simplify(struct BoolExpr *);


/*
** Convert all N-ary operators to binary operators.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_ToBinary(struct BoolExpr *);


/*
** Return an expression in negation normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_ToNNF(struct BoolExpr *);


/*
** Return an expression in disjunctive normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_ToDNF(struct BoolExpr *);


/*
** Return an expression in conjunctive normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_ToCNF(struct BoolExpr *);


/*
** Return a DNF expression that contains all prime implicants.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_CompleteSum(struct BoolExpr *);


/*
** Substitute a subset of support variables with other Boolean expressions.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_Compose(struct BoolExpr *, struct BX_Dict *var2ex);


/*
** Restrict a subset of support variables to {0, 1}
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BX_Restrict(struct BoolExpr *, struct BX_Dict *var2const);


/* Return a new Boolean expression iterator. */
struct BX_Iter * BX_Iter_New(struct BoolExpr *ex);

/* Delete a Boolean expression iterator. */
void BX_Iter_Del(struct BX_Iter *);

/* Return the next Boolean expression in an iteration. */
bool BX_Iter_Next(struct BX_Iter *);


/* Return a new array of Boolean expressions. */
struct BX_Array * BX_Array_New(size_t length, struct BoolExpr **exprs);

/* Delete an array of Boolean expressions. */
void BX_Array_Del(struct BX_Array *);

/* Return true if two arrays are equal. */
bool BX_Array_Equal(struct BX_Array *, struct BX_Array *);

/* Return the cartesian product of N arrays */
struct BX_Array * BX_Product(BX_Kind kind, size_t length, struct BX_Array **);


/*
** Return a new vector of Boolean expressions.
**
** All items will be initialized to NULL.
*/
struct BX_Vector * BX_Vector_New(void);

/* Delete a vector of Boolean expressions. */
void BX_Vector_Del(struct BX_Vector *);

bool BX_Vector_Insert(struct BX_Vector *, size_t index, struct BoolExpr *ex);

bool BX_Vector_Append(struct BX_Vector *, struct BoolExpr *ex);


/*
** Return a new dictionary of Boolean expressions.
*/
struct BX_Dict * BX_Dict_New(void);

/* Delete a dictionary of Boolean expressions. */
void BX_Dict_Del(struct BX_Dict *);

/* Insert an expression into the dictionary. */
bool BX_Dict_Insert(struct BX_Dict *, struct BoolExpr *key, struct BoolExpr *val);

/* Remove an expression from the dictionary. */
bool BX_Dict_Remove(struct BX_Dict *, struct BoolExpr *key);

/* If the dict contains the key, return its value. */
struct BoolExpr * BX_Dict_Search(struct BX_Dict *, struct BoolExpr *key);

/* Return true if the dict contains the key. */
bool BX_Dict_Contains(struct BX_Dict *, struct BoolExpr *key);

/* Remove all items from the dict. */
void BX_Dict_Clear(struct BX_Dict *);

/* Return true if two dicts are equal. */
bool BX_Dict_Equal(struct BX_Dict *, struct BX_Dict *);

bool BX_Dict_Update(struct BX_Dict *, struct BX_Dict *);

/*
** Initialize a Boolean expression set iterator.
*/
void BX_DictIter_Init(struct BX_DictIter *, struct BX_Dict *);

/* Move to the next item in the set iteration. */
void BX_DictIter_Next(struct BX_DictIter *);


/*
** Return a new set of Boolean expressions.
*/
struct BX_Set * BX_Set_New(void);

/* Delete a set of Boolean expressions. */
void BX_Set_Del(struct BX_Set *);

/*
** Initialize a Boolean expression set iterator.
*/
void BX_SetIter_Init(struct BX_SetIter *, struct BX_Set *);

/* Move to the next item in the set iteration. */
void BX_SetIter_Next(struct BX_SetIter *);

/* Insert an expression into the set. */
bool BX_Set_Insert(struct BX_Set *, struct BoolExpr *key);

/* Remove an expression from the set. */
bool BX_Set_Remove(struct BX_Set *, struct BoolExpr *key);

/* Return true if the set contains the key. */
bool BX_Set_Contains(struct BX_Set *, struct BoolExpr *key);

/* Set comparison operators */
bool BX_Set_EQ(struct BX_Set *, struct BX_Set *);
bool BX_Set_NE(struct BX_Set *, struct BX_Set *);
bool BX_Set_LTE(struct BX_Set *, struct BX_Set *);
bool BX_Set_GT(struct BX_Set *, struct BX_Set *);
bool BX_Set_GTE(struct BX_Set *, struct BX_Set *);
bool BX_Set_LT(struct BX_Set *, struct BX_Set *);

bool BX_Set_Update(struct BX_Set *, struct BX_Set *);

/* Remove all items from the set. */
void BX_Set_Clear(struct BX_Set *);

/* Convert the set to a simple array of expressions */
struct BoolExpr **
BX_Set_ToExprs(struct BX_Set *);


/*
** Return a new OR/AND set
*/
struct BX_OrAndArgSet * BX_OrAndArgSet_New(BX_Kind kind);

void BX_OrAndArgSet_Del(struct BX_OrAndArgSet *);

bool BX_OrAndArgSet_Insert(struct BX_OrAndArgSet *, struct BoolExpr *key);

struct BoolExpr * BX_OrAndArgSet_Reduce(struct BX_OrAndArgSet *);


/*
** Return a new XOR/XNOR set
*/
struct BX_XorArgSet * BX_XorArgSet_New(bool parity);

void BX_XorArgSet_Del(struct BX_XorArgSet *);

bool BX_XorArgSet_Insert(struct BX_XorArgSet *, struct BoolExpr *key);

struct BoolExpr * BX_XorArgSet_Reduce(struct BX_XorArgSet *);


/*
** Return a new Equal set
*/
struct BX_EqArgSet * BX_EqArgSet_New(void);

void BX_EqArgSet_Del(struct BX_EqArgSet *);

bool BX_EqArgSet_Insert(struct BX_EqArgSet *, struct BoolExpr *key);

struct BoolExpr * BX_EqArgSet_Reduce(struct BX_EqArgSet *);


#ifdef __cplusplus
}
#endif


#endif /* BOOLEXPR_H */

