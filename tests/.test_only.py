import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_only")
code_dir = os.path.join(test_datadir, "code")
yaml_file = os.path.join(test_datadir, "scikick.yml")

htmls_no = ["analysis_normalization.html", "analysis_summary.html",
	"index.html", "test_python.html", "analysis_oscillations.html",
	"test_bash.html"]
htmls = ["data_generate.html"] 

class TestOnly:
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
	def test_only(self):
		os.system("scikick run -o %s" % re.sub("(.*).html",
			"code/\\1.Rmd", htmls[0]))
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		for curr_file in htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
		for curr_file in htmls_no:
			assert not os.path.isfile(os.path.join(html_dir, curr_file))
