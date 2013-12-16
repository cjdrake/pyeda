/* LINTLIBRARY */
#include "copyright.h"
#include "port.h"
#include <sys/wait.h>
#include "utility.h"

int
util_csystem(s)
char *s;
{
    register SIGNAL_FN (*istat)(), (*qstat)();
    union wait status;
    int pid, w, retval;

    if ((pid = vfork()) == 0) {
	(void) execl("/bin/csh", "csh", "-f", "-c", s, 0);
	(void) _exit(127);
    }

    /* Have the parent ignore interrupt and quit signals */
    istat = signal(SIGINT, SIG_IGN);
    qstat = signal(SIGQUIT, SIG_IGN);

    while ((w = wait(&status)) != pid && w != -1)
	    ;
    if (w == -1) {		/* check for no children ?? */
	retval = -1;
    } else {
	retval = status.w_status;
    }

    /* Restore interrupt and quit signal handlers */
    (void) signal(SIGINT, istat);
    (void) signal(SIGQUIT, qstat);
    return retval;
}
