.c.o:
	$(CC) $(CFLAGS) -c -S $*.c
	check_pointer $*.s >$*.s1
	as -o $*.o $*.s1
	rm $*.s $*.s1
