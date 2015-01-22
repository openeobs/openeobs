#!/bin/bash

echo "Compiling LESS into CSS"
lessc src/kiosk_style.less > test/kiosk_style.css

echo "Testing CSS"
uncss test/styleguide.html > ../../src/css/kiosk_style.css

echo "Redundant Styles"
diff --suppress-common-lines -i -E -Z -b -B -w test/kiosk_style.css ../../src/css/kiosk_style.css