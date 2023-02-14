import os
import re
import subprocess
import tempfile
import shutil
import functools
import unittest

exe_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = tempfile.TemporaryDirectory()
test_datadir = os.path.join(exe_dir, "data", "test_ipynb")

class TestIpynb(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(project_dir.name):
            shutil.rmtree(project_dir.name)
        shutil.copytree(test_datadir, project_dir.name)
        os.chdir(project_dir.name)
    def tearDown(self):
        project_dir.cleanup()

    def test_ipynb_atroot(self):
        assert os.system("sk add test.ipynb") == 0 
        assert os.system("sk run") == 0
        htmls = ["index.html", "test.html"]
        html_dir = os.path.join("report", "out_html")
        assert os.path.isdir(html_dir)
        for curr_file in htmls:
            assert os.path.isfile(os.path.join(html_dir, curr_file))
        assert os.path.isfile("output/test.png")

    def test_ipynb_insubdir(self):
        assert os.system("sk add code/test.ipynb") == 0 
        assert os.system("sk run") == 0
        htmls = ["index.html", "code/test.html"]
        html_dir = os.path.join("report", "out_html")
        assert os.path.isdir(html_dir)
        for curr_file in htmls:
            assert os.path.isfile(os.path.join(html_dir, curr_file))
        assert os.path.isfile("output/test.png")

