import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_run")
code_dir = os.path.join(test_datadir, "code")
yaml_file = os.path.join(test_datadir, "scikick.yml")
# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"

htmls = ["code/analysis_normalization.html", "code/analysis_summary.html",
	"index.html", "code/test_python.html", "code/data_generate.html",
	"code/test_bash.html"]

class TestRun:
	# copy test project to a separate temporary directory
	def setup(self):
		self.project_dir = tempfile.TemporaryDirectory()
		shutil.copytree(code_dir, os.path.join(self.project_dir.name, "code"))
		shutil.copy2(yaml_file, self.project_dir.name)
		# go to the project dir, where scikick will be run
		os.chdir(self.project_dir.name)
	# delete the tmpdir/everything that was created
	def teardown(self):
		self.project_dir.cleanup()
	# running scikick with different arguments
	def test_run(self):
		os.system("%s run" % cli_name)
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		for curr_file in htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
	def test_run_noexistentf(self):
		os.system("%s add code/some_nonexistant_file.rmd" % cli_name)
		os.system("%s run" % cli_name)
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		all_htmls = htmls.copy()
		all_htmls.append("code/some_nonexistant_file.html")
		for curr_file in all_htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
