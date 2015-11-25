#!/bin/bash

echo "## Compiling LESS into CSS"
lessc src/kiosk_style.less > test/kiosk_style.css

echo "## Running CSS Lint on compiled CSS file"
csslint test/kiosk_style.css --quiet --ignore=fallback-colors

echo "## Testing CSS against Style Guide  with UnCSS"
uncss test/styleguide.html > ../../src/css/kiosk_style.css
diff --suppress-common-lines -i -E -Z -b -B -w test/kiosk_style.css ../../src/css/kiosk_style.css

echo "## Minifying UnCSS'd file"
lessc ../../src/css/kiosk_style.css ../../src/css/kiosk_style.css -x

filesize="$(du -h ../../src/css/kiosk_style.css | cut -f1)"
echo "Resulting file is ${filesize}B"