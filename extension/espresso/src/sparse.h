#ifndef SPARSE_H
#define SPARSE_H

#include <stdio.h>

//
// sparse.h -- sparse matrix package header file
//

typedef struct sm_element_struct sm_element;
typedef struct sm_row_struct sm_row;
typedef struct sm_col_struct sm_col;
typedef struct sm_matrix_struct sm_matrix;

//
// sparse matrix element
//
struct sm_element_struct {
    int row_num;            // row number of this element
    int col_num;            // column number of this element
    sm_element *next_row;   // next row in this column
    sm_element *prev_row;   // previous row in this column
    sm_element *next_col;   // next column in this row
    sm_element *prev_col;   // previous column in this row
    char *user_word;        // user-defined word
};

//
// row header
//
struct sm_row_struct {
    int row_num;            // the row number
    int length;             // number of elements in this row
    int flag;               // user-defined word
    sm_element *first_col;  // first element in this row
    sm_element *last_col;   // last element in this row
    sm_row *next_row;       // next row (in sm_matrix linked list)
    sm_row *prev_row;       // previous row (in sm_matrix linked list)
    char *user_word;        // user-defined word
};

//
// column header
//
struct sm_col_struct {
    int col_num;            // the column number
    int length;             // number of elements in this column
    int flag;               // user-defined word
    sm_element *first_row;  // first element in this column
    sm_element *last_row;   // last element in this column
    sm_col *next_col;       // next column (in sm_matrix linked list)
    sm_col *prev_col;       // prev column (in sm_matrix linked list)
    char *user_word;        // user-defined word
};

//
// A sparse matrix
//
struct sm_matrix_struct {
    sm_row **rows;      // pointer to row headers (by row #)
    int rows_size;      // alloc'ed size of above array
    sm_col **cols;      // pointer to column headers (by col #)
    int cols_size;      // alloc'ed size of above array
    sm_row *first_row;  // first row (linked list of all rows)
    sm_row *last_row;   // last row (linked list of all rows)
    int nrows;          // number of rows
    sm_col *first_col;  // first column (linked list of columns)
    sm_col *last_col;   // last column (linked list of columns)
    int ncols;          // number of columns
    char *user_word;    // user-defined word
};

#define sm_get_col(A, colnum)                                                  \
    (((colnum) >= 0 && (colnum) < (A)->cols_size) ?                            \
    (A)->cols[colnum] : (sm_col *) 0)

#define sm_get_row(A, rownum)                                                  \
    (((rownum) >= 0 && (rownum) < (A)->rows_size) ?                            \
    (A)->rows[rownum] : (sm_row *) 0)

#define sm_foreach_row(A, prow)                                                \
    for(prow = A->first_row; prow != 0; prow = prow->next_row)

#define sm_foreach_col(A, pcol)                                                \
    for(pcol = A->first_col; pcol != 0; pcol = pcol->next_col)

#define sm_foreach_row_element(prow, p)                                        \
    for(p = prow->first_col; p != 0; p = p->next_col)

#define sm_foreach_col_element(pcol, p)                                        \
    for(p = pcol->first_row; p != 0; p = p->next_row)

#define sm_put(x, val) (x->user_word = (char *) val)

#define sm_get(type, x) ((type) (x->user_word))

sm_matrix *sm_alloc(void);
sm_matrix *sm_alloc_size(int row, int col);
sm_matrix *sm_dup(sm_matrix *A);
void sm_free(sm_matrix *A);
void sm_delrow(sm_matrix *A, int i);
void sm_delcol(sm_matrix *A, int i);
void sm_resize(sm_matrix *A, int row, int col);
void sm_write(FILE *fp, sm_matrix *A);
void sm_print(FILE *fp, sm_matrix *A);
void sm_dump(sm_matrix *A, char *s, int max);
void sm_cleanup(void);
void sm_copy_row(sm_matrix *dest, int dest_row, sm_row *prow);
void sm_copy_col(sm_matrix *dest, int dest_col, sm_col *pcol);
void sm_remove(sm_matrix *A, int rownum, int colnum);
void sm_remove_element(sm_matrix *A, sm_element *p);
sm_element *sm_insert(sm_matrix *A, int row, int col);
sm_element *sm_find(sm_matrix *A, int rownum, int colnum);
sm_row *sm_longest_row(sm_matrix *A);
sm_col *sm_longest_col(sm_matrix *A);
int sm_read(FILE *fp, sm_matrix **A);
int sm_read_compressed(FILE *fp, sm_matrix **A);

sm_row *sm_row_alloc(void);
sm_row *sm_row_dup(sm_row *prow);
sm_row *sm_row_and(sm_row *p1, sm_row *p2);
void sm_row_free(sm_row *prow);
void sm_row_remove(sm_row *prow, int col);
void sm_row_print(FILE *fp, sm_row *prow);
sm_element *sm_row_insert(sm_row *prow, int col);
sm_element *sm_row_find(sm_row *prow, int col);
int sm_row_contains(sm_row *p1, sm_row *p2);
int sm_row_intersects(sm_row *p1, sm_row *p2);
int sm_row_compare(sm_row *p1, sm_row *p2);
int sm_row_hash(sm_row *prow, int modulus);

sm_col *sm_col_alloc(void);
sm_col *sm_col_dup(sm_col *pcol);
sm_col *sm_col_and(sm_col *p1, sm_col *p2);

void sm_col_free(sm_col *pcol);
void sm_col_remove(sm_col *pcol, int row);
void sm_col_print(FILE *fp, sm_col *pcol);
sm_element *sm_col_insert(sm_col *pcol, int row);
sm_element *sm_col_find(sm_col *pcol, int row);
int sm_col_contains(sm_col *p1, sm_col *p2);
int sm_col_intersects(sm_col *p1, sm_col *p2);

int sm_col_compare(sm_col *p1, sm_col *p2);
int sm_col_hash(sm_col *pcol, int modulus);

// dominate.c
int sm_row_dominance(sm_matrix *A);
int sm_col_dominance(sm_matrix *A, int *weight);

// part.c
int sm_block_partition(sm_matrix *A, sm_matrix **L, sm_matrix **R);

#endif

