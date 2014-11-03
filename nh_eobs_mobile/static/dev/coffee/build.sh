#! /bin/bash

# build libs ready for tests
coffee -o tests/src/ -b -c *.coffee 

# build libs for browser foo
# cat nhlib.coffee nhmobile.coffee nhmobileform.coffee nhmobilepatient.coffee nhmodal.coffee | coffee --compile --stdio > playground/nhlib.js

cat nhlib.coffee nhmobile.coffee nhmobileform.coffee nhmobilepatient.coffee nhmodal.coffee nhmobileformloz.coffee | coffee --compile --stdio > playground/nhlib.js
