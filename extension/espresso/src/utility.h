// Filename: utility.h

#ifndef UTILITY_H
#define UTILITY_H

#include <stdlib.h>

#define NIL(type) ((type *) 0)

#define ALLOC(type, num) ((type *) malloc(sizeof(type) * (num)))

#define REALLOC(type, obj, num)                                                \
    (obj) ? ((type *) realloc((char *) obj, sizeof(type) * (num)))             \
          : ((type *) malloc(sizeof(type) * (num)))

#define FREE(obj) if ((obj)) { free((char *) (obj)); (obj) = 0; }

#ifndef MAX
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#endif

#ifndef MIN
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#endif

#ifndef ABS
#define ABS(a) ((a) > 0 ? (a) : -(a))
#endif

#endif // UTILITY_H

