/* $Header: st.h,v 1.3 89/05/24 09:31:40 octtools Exp $ */

#ifndef ST_INCLUDED
#define ST_INCLUDED

#include "ansi.h"

extern char st_pkg_name[];

/* Fatal error codes */
#define ST_NO_MEM	0
#define ST_BAD_RET	1
#define ST_BAD_GEN	2

typedef struct _st_table_entry st_table_entry;
struct _st_table_entry {
    char *key;
    char *record;
    st_table_entry *next;
};

typedef struct _st_table st_table;
struct _st_table {
    int (*compare)();
    int (*hash)();
    int num_bins;
    int num_entries;
    int max_density;
    int reorder_flag;
    double grow_factor;
    st_table_entry **bins;
};

typedef struct _st_generator st_generator;
struct _st_generator {
    st_table *table;
    st_table_entry *entry;
    int index;
};

#define st_is_member(table,key) st_lookup(table,key,(char **) 0)
#define st_count(table) ((table)->num_entries)

enum st_retval {ST_CONTINUE, ST_STOP, ST_DELETE};

extern st_table *st_init_table_with_params
  ARGS((int (*compare)(), int (*hash)(), int size, int density,
	double grow_factor, int reorder_flag));

extern st_table *st_init_table
  ARGS((int (*compare)(), int (*hash)()));

extern void st_free_table
  ARGS((st_table *table));

extern int st_lookup
  ARGS((st_table *table, char *key, char **value));

extern int st_insert
  ARGS((st_table *table, char *key, char *value));

extern void st_add_direct
  ARGS((st_table *table, char *key, char *value));

extern int st_find_or_add
  ARGS((st_table *table, char *key, char ***slot));

extern int st_find
  ARGS((st_table *table, char *key, char ***slot));

extern st_table *st_copy
  ARGS((st_table *old_table));

extern int st_delete
  ARGS((st_table *table, char **keyp, char **value));

extern int st_foreach
  ARGS((st_table *table, enum st_retval (*func)(), char *arg));

extern int st_strhash
  ARGS((char *string, int modulus));

extern int st_numhash
  ARGS((char *x, int size));

extern int st_ptrhash
  ARGS((char *x, int size));

extern int st_numcmp
  ARGS((char *x, char *y));

extern int st_ptrcmp
  ARGS((char *x, char *y));

extern st_generator *st_init_gen
  ARGS((st_table *table));

extern int st_gen
  ARGS((st_generator *gen, char **key_p, char **value_p));

extern void st_free_gen
  ARGS((st_generator *gen));

#define ST_DEFAULT_MAX_DENSITY 5
#define ST_DEFAULT_INIT_TABLE_SIZE 11
#define ST_DEFAULT_GROW_FACTOR 2.0
#define ST_DEFAULT_REORDER_FLAG 0

#define st_foreach_item(table, gen, key_p, value_p) \
    for(gen=st_init_gen(table); st_gen(gen,key_p,value_p) || (st_free_gen(gen),0);)

#endif /* ST_INCLUDED */
