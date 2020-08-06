import os
import re
import tempfile
import shutil
import functools
import subprocess
from nose.tools import with_setup
from scikick.yaml import yaml_in

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_mv")
project_dir = tempfile.TemporaryDirectory()

def setup():
    if os.path.isdir(project_dir.name):
        shutil.rmtree(project_dir.name)
    shutil.copytree(test_datadir, project_dir.name)
    os.chdir(project_dir.name)
    os.mkdir("code/subdir")
def teardown():
    project_dir.cleanup()

@with_setup(setup, teardown)
def test_mv_file2file():
    assert os.system("sk run") == 0
    assert os.system("sk mv code/page1.Rmd code/page3.Rmd") == 0
    # check the files
    assert os.path.isfile("code/page3.Rmd")
    assert os.path.isfile("report/out_md/code/page3.md")
    # check the yaml
    assert "code/page3.Rmd" in yaml_in()["analysis"].keys()

@with_setup(setup, teardown)
def test_mv_file2dir():
    assert os.system("sk run") == 0
    assert os.system("sk mv code/page1.Rmd code/subdir") == 0
    # check the files
    assert os.path.isfile("code/subdir/page1.Rmd")
    assert os.path.isfile("report/out_md/code/subdir/page1.md")
    # check the yaml
    assert "code/subdir/page1.Rmd" in yaml_in()["analysis"].keys()

@with_setup(setup, teardown)
def test_mv_dir2exdir():
    assert os.system("sk run") == 0
    assert os.system("sk mv code/subdf code/subdir") == 0
    # check the files
    assert os.path.isfile("code/subdir/subdf/pagesd.Rmd")
    assert os.path.isfile("report/out_md/code/subdir/subdf/pagesd.md")
    # check the yaml
    assert "code/subdir/subdf/pagesd.Rmd" in yaml_in()["analysis"].keys()

@with_setup(setup, teardown)
def test_mv_dir2nonexdir():
    assert os.system("sk run") == 0
    assert os.system("sk mv code/subdf code/subdf2") == 0
    # check the files
    assert os.path.isfile("code/subdf2/pagesd.Rmd")
    assert os.path.isfile("report/out_md/code/subdf2/pagesd.md")
    # check the yaml
    assert "code/subdf2/pagesd.Rmd" in yaml_in()["analysis"].keys()

@with_setup(setup, teardown)
def test_mv_mul2dir():
    assert os.system("sk run") == 0
    assert os.system("sk mv code/*.Rmd code/subdir") == 0
    # check the files
    assert os.path.isfile("code/subdir/page1.Rmd")
    assert os.path.isfile("code/subdir/page2.Rmd")
    assert os.path.isfile("report/out_md/code/subdir/page1.md")
    assert os.path.isfile("report/out_md/code/subdir/page2.md")
    # check the yaml
    assert "code/subdir/page1.Rmd" in yaml_in()["analysis"].keys()
    assert "code/subdir/page2.Rmd" in yaml_in()["analysis"].keys()

@with_setup(setup, teardown)
def test_mv_mul2onef():
    assert os.system("sk mv code/*.Rmd code/subdf/pagesd.Rmd") != 0

@with_setup(setup, teardown)
def test_mv_mul2nonex():
    assert os.system("sk mv code/*.Rmd nonexistf.Rmd") != 0
