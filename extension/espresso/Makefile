# Makefile

VPATH := src utility

CC := clang
CFLAGS :=

# espresso
OBJS := cofactor cols compl contain cubestr cvrin cvrm cvrmisc cvrout dominate espresso essen exact expand gasp gimpel globals hack indep irred main matrix mincov opo pair part primes reduce rows set setc sharp sminterf solution sparse unate verify

espresso: $(addsuffix .o,$(OBJS))
	$(CC) -o $@ $^

%.o: %.c
	$(CC) -c $(CFLAGS) $<

.PHONY: test
test: espresso
	@./test.py

.PHONY: clean
clean:
	rm -f *.o
	rm -f espresso
