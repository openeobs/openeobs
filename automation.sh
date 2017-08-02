#!/bin/bash
travis_run_tests &
git clone https://github.com/BJSS/BJSS_liveobs_automation.git@SauceLabs-Browser
cd BJSS_liveobs_automation
pip install -r requirements.txt
behave features