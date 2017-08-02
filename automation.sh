#!/bin/bash
travis_run_tests
git clone https://github.com/BJSS/BJSS_liveobs_automation.git
cd BJSS_liveobs_automation
pip install -r requirements.txt
behave features