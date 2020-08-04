import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_run")
project_dir = tempfile.TemporaryDirectory()

htmls = ["code/page1.html"]
htmls_not = ["code/page2.html"]

def setup():
    os.rmdir(project_dir.name)
    shutil.copytree(test_datadir, project_dir.name)
    os.chdir(project_dir.name)
def teardown():
    project_dir.cleanup()

def test_rm():
    assert os.system("sk del code/page2.Rmd -d code/page1.Rmd") == 0
    assert os.system("sk del code/page2.Rmd") == 0
    assert os.system("sk run") == 0
    html_dir = os.path.join("report", "out_html")
    assert os.path.isdir(html_dir)
    for curr_file in htmls:
        assert os.path.isfile(os.path.join(html_dir, curr_file))
    for curr_file in htmls_not:
        assert not os.path.isfile(os.path.join(html_dir, curr_file))
