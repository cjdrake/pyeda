/*
** Filename: share.h
**
** Private functions shared between C files
*/


/* array.c */
struct BX_Array * _bx_array_from(size_t length, struct BoolExpr **items);

/* boolexpr.c */
struct BoolExpr * _bx_op_from(BX_Kind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _op_new(BX_Kind kind, size_t n, struct BoolExpr **xs);
struct BoolExpr * _orandxor_new(BX_Kind kind, size_t n, struct BoolExpr **xs);

/* nnf.c */
struct BoolExpr * _to_nnf(struct BoolExpr *ex);

/* simple.c */
struct BoolExpr * _simplify(struct BoolExpr *ex);

/* util.c */
size_t _uniqid2index(long uniqid);
void _free_exs(int n, struct BoolExpr **exs);
struct BoolExpr * _op_transform(struct BoolExpr *op, struct BoolExpr * (*fn)(struct BoolExpr *));
void _mark_flags(struct BoolExpr *ex, BX_Flags f);
bool _is_clause(struct BoolExpr *op);

