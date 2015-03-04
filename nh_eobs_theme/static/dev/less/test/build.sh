#!/bin/bash

echo $(tput setaf 7)
# compile the CSS file
#lessc ../src/etake_style.less > css/etake_style.css
echo "Compiling all LESS files to CSS"
cd ../src/
for file in *.less
do
    FROM=$file
    TO=${file/.*/.css}
    echo "$FROM --> ../test/css/files/${TO}"
    lessc $FROM "../test/css/files/${TO}"
done
cd ../test

# lint over the files
echo $(tput setaf 1)
for file in css/files/*.css
do
    FROM=$file
    echo $(tput setaf 7)
    echo "######################################"
    echo "${file}                   "
    echo "######################################"
    echo $(tput setaf 1)
    csslint $FROM --ignore=adjoining-classes,box-model | grep 'csslint: There are' -A 1000
done
echo $(tput setaf 7)

# generate the styleguide
python generate_styleguide.py

cat css/files/* > css/test_etake_style.css
cat css/files/* > css/etake_style.css
cleancss -o css/test_etake_style.css css/test_etake_style.css -b --s0
# use UnCSS to ensure that all styles are used
#uncss styleguide.html > css/etake_style.css --ignoreSheets css/oe_base.css
cleancss -o css/etake_style.css css/etake_style.css -b --s0

#echo $(tput setaf 1)
#
#diff -y css/etake_style.css css/test_etake_style.css
#
#echo $(tput setaf 7)

echo $(tput setaf 2)
echo "## Minifying UnCSS'd file"
cleancss -o ../../../src/css/etake_style.css css/etake_style.css

filesize="$(du -h ../../../src/css/etake_style.css | cut -f1)"
echo "Resulting file is ${filesize}B"
echo $(tput setaf 7)