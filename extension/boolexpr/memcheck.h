/*
** Filename: memcheck.h
**
** Convenience macros for checking memory allocation
*/


#ifndef MEMCHECK_H
#define MEMCHECK_H


#define CHECK_NULL(y, x) \
do { \
    if ((y = x) == NULL) \
        return NULL; \
} while (0)


#define CHECK_NULL_1(y, x, temp) \
do { \
    if ((y = x) == NULL) { \
        BX_DecRef(temp); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_2(y, x, t0, t1) \
do { \
    if ((y = x) == NULL) { \
        BX_DecRef(t0); \
        BX_DecRef(t1); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_3(y, x, t0, t1, t2) \
do { \
    if ((y = x) == NULL) { \
        BX_DecRef(t0); \
        BX_DecRef(t1); \
        BX_DecRef(t2); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_N(y, x, n, temps) \
do { \
    if ((y = x) == NULL) { \
        for (size_t i = 0; i < n; ++i) \
            BX_DecRef(temps[i]); \
        free(temps); \
        return NULL; \
    } \
} while (0)


#endif // MEMCHECK_H

