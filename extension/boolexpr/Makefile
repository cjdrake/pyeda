# Filename: Makefile

AR := ar
CC := c99
CXX := g++

GENHTML := genhtml
LCOV := lcov
VALGRIND := valgrind

.PHONY: help
help:
	@printf "Usage: make [options] [target] ...\n"
	@printf "\n"
	@printf "Valid targets:\n"
	@printf "\n"
	@printf "    help            Display this help message\n"
	@printf "    test            Run unit test suite\n"
	@printf "    memtest         Check for memory leaks\n"
	@printf "    cover           Collect coverage\n"
	@printf "    all             Build all binary targets\n"

.PHONY: test
test: bld/test/run
	@./$<

.PHONY: memtest
memtest: bld/test/run
	@$(VALGRIND) $(VALGRIND_FLAGS) ./$<

.PHONY: cover
cover: bld/cover/run
	@./$<
	@$(LCOV) -c -d bld/cover -o bld/cover/coverage.info
	@$(GENHTML) -o bld/cover/html bld/cover/coverage.info

.PHONY: all
all: bld/test/run bld/cover/run bld/lib/libboolexpr.a

#===============================================================================
# Source Code
#===============================================================================

BOOLEXPR_HDRS := boolexpr.h primes-inl.c

BOOLEXPR_SRCS := \
    argset.c \
    array.c \
    binary.c \
    boolexpr.c \
    bubble.c \
    compose.c \
    dict.c \
    flatten.c \
    nnf.c \
    product.c \
    set.c \
    simple.c \
    util.c \
    vector.c \

BOOLEXPR_TEST_HDRS := test/boolexprtest.hpp

BOOLEXPR_TEST_SRCS := \
    test/main.cpp \
    test/boolexprtest.cpp \
    test/test_argset.cpp \
    test/test_array.cpp \
    test/test_basic.cpp \
    test/test_binary.cpp \
    test/test_bubble.cpp \
    test/test_compose.cpp \
    test/test_dict.cpp \
    test/test_flatten.cpp \
    test/test_nnf.cpp \
    test/test_product.cpp \
    test/test_set.cpp \
    test/test_simple.cpp \
    test/test_vector.cpp \

#===============================================================================
# Build Rules
#===============================================================================

bld/:
	@mkdir $@

# Unit tests
bld/test/: | bld/
	@mkdir $@

bld/test/%.o: %.c $(BOOLEXPR_HDRS) | bld/test/
	$(CC) -c -g -o $@ $<

bld/test/%.o: test/%.cpp $(BOOLEXPR_TEST_HDRS) | bld/test/
	$(CXX) -c -g -I. -o $@ $<

TEST_OBJS := \
    $(patsubst %.c,bld/test/%.o,$(BOOLEXPR_SRCS)) \
    $(patsubst test/%.cpp,bld/test/%.o,$(BOOLEXPR_TEST_SRCS)) \

bld/test/run: $(TEST_OBJS)
	$(CXX) -o $@ -g $^ -lgtest -lpthread

# Coverage
bld/cover/: | bld/
	@mkdir $@

bld/cover/%.o: %.c $(BOOLEXPR_HDRS) | bld/cover/
	$(CC) -c --coverage -o $@ $<

bld/cover/%.o: test/%.cpp $(BOOLEXPR_TEST_HDRS) | bld/cover/
	$(CXX) -c -I. -o $@ $<

COVER_OBJS := \
    $(patsubst %.c,bld/cover/%.o,$(BOOLEXPR_SRCS)) \
    $(patsubst test/%.cpp,bld/cover/%.o,$(BOOLEXPR_TEST_SRCS)) \

bld/cover/run: $(COVER_OBJS)
	$(CXX) -o $@ --coverage $^ -lgtest -lpthread

# Library archive
bld/lib/: bld/
	@mkdir $@

bld/lib/%.o: %.c $(BOOLEXPR_HDRS) | bld/lib/
	$(CC) -c -o $@ $<

LIB_OBJS := $(patsubst %.c,bld/lib/%.o,$(BOOLEXPR_SRCS))

bld/lib/libboolexpr.a: $(LIB_OBJS)
	$(AR) -o $@ -crs $@ $^

