import os
import tempfile
import shutil
import unittest

exe_dir = os.path.dirname(os.path.realpath(__file__))
htmls = ["code/PCA.html", "code/generate.html","code/PC_score_statistics.html","index.html"]
project_dir = tempfile.TemporaryDirectory()

class TestDemo(unittest.TestCase):
    def setUp(self):
        os.rmdir(project_dir.name)
        os.mkdir(project_dir.name)
        os.chdir(project_dir.name)
    def tearDown(self):
        project_dir.cleanup()

    def test_demo(self):
        assert os.system("sk init --demo") == 0
        assert os.system("sk init --demo") == 0
        assert os.system("sk init --demo") == 0
        assert os.system("sk init --demo") == 0
        assert os.system("sk init --demo") == 0
        assert os.system("sk init --demo") == 0
        html_dir = os.path.join("report", "out_html")
        assert os.path.isdir(html_dir)
        for curr_file in htmls:
            assert os.path.isfile(os.path.join(html_dir, curr_file))


