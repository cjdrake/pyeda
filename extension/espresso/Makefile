all: 
	-mkdir lib include doc
	(cd utility; make ../include/utility.h CAD=..)
	for i in port uprintf errtrap st mm utility; do \
		(cd $$i; make install CAD=..); done
	(cd espresso; make CAD=..)

clean:
	for i in port uprintf errtrap st mm utility espresso; do \
		(cd $$i; make clean CAD=..); done
