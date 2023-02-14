import os
import tempfile
import shutil
import unittest

htmls = ["index.html"]

class TestOther(unittest.TestCase):
    def setUp(self):
        self.project_dir = tempfile.TemporaryDirectory()
        os.chdir(self.project_dir.name)
    def tearDown(self):
        self.project_dir.cleanup()

    def test_index_only_proj(self):
        assert os.system("sk init") == 0
        assert os.system("sk run") == 0
        html_dir = os.path.join("report", "out_html")
        assert os.path.isdir(html_dir)
        for curr_file in htmls:
            assert os.path.isfile(os.path.join(html_dir, curr_file))

    def test_init_and_add(self):
        assert os.system("sk init") == 0
        assert os.system("sk add first.Rmd") == 0
