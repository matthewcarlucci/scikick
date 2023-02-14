import os
import tempfile
import unittest
import shutil

class TestInit(unittest.TestCase):
    def setUp(self):
        self.project_dir = tempfile.TemporaryDirectory()
        os.chdir(self.project_dir.name)
    def tearDown(self):
        self.project_dir.cleanup()

    def test_init_basic(self):
        assert os.system("sk init") == 0

    def test_init_options(self):
        assert os.system("sk init --yaml --git --dirs") == 0
        for curr_file in ["scikick.yml", ".gitignore"]:
            assert os.path.isfile(curr_file)
        for curr_dir in ["report", "input", "output", "code"]:
            assert os.path.isdir(curr_dir)
