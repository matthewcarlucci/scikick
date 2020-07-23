import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_nested")

htmls = ["readandproduce.html"]

class TestNested:
	# copy test project to a separate temporary directory
	def setup(self):
		self.project_dir = tempfile.TemporaryDirectory()
		shutil.copytree(test_datadir,
			os.path.join(self.project_dir.name, "test_datadir"))
		# go to the project dir, where scikick will be run
		os.chdir(os.path.join(self.project_dir.name, "test_datadir"))
	# delete the tmpdir/everything that was created
	def teardown(self):
		self.project_dir.cleanup()
	# running scikick with different arguments
	def test_nested(self):
		assert os.system("scikick run") == 0
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		for curr_file in htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
