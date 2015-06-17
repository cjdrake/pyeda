/*
** Filename: share.h
**
** Private functions shared between C files
*/


/* array.c */
struct BX_Array * _bx_array_from(size_t length, struct BoolExpr **exprs);

/* boolexpr.c */
extern struct BoolExpr * _bx_identity[16];
extern struct BoolExpr * _bx_dominator[16];

struct BoolExpr * _bx_op_from(BX_Kind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _bx_op_new(BX_Kind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _bx_orandxor_new(BX_Kind kind, size_t n, struct BoolExpr **xs);

/* nnf.c */
struct BoolExpr * _bx_to_nnf(struct BoolExpr *ex);

/* simple.c */
struct BoolExpr * _bx_simplify(struct BoolExpr *ex);

