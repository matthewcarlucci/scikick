import os
import tempfile
import shutil

exe_dir = os.path.dirname(os.path.realpath(__file__))

# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"

class TestInit:
	# copy test project to a separate temporary directory
	def setup(self):
		self.project_dir = tempfile.TemporaryDirectory()
		# go to the project dir, where scikick will be run
		os.chdir(self.project_dir.name)
	# delete the tmpdir/everything that was created
	def teardown(self):
		self.project_dir.cleanup()
	# running scikick with different arguments
	def test_init_basic(self):
		assert os.system("%s init" % cli_name) == 0
	def test_init(self):
		assert os.system("%s init --yaml --git --dirs" % cli_name) == 0
		for curr_file in ["scikick.yml", ".gitignore"]:
			assert os.path.isfile(curr_file)
		for curr_dir in ["report", "input", "output", "code"]:
			assert os.path.isdir(curr_dir)
	def test_init_1largs(self):
		assert os.system("%s init -ygd" % cli_name) == 0
		for curr_file in ["scikick.yml", ".gitignore"]:
			assert os.path.isfile(curr_file)
		for curr_dir in ["report", "input", "output", "code"]:
			assert os.path.isdir(curr_dir)
