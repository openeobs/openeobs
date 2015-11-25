__author__ = 'colin'
import subprocess, shutil

# compile LESS into CSS
compile_for_test = subprocess.Popen(['lessc', 'src/kiosk_style.less', 'test/kiosk_style.css'], stdout=subprocess.PIPE)
compiler_output = compile_for_test.stdout.readline()

if len(compiler_output) is 0:
    # run tests against it with uncss
    uncss_test = subprocess.Popen(['uncss', 'test/styleguide.html'], stdout=subprocess.PIPE)
    uncss_output = uncss_test.stdout.readline()

    # move tested CSS into src/css folder
    final_css = open('../../src/css/kiosk_style.css', 'w')
    final_css.write(uncss_output)
    final_css.close()
else:
    print compiler_output