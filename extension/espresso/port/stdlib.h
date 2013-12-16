/* ANSI Compatible stdlib.h stub */

extern double atof(char *);
extern int atoi(char *);
extern long atol(char *);
extern void abort();
extern char *calloc(unsigned int, unsigned int);
extern void exit(int);
extern void free(char *);
extern char *malloc(unsigned int);
extern char *realloc(char *, unsigned int);
extern char *getenv(char *);

/* should be in stdio.h */
extern void perror(char *);

#ifdef LINT
#undef putc
#endif
