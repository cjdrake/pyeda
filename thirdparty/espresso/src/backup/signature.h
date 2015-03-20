// Filename: signature.h

/* black_white.c */
void setup_bw();
void free_bw();
int black_white();
void split_list();
void merge_list();
void print_bw();
void variable_list_alloc();
void variable_list_delete();
void variable_list_insert();
int variable_list_empty();
void get_next_variable();
void print_variable_list();

/* canonical.c */
int is_minterm();
set_family_t *find_canonical_cover();

/* essentiality.c */
set_family_t *etr_order();
void aux_etr_order();
set_family_t *get_mins();
int ascending();

/* sigma.c */
set *get_sigma();
void set_not();

/* signature.c */
void cleanup();
set_family_t *signature();
set_family_t *generate_primes();

/* signature_exact.c */
set_family_t *signature_minimize_exact();
sm_matrix *signature_form_table();
