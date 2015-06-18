/*
** Filename: util.h
*/


void _bx_free_exprs(int length, struct BoolExpr **exprs);

struct BoolExpr * _bx_op_transform(struct BoolExpr *op,
                                   struct BoolExpr * (*fn)(struct BoolExpr *));

void _bx_mark_flags(struct BoolExpr *ex, BX_Flags f);

bool _bx_is_clause(struct BoolExpr *op);

