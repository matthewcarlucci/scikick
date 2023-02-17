import os
import re
import subprocess
import tempfile
import shutil
import functools
import unittest

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_status")
project_dir = tempfile.TemporaryDirectory()
output_dir = os.path.join(test_datadir, "outputs")

class TestStatus(unittest.TestCase):
    def setUp(self):
        if os.path.isdir(project_dir.name):
            shutil.rmtree(project_dir.name)
        shutil.copytree(test_datadir, project_dir.name)
        os.chdir(project_dir.name)
    def tearDown(self):
        project_dir.cleanup()

    def output_check(self,out_fname, verbose=False):
        skstat_cmd = "sk status"
        if verbose:
            skstat_cmd += " -v"
        status = subprocess.Popen(skstat_cmd, shell=True, stdout=subprocess.PIPE)
        current_output = status.stdout.read().decode()
        with open(os.path.join(output_dir, out_fname)) as out_file:
            expected_output = out_file.read()
            self.assertEqual(current_output,expected_output)

    def test_status_basic(self):
        self.output_check("output1.txt")

    def test_status_after_run(self):
        assert os.system("sk run") == 0
        self.output_check("output2.txt")

    def test_status_touch(self):
        os.system("sk run")
        os.system("echo 'trigger rerun' >> code/page1.Rmd")
        self.output_check("output3.txt")

    def test_status_touch_v(self):
        os.system("sk run")
        os.system("echo 'trigger rerun' >> code/page1.Rmd")
        self.output_check("output3_v.txt", True)

    def test_status_touch_rm(self):
        os.system("sk run")
        os.system("echo 'trigger rerun' >> code/page1.Rmd")
        os.system("rm code/page2.Rmd")
        self.output_check("output4.txt", True)

    def test_status_touch_config(self):
        os.system("sk run")
        os.system("echo '# trigger rerun' >> scikick.yml")
        self.output_check("output5.txt")

    def test_status_nohtml(self):
        os.system("sk run")
        os.system("rm report/out_html/code/*.html")
        self.output_check("output6.txt")

    def test_status_touch_md(self):
        os.system("sk run")
        os.system("echo 'trigger rerun' >> report/out_md/code/page1.md")
        self.output_check("output7.txt", True)

    def test_status_rm_md(self):
        os.system("sk run")
        os.system("rm report/out_md/code/page2.md")
        self.output_check("output8.txt", True)

    def test_status_skrunfile(self):
        os.system("sk run")
        os.system("rm report/out_md/code/page1.md")
        os.system("rm report/out_html/code/page1.html")
        os.system("sk run code/page1.Rmd")
        self.output_check("output9.txt", True)
