#include "copyright.h"
#include "port.h"

int f() {}

int g() {}

main()
{
    char *p, *malloc();

    p = malloc(10);
    f();
/*(    p[-1] = 0;*/
    g();
}

