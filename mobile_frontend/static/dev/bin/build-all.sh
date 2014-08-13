#!/bin/bash

node_modules/.bin/gulp build_observation_js
node_modules/.bin/gulp build_patientgraph_js
node_modules/.bin/lessc ../less/compile.less ../../src/css/t4skr.css