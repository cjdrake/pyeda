#
#  Octtools 3.0 Makefile
#
#  utility - Provides commonly used functions and macros
#
#  Makefile created on Thu Feb 16 20:38:50 PST 1989 by octtools (using 'create-octtools-makefile')
#
#  Copyright (c) 1988, 1989, Regents of the University of California
#
#
# Description of the 'targets':
#
#  all:			create the tags file, run lint, build the tool/package
#  install:		build the tool/package and install all the necessary files
#  uninstall:		remove the files that would be installed with 'make install'
#  debug:		build and install the debug versions of the package
#				(for tools, build the debug versions and leave in the
#				source directories; note: debug versions of tools
#				MUST be built using 'make debug' or 'make debug-*')
#  header:		install the exported header files for the package
#  lint:		run lint
#  clean:		remove the binary, object files, and temporary files
#  require:		echo a list of packages used in the compilation of the tool/package
#  toolrequire:		echo a list of tools used in the running of the tool
#  test:		run a simple test on the tool/package
#  tags:		build the 'tags' file (for 'vi')
#  TAGS:		build the 'TAGS' file (for 'emacs')
#  info:		echo a one-line description of the tool/package
#  print:		print out the man page or doc file for the tool/package
#  dist:		dist the tool/package
#  test-dist:		tell what would be disted in 'make dist' were run
#  depend:		generate the dependency information
#  strip-depend:	remove the dependency information
#
#
# Description of the 'variables':
#
#  BUILD:		name of the program that builds a 'Makefile' from
#				'Makefile.template'
#  CAD:			location of the CAD tools (for installation)
#  CADROOT:		run-time location of the CAD libraries (can have '~')
#  CC:			name of the C-compiler
#  COMPFLAG:		compilation level (usually nothing, -g, -pg, or -O)
#  CP:			name of the program used for installation ('cp' for installing
#				the file each time, 'ln -s' for installing a link)
#  LDFLAGS:		flags used for linking (e.g., -lXMenu -lX -lm)
#  LINKER:		name of the program used for linking (normally '${CC}')
#  LINTCREATEFLAG:	flag used by 'lint' for creating lint libraries
#				(-C for BSD, ULTRIX 2.2; -o for IBM RT/PC, ULTRIX 3.0)
#  PRINTER:		name of the printer
#  SHELL:		shell used by 'make' (should always be the bourne shell)
#  UTILS:		location of the utility programs
#
#
#------------------------------------------------------------------------------

# for HPUX
SHELL	= /bin/sh

CAD	= /net/shambhala/users/octtools-3.0
CADROOT	= ~octtools
UTILS	= ${CAD}/utils

LINTCREATEFLAG = -C
COMPFLAG=

# an alternative if you want links in the installation locations
# back to the source directories would be:
#   CP = sh -c 'ln -s `pwd`/$$0 $$1'
CP = cp

BUILD = ${UTILS}/bin/create-octtools-makefile

# alternate (for ULTRIX) would be LINKER = 'ld -N ${CAD}/utils/pageZero/crt0.o'
# (this will not work for -pg programs)
LINKER = ${CC}

# cute hack for the sequent
#   setenv PARALLEL 8; make P="&" install
P = 

NAME	= utility

# packages required for this package/tool
REQUIRE	= st mm port

# tools required for this tool
TOOLREQUIRE = 

SRC	= cpu_time.c csystem.c pathsearch.c pipefork.c prtime.c strsav.c texpand.c tmpfile.c
LSRC	= cpu_time.c csystem.c pathsearch.c pipefork.c prtime.c strsav.c texpand.c tmpfile.c
OBJ	= cpu_time.o csystem.o pathsearch.o pipefork.o prtime.o strsav.o texpand.o tmpfile.o
HDR	= utility.h
EXPHDR	= ${NAME}.h

DRVRSRC	= uttest.c
DRVROBJ	= uttest.o
DRIVER	= $(NAME)-test

CADBIN	= ${CAD}/bin

PKGINSTALL= ${CAD}/lib/${LIB} ${CAD}/include/${EXPHDR} ${CAD}/lib/${LINTLIB} ${CAD}/doc/${DOC}
INSTALL	= ${PKGINSTALL} ${TOOLINSTALL} 

DISTDEST= ${CAD}/src/${NAME}
DISTHOST= octtools@shambhala
MISC	= Makefile Makefile.template 

LIBS	= $(CAD)/lib/libst$(COMPFLAG).a $(CAD)/lib/libmm$(COMPFLAG).a $(CAD)/lib/liberrtrap$(COMPFLAG).a $(CAD)/lib/libuprintf$(COMPFLAG).a $(CAD)/lib/libport$(COMPFLAG).a
LINTLIBS= $(CAD)/lib/llib-lst.ln $(CAD)/lib/llib-lmm.ln $(CAD)/lib/llib-lport.ln

LIB	= lib${NAME}.a
LIBPG	= lib${NAME}-pg.a
LIBG	= lib${NAME}-g.a
LINTLIB	= llib-l${NAME}.ln
DOC	= ${NAME}.doc

PRINTER	= lps40
MACROS	= -man.4.3
PRINT	= lpr
TROFF	= ptroff
TBL	= tbl

INCLUDE	= -I${CAD}/include 
CFLAGS	= ${COMPFLAG} ${INCLUDE} '-DCADROOT="${CADROOT}"'
VERSION	= "-DCUR_DATE=\"`date | awk '{print $$2, $$3, $$6}'`\"" \
	  "-DCUR_TIME=\"`date | awk '{print $$4}'`\""
LINTFLAGS= ${INCLUDE} '-DCADROOT="${CADROOT}"'
LINTLIBFLAGS= ${INCLUDE} '-DCADROOT="${CADROOT}"'
LDFLAGS	= -lm

#-----------------------------------------------------------------------

all: tags lint ${LIB} ${LINTLIB}

build: Makefile.template
	${BUILD} Makefile.template

install: ${INSTALL}

uninstall:
	rm -rf ${INSTALL} ${CAD}/lib/${LIBG} ${CAD}/lib/${LIBPG}

version.o: version.c
	${CC} ${CFLAGS} ${VERSION} -c version.c
	-touch -f version.c

debug: debug-g debug-pg

debug-g: ${CAD}/lib/${LIBG}

debug-pg: ${CAD}/lib/${LIBPG}



${DRIVER}:${P} ${DRVROBJ} ${LIB} ${LIBS}
	${LINKER} ${COMPFLAG} -o ${DRIVER} ${DRVROBJ} ${LIB} ${LIBS} ${LDFLAGS}



${LIB}:${P} ${OBJ}
	ar r $@ $?
	ranlib $@

${LINTLIB}: ${LSRC} ${HDR}
	lint ${LINTLIBFLAGS} ${LINTCREATEFLAG}${NAME} -n ${LSRC}

${LIBPG}: ${SRC} ${HDR}
	rm -f ${OBJ}
	-ar xo $@
	make COMPFLAG=-pg CC="${CC}" CAD="${CAD}" CADROOT="${CADROOT}" ${MFLAGS} .pg
	-ar xo ${LIB}

.pg :${P} ${OBJ}
	ar r ${LIBPG} $?
	ranlib ${LIBPG}
	touch .pg

${LIBG}: ${SRC} ${HDR}
	rm -f ${OBJ}
	-ar xo $@
	make COMPFLAG=-g CC="${CC}" CAD="${CAD}" CADROOT="${CADROOT}" ${MFLAGS} .g
	-ar xo ${LIB}

.g :${P} ${OBJ}
	ar r ${LIBG} $?
	ranlib ${LIBG}
	touch .g

${CAD}/lib/${LIB}: ${LIB}
	rm -f $@
	${CP} $? $@
	ranlib $@

header:: ${CAD}/include/${EXPHDR}

${CAD}/include/${EXPHDR}: ${EXPHDR}
	rm -f $@
	${CP} $? $@

${CAD}/lib/${LINTLIB}: ${LINTLIB}
	rm -f $@
	${CP} $? $@

${CAD}/doc/${DOC}: ${DOC}
	rm -f $@
	${CP} $? $@

${CAD}/lib/${LIBG}: ${LIBG}
	rm -f $@
	${CP} $? $@
	ranlib $@

${CAD}/lib/${LIBPG}: ${LIBPG}
	rm -f $@
	${CP} $? $@
	ranlib $@


lint: ${LSRC} ${DRVRSRC} ${HDR} ${LINTLIBS}
	lint ${LINTFLAGS} ${LSRC} ${DRVRSRC} ${LINTLIBS} ${LDFLAGS} | tee lint

clean::
	rm -f ${OBJ} ${DRVROBJ} ${TARGET} ${TARGETG} ${TARGETPG} ${DRIVER} tags TAGS ${LIB} ${LIBG} ${LIBPG} ${LINTLIB} lint make.out mktemp

require:
	@echo ${REQUIRE}

toolrequire:
	@echo ${TOOLREQUIRE}

test::
	@test -f ${CAD}/lib/${LIB}

tags: ${LSRC} ${DRVRSRC} ${HDR}
	ctags ${LSRC} ${DRVRSRC} ${HDR}

TAGS: ${LSRC} ${DRVRSRC} ${HDR}
	etags ${LSRC} ${DRVRSRC} ${HDR}

info:
	@echo '${NAME}:  Provides commonly used functions and macros'

print:: ${DOC} ${MAN}
	${PRINT} -P${PRINTER} ${DOC}

dist: ${SRC} ${DRVRSRC} ${HDR} ${DOC} ${MAN}
	rdist -Rich ${SRC} ${DRVRSRC} ${HDR} ${DOC} ${MAN} ${MISC} ${DISTHOST}:${DISTDEST}

test-dist: ${SRC} ${DRVRSRC} ${HDR} ${DOC} ${MAN}
	rdist -Richv ${SRC} ${DRVRSRC} ${HDR} ${DOC} ${MAN} ${MISC} ${DISTHOST}:${DISTDEST}


depend: ${SRC} ${DRVRSRC} ${HDR}
	@rm -f mktemp
	@sed '/^#--DO NOT CHANGE ANYTHING AFTER THIS LINE/,$$d' Makefile > mktemp
	@echo '#--DO NOT CHANGE ANYTHING AFTER THIS LINE' >> mktemp
	@${UTILS}/bin/cc-M ${INCLUDE} ${SRC} ${DRVRSRC} | sed 's|${CAD}|$${CAD}|g' >>mktemp
	@mv mktemp Makefile

strip-depend:
	@rm -f mktemp
	@sed '/^#--DO NOT CHANGE ANYTHING AFTER THIS LINE/,$$d' Makefile > mktemp
	@mv mktemp Makefile

# does not work with 'pat2tap' creation of devnames.h
#${SRC} ${DRVRSRC} ${HDR}:
#	co $@

#--EXTRA TARGETS
test:: ${DRIVER}
	@${DRIVER}


#--DO NOT CHANGE ANYTHING AFTER THIS LINE
cpu_time.o: cpu_time.c ${CAD}/include/ansi.h
cpu_time.o:  ${CAD}/include/copyright.h
cpu_time.o:  ${CAD}/include/port.h utility.h
csystem.o: csystem.c ${CAD}/include/ansi.h
csystem.o:  ${CAD}/include/copyright.h
csystem.o:  ${CAD}/include/port.h utility.h
pathsearch.o: pathsearch.c ${CAD}/include/ansi.h
pathsearch.o:  ${CAD}/include/copyright.h
pathsearch.o:  ${CAD}/include/port.h utility.h
pipefork.o: pipefork.c ${CAD}/include/ansi.h
pipefork.o:  ${CAD}/include/copyright.h
pipefork.o:  ${CAD}/include/port.h utility.h
prtime.o: prtime.c ${CAD}/include/ansi.h
prtime.o:  ${CAD}/include/copyright.h
prtime.o:  ${CAD}/include/port.h utility.h
strsav.o: strsav.c ${CAD}/include/ansi.h
strsav.o:  ${CAD}/include/copyright.h
strsav.o:  ${CAD}/include/port.h utility.h
texpand.o: texpand.c ${CAD}/include/ansi.h
texpand.o:  ${CAD}/include/copyright.h
texpand.o:  ${CAD}/include/port.h
texpand.o:  ${CAD}/include/st.h utility.h
tmpfile.o: tmpfile.c ${CAD}/include/ansi.h
tmpfile.o:  ${CAD}/include/copyright.h
tmpfile.o:  ${CAD}/include/port.h utility.h
uttest.o: uttest.c ${CAD}/include/ansi.h
uttest.o:  ${CAD}/include/copyright.h
uttest.o:  ${CAD}/include/port.h utility.h
