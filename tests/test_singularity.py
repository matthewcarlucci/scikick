import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_run")
htmls = ["code/page1.html", "code/page2.html"]
project_dir = tempfile.TemporaryDirectory()
sing_img = "docker://rocker/tidyverse:4.0.0"

def setup():
    os.rmdir(project_dir.name)
    shutil.copytree(test_datadir, project_dir.name)
    os.chdir(project_dir.name)
def teardown():
    project_dir.cleanup()

def test_singularity():
    assert os.system(f"sk config --singularity {sing_img}") == 0
    assert os.system("sk run -v -s --use-singularity") == 0
    html_dir = os.path.join("report", "out_html")
    assert os.path.isdir(html_dir)
    for curr_file in htmls:
        assert os.path.isfile(os.path.join(html_dir, curr_file))
