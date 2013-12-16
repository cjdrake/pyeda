#if BPI == 16
#define ODD_MASK 0xaaaa
#define EVEN_MASK 0x5555
#else
#define ODD_MASK 0xaaaaaaaa
#define EVEN_MASK 0x55555555
#endif

#define POSITIVE 1
#define NEGATIVE 0

#define PRESENT 1
#define ABSENT 0

#define RAISED 2

/* black_white.c */ int setup_bw();
/* black_white.c */ int free_bw();
/* black_white.c */ int black_white();
/* black_white.c */ int split_list();
/* black_white.c */ int merge_list();
/* black_white.c */ int print_bw();
/* black_white.c */ int variable_list_alloc();
/* black_white.c */ int variable_list_init();
/* black_white.c */ int variable_list_delete();
/* black_white.c */ int variable_list_insert();
/* black_white.c */ int variable_list_empty();
/* black_white.c */ int get_next_variable();
/* black_white.c */ int print_variable_list();
/* canonical.c */ int is_minterm();
/* canonical.c */ pcover find_canonical_cover();
/* essentiality.c */ pcover etr_order();
/* essentiality.c */ int aux_etr_order();
/* essentiality.c */ pcover get_mins();
/* essentiality.c */ int ascending();
/* util_signature.c */ void set_time_limit();
/* util_signature.c */ int print_cover();
/* util_signature.c */ int sf_equal();
/* util_signature.c */ int mem_usage();
/* util_signature.c */ int time_usage();
/* util_signature.c */ void s_totals();
/* util_signature.c */ void s_runtime();
/* sigma.c */ pcube get_sigma();
/* sigma.c */ void set_not();
/* signature.c */ void cleanup();
/* signature.c */ pcover signature();
/* signature.c */ pcover generate_primes();
/* signature_exact.c */ pcover signature_minimize_exact();
/* signature_exact.c */ sm_matrix *signature_form_table();
