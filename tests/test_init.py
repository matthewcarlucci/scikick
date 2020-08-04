import os
import tempfile

exe_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = tempfile.TemporaryDirectory()

def setup():
    os.chdir(project_dir.name)
def teardown():
    project_dir.cleanup()

def test_init_basic():
    assert os.system("sk init") == 0

def test_init_options():
    assert os.system("sk init --yaml --git --dirs") == 0
    for curr_file in ["scikick.yml", ".gitignore"]:
        assert os.path.isfile(curr_file)
    for curr_dir in ["report", "input", "output", "code"]:
        assert os.path.isdir(curr_dir)
