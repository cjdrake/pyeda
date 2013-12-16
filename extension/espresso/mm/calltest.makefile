.c.o:
	$(CC) $(CFLAGS) -c -S $*.c
	check_pointer $*.s >$*.s1
	as -o $*.o $*.s1
#	rm $*.s $*.s1

a.out: calltest.o
	cc -o calltest calltest.o libmm_t.a
