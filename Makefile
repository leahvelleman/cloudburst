RUNTEST=python -m unittest -v -b

% : test_%.py
	        ${RUNTEST} test_$@
