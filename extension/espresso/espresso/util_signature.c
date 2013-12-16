/* Module:util_signature.c
 * Purpose:
 *	contains miscellaneous utility routines 
 * Routines:
 * void set_time_limit(seconds)
 *	sets the cpu time limit
 * int sf_equal():
 *	 checks equlaity of two set families.
 * int print_cover():
 *	prints cover.
 * int mem_usage():
 *	current Memory usage.
 *	Initialized on the first call.
 * int time_usage():
 *	current time usage.
 *	Initialized on the first call.
 */

#include <stdio.h>
#include <math.h>
#include "espresso.h"
#include "signature.h"
#include <sys/time.h>
#include <sys/resource.h>

void
set_time_limit(seconds)
int seconds;
{
	struct rlimit rlp_st, *rlp = &rlp_st;
	rlp->rlim_cur = seconds;
	setrlimit(RLIMIT_CPU, rlp);
}

int
print_cover(F,name)
pcover F;
char *name;
{
	pcube last, p;
	printf("%s:\t %d\n",name,F->count);
	foreach_set(F,last,p){
		print_cube(stdout,p,"~0");
	}
	printf("\n\n",name);
}

/* sf_equal: Check equality of two set families */
int
sf_equal(F1,F2)
pcover F1,F2;
{
	int i;
	int count = F1->count;
	pcube *list1,*list2;

	if(F1->count != F2->count){
		return(FALSE);
	}
	
	list1 = sf_sort(F1,descend);
	list2 = sf_sort(F2,descend);

	for(i = 0; i < count; i++){
		if(!setp_equal(list1[i],list2[i])){
			return FALSE;
		}
	}

	return TRUE;
}

/* mem_usage:
 * 	Initialized on first call. Prints current memory usage.
 */
int
mem_usage(name)
char *name;
{
	static int memory_init;
	int memory_current;
	static int flag = 1;

	if(flag){
		memory_init = sbrk(0);
		flag = 0;
	}

	memory_current = sbrk(0);

	printf("Memory %s\t %d\n", name, memory_current - memory_init);

	return memory_current;

}

/* time_usage:
 * 	Initialized on first call. Prints current time usage.
 */
int
time_usage(name)
char *name;
{
	static int time_init;
	int time_current;
	static int flag = 1;

	if(flag){
		time_init = ptime();
		flag = 0;
		return time_init;
	}

	time_current = ptime();

	printf("%s\t %ld\n", name, (time_current - time_init)/1000);

	return time_current;

}

/* s_totals : add time spent in the function and update call count */
void
s_totals(time,i)
long time;
int i;
{
    time = ptime() - time;
    total_time[i] += time;
    total_calls[i]++;
}

void
s_runtime(total)
long total;
{
    int i;
    long temp;

    for(i = 0; i < TIME_COUNT; i++) {
	if (total_calls[i] != 0) {
	    temp = 100 * total_time[i];
	    printf("# %s\t%2d call(s) for %s ( %2ld.%01ld%% )\n",
		total_name[i], total_calls[i], print_time(total_time[i]),
		    temp/total, (10 * (temp%total)) / total);
	}
    }
}

