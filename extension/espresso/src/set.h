// Filename: set.h

#include <stdio.h>

bool set_andp(set *r, set *a, set *b);
bool set_orp(set *r, set *a, set *b);
bool setp_disjoint(set *a, set *b);
bool setp_empty(set *a);
bool setp_equal(set *a, set *b);
bool setp_full(set *a, int size);
bool setp_implies(set *a, set *b);
int *sf_count(set_family_t *A);
int *sf_count_restricted(set_family_t *A, set *r);
int bit_index(unsigned int a);
int set_dist(set *a, set *b);
int set_ord(set *a);
void set_adjcnt(set *a, int *count, int weight);

set *set_and(set *r, set *a, set *b);
set *set_clear(set *r, int size);
set *set_copy(set *r, set *a);
set *set_diff(set *r, set *a, set *b);
set *set_fill(set *r, int size);
set *set_merge(set *r, set *a, set *b, set *mask);
set *set_or(set *r, set *a, set *b);
set *set_xor(set *r, set *a, set *b);

set *sf_and(set_family_t *A);
set *sf_or(set_family_t *A);
set_family_t *sf_active(set_family_t *A);
set_family_t *sf_addcol(set_family_t *A, int firstcol, int n);
set_family_t *sf_addset(set_family_t *A, set *s);
set_family_t *sf_append(set_family_t *A, set_family_t *B);
set_family_t *sf_bm_read(FILE *fp);
set_family_t *sf_compress(set_family_t *A, set *c);
set_family_t *sf_copy(set_family_t *R, set_family_t *A);
set_family_t *sf_copy_col(set_family_t *dst, int dstcol, set_family_t *src, int srccol);
set_family_t *sf_delc(set_family_t *A, int first, int last);
set_family_t *sf_delcol(set_family_t *A, int firstcol, int n);
set_family_t *sf_inactive(set_family_t *A);
set_family_t *sf_join(set_family_t *A, set_family_t *B);
set_family_t *sf_new(int num, int size);
set_family_t *sf_permute(set_family_t *A, int *permute, int npermute);
set_family_t *sf_read(FILE *fp);
set_family_t *sf_save(set_family_t *A);
set_family_t *sf_transpose(set_family_t *A);

void set_write(FILE *fp, set *a);
void sf_bm_print(set_family_t *A);
void sf_cleanup(void);
void sf_delset(set_family_t *A, int i);
void sf_free(set_family_t *A);
void sf_print(set_family_t *A);
void sf_write(FILE *fp, set_family_t *A);

int sf_equal(set_family_t *F1, set_family_t *F2);
void print_cover(set_family_t *F, char *name);

