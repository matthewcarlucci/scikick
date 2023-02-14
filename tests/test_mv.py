import os
import re
import tempfile
import shutil
import functools
import subprocess
from scikick.yaml import yaml_in
import unittest

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_mv")
project_dir = tempfile.TemporaryDirectory()

class TestMv(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(project_dir.name):
            shutil.rmtree(project_dir.name)
        shutil.copytree(test_datadir, project_dir.name)
        os.chdir(project_dir.name)
        os.mkdir("code/subdir")
    def tearDown(self):
        project_dir.cleanup()

    def test_mv_file2file(self):
        assert os.system("sk run") == 0
        assert os.system("sk mv code/page1.Rmd code/page3.Rmd") == 0
        # check the files
        assert os.path.isfile("code/page3.Rmd")
        assert os.path.isfile("report/out_md/code/page3.md")
        # check the yaml
        assert "code/page3.Rmd" in yaml_in()["analysis"].keys()

    def test_mv_file2subdirfile_runagain(self):
        assert os.system("sk run") == 0
        assert os.system("sk mv code/page1.Rmd code/subdf/page1.Rmd") == 0
        # check the files
        assert os.path.isfile("code/subdf/page1.Rmd")
        assert os.path.isfile("report/out_md/code/subdf/page1.md")
        # check the yaml
        assert "code/subdf/page1.Rmd" in yaml_in()["analysis"].keys()
        assert os.system("sk run > /dev/null") == 0

    def test_mv_file2dir(self):
        assert os.system("sk run") == 0
        assert os.system("sk mv code/page1.Rmd code/subdir") == 0
        # check the files
        assert os.path.isfile("code/subdir/page1.Rmd")
        assert os.path.isfile("report/out_md/code/subdir/page1.md")
        # check the yaml
        assert "code/subdir/page1.Rmd" in yaml_in()["analysis"].keys()

    def test_mv_dir2exdir(self):
        assert os.system("sk run") == 0
        assert os.system("sk mv code/subdf code/subdir") == 0
        # check the files
        assert os.path.isfile("code/subdir/subdf/pagesd.Rmd")
        assert os.path.isfile("report/out_md/code/subdir/subdf/pagesd.md")
        # check the yaml
        assert "code/subdir/subdf/pagesd.Rmd" in yaml_in()["analysis"].keys()

    # also check for the non-rmd dep
    def test_mv_dir2nonexdir(self):
        assert os.system("sk run") == 0
        assert os.system("sk mv code/subdf code/subdf2") == 0
        # check the files
        assert os.path.isfile("code/subdf2/pagesd.Rmd")
        assert os.path.isfile("report/out_md/code/subdf2/pagesd.md")
        # check the yaml
        assert "code/subdf2/pagesd.Rmd" in yaml_in()["analysis"].keys()
        assert "code/subdf2/non_rmd_dep.txt" in yaml_in()["analysis"]["code/subdf2/pagesd.Rmd"]

    def test_mv_mul2dir(self):
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

    def test_mv_mul2onef(self):
        assert os.system("sk mv code/*.Rmd code/subdf/pagesd.Rmd") != 0

    def test_mv_mul2nonex(self):
        assert os.system("sk mv code/*.Rmd nonexistf.Rmd") != 0
