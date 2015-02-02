# Filename: Makefile

AR := ar
CC := c99
CXX := g++

CPPFLAGS :=
CFLAGS :=
CXXFLAGS :=
ARFLAGS := -crs
LDFLAGS :=
LDLIBS := -lgtest -lpthread

GENHTML := genhtml
LCOV := lcov
VALGRIND := valgrind

ifdef COVER_ON
CFLAGS += --coverage
LDFLAGS += --coverage
endif

.PHONY: do_test
do_test: a.out
	@./$<

.PHONY: do_valgrind
do_valgrind: a.out
	@$(VALGRIND) ./$<

.PHONY: clean
clean:
	@rm -f *.o
	@rm -f *.gcda *.gcno coverage.info
	@rm -rf coverage

.PHONY: cover
cover: clean
	@$(MAKE) clean
	@$(MAKE) do_test COVER_ON=1
	@$(LCOV) -c -d . -o coverage.info
	@$(GENHTML) coverage.info -o coverage

#===============================================================================
# Source code
#===============================================================================

BOOLEXPR_HDRS := boolexpr.h

BOOLEXPR_SRCS := \
    array.c \
    array2.c \
    binary.c \
    boolexpr.c \
    bubble.c \
    compose.c \
    dict.c \
    flatten.c \
    nnf.c \
    set.c \
    simple.c \
    util.c \
    vector.c \

TEST_HDRS := test/boolexprtest.hpp

TEST_SRCS := \
    test/main.cpp \
    test/boolexprtest.cpp \
    test/test_array.cpp \
    test/test_array2.cpp \
    test/test_basic.cpp \
    test/test_binary.cpp \
    test/test_bubble.cpp \
    test/test_compose.cpp \
    test/test_dict.cpp \
    test/test_flatten.cpp \
    test/test_nnf.cpp \
    test/test_set.cpp \
    test/test_simple.cpp \
    test/test_vector.cpp \

#===============================================================================
# Generic rules
#===============================================================================

%.o: %.c $(BOOLEXPR_HDRS)
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

test/%.o: test/%.cpp $(TEST_HDRS)
	$(CXX) -c -I. $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

#===============================================================================
# boolexpr library
#===============================================================================

BOOLEXPR_OBJS := $(patsubst %.c,%.o,$(BOOLEXPR_SRCS))

libboolexpr.a: $(BOOLEXPR_OBJS)
	$(AR) $(ARFLAGS) $@ $^

#===============================================================================
# Unit tests
#===============================================================================

TEST_OBJS := $(patsubst test/%.cpp,test/%.o,$(TEST_SRCS))

a.out: $(BOOLEXPR_OBJS) $(TEST_OBJS)
	$(CXX) -o $@ $(LDFLAGS) $^ $(LDLIBS)

