import os
import re
import subprocess
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_layout")
code_dir = os.path.join(test_datadir, "code")
yaml_file = os.path.join(test_datadir, "scikick.yml")
# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"

class TestLayout:
	# copy test project to a separate temporary directory
	def setup(self):
		self.project_dir = tempfile.TemporaryDirectory()
		shutil.rmtree(self.project_dir.name)
		shutil.copytree(test_datadir, self.project_dir.name)
		# go to the project dir, where scikick will be run
		os.chdir(self.project_dir.name)
	# delete the tmpdir/everything that was created
	def teardown(self):
		self.project_dir.cleanup()
	# running scikick with different arguments
	def test_layout_no_commpath(self):
		status = subprocess.Popen("sk layout; sk layout -s f;" + \
			"sk layout -s subdir; sk layout -s subdir/subsub", \
			shell=True, stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(self.project_dir.name, "output.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
