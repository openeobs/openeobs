#! /bin/bash

# build libs ready for tests
coffee -o tests/src/ -b -c *.coffee 

# build libs for browser foo
cat *.coffee | coffee -b --compile --stdio > playground/nhlib.js
