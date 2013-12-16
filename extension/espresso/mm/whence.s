/* sccsid "@(#)whence.s	1.5 MAGIC (Berkeley) 2/8/85" */

/*
 * Three procedures for managing stack traces.
 * Currently used by malloc for leak tracing.
 *
 * whence --
 *	Return the frame pointer of our caller's caller.
 *
 * nextfp --
 *	Given a frame pointer, return the frame pointer to
 *	the previous stack frame.
 *
 * thispc --
 *	Given a frame pointer, return the PC from which this
 *	frame was called.
 */

#if	defined(VAX) || defined(vax)
	/*
	 * The calls instruction on the VAX updates the
	 * frame pointer, so we have to go back two levels
	 * on the stack.
	 */
	.globl	_whence
	.globl	_nextfp
	.globl	_thispc
	.globl	_memset

_whence:
	.word	0
	movl	12(fp),r0	/* r0/ fp of caller */
	movl	12(r0),r0	/* r0/ fp of caller's caller */
	ret

_nextfp:
	.word 	0
	movl	4(ap),r0	/* r0/ argument fp */
	movl	12(r0),r0	/* r0/ previous fp */
	ret

_thispc:
	.word	0
	movl	4(ap),r0	/* r0/ argument fp */
	movl	16(r0),r0	/* r0/ pc with fp */
	ret

_memset:	/* DAMN ULTRIX for inefficient memset */
	.word 0
	movc5	$0,(sp),8(ap),12(ap),*4(ap)
	movl	4(ap),r0
	ret

#endif	defined(VAX) || defined(vax)


#if	defined(mc68000) || defined(SUN2)
	.globl	_whence
	.globl	_nextfp
	.globl	_thispc
_whence:
	movl	a6@,a0
	movl	a0@,d0
	rts

_nextfp:
	movl	sp@(4),a0
	movl	a0@,d0
	rts

_thispc:
	movl	sp@(4),a0
	movl	a0@(4),d0
	rts
#endif	defined(mc68000) || defined(SUN2)
