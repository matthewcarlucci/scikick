import os
import re
import subprocess
import tempfile
import shutil
import functools
from nose import with_setup

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_status")
project_dir = tempfile.TemporaryDirectory()
output_dir = os.path.join(test_datadir, "outputs")

def setup():
    if os.path.isdir(project_dir.name):
        shutil.rmtree(project_dir.name)
    shutil.copytree(test_datadir, project_dir.name)
    os.chdir(project_dir.name)
def teardown():
    project_dir.cleanup()

def output_check(out_fname, verbose=False):
    skstat_cmd = "sk status"
    if verbose:
        skstat_cmd += " -v"
    status = subprocess.Popen(skstat_cmd, shell=True, stdout=subprocess.PIPE)
    current_output = status.stdout.read().decode()
    with open(os.path.join(output_dir, out_fname)) as out_file:
        assert current_output == out_file.read()

@with_setup(setup, teardown)
def test_status_basic():
    output_check("output1.txt")

@with_setup(setup, teardown)
def test_status_after_run():
    assert os.system("sk run") == 0
    output_check("output2.txt")

@with_setup(setup, teardown)
def test_status_touch():
    os.system("sk run")
    os.system("touch code/page1.Rmd")
    output_check("output3.txt")

@with_setup(setup, teardown)
def test_status_touch_v():
    os.system("sk run")
    os.system("touch code/page1.Rmd")
    output_check("output3_v.txt", True)

@with_setup(setup, teardown)
def test_status_touch_rm():
    os.system("sk run")
    os.system("touch code/page1.Rmd")
    os.system("rm code/page2.Rmd")
    output_check("output4.txt", True)

@with_setup(setup, teardown)
def test_status_basic():
    os.system("sk run")
    os.system("touch scikick.yml")
    output_check("output5.txt")

@with_setup(setup, teardown)
def test_status_nohtml():
    os.system("sk run")
    os.system("rm report/out_html/code/*.html")
    output_check("output6.txt")

@with_setup(setup, teardown)
def test_status_mdtouch():
    os.system("sk run")
    os.system("touch report/out_md/code/page1.md")
    output_check("output7.txt", True)
