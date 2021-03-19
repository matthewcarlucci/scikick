import os
import re
import subprocess
import tempfile
import shutil
import functools
from nose.tools import assert_equal

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_layout")
project_dir = tempfile.TemporaryDirectory()

def setup():
    os.rmdir(project_dir.name)
    shutil.copytree(test_datadir, project_dir.name)
    os.chdir(project_dir.name)
def teardown():
    project_dir.cleanup()

def test_layout():
    status = subprocess.Popen("sk layout; sk layout -s f;" + \
        "sk layout -s subdir; sk layout -s subdir/subsub", \
        shell=True, stdout=subprocess.PIPE)
    current_output = status.stdout.read().decode()
    with open(os.path.join(project_dir.name, "output.txt")) as out_file:
        assert_equal(current_output, out_file.read())
