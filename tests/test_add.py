import os
import re
import tempfile
import shutil
import functools
import unittest

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_add")
htmls = ["code/page1.html", "code/page2.html"]
project_dir = tempfile.TemporaryDirectory()

class TestAdd(unittest.TestCase):
    def setUp(self):
        os.rmdir(project_dir.name)
        shutil.copytree(test_datadir, project_dir.name)
        os.chdir(project_dir.name)
        assert os.system("sk init -yd") == 0

    def tearDown(self):
        project_dir.cleanup()

    def test_add(self):
        assert os.system("sk add code/page1.Rmd") == 0
        assert os.system("sk add code/page2.Rmd -d code/page1.Rmd") == 0
        assert os.system("sk run") == 0
        html_dir = os.path.join("report", "out_html")
        assert os.path.isdir(html_dir)
        for curr_file in htmls:
            assert os.path.isfile(os.path.join(html_dir, curr_file))

if __name__ == '__main__':
    unittest.main()
