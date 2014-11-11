#! /bin/bash

# build libs ready for tests
coffee -o ../../static/src/coffee -b -c *.coffee

# build libs for browser foo
cat nh_graphlib.coffee nh_graphlib_context.coffee nh_graphlib_focus.coffee nh_graphlib_graph.coffee nh_graphlib_table.coffee | coffee --compile --stdio > ../../static/src/js/nh_graphlib.js

#cat nhlib.coffee nhmobile.coffee nhmobileform.coffee nhmobilepatient.coffee nhmodal.coffee nhmobileformloz.coffee | coffee --compile --stdio > playground/nhlib.js
