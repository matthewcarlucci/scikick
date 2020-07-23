import os
import re
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
code_dir = os.path.join(exe_dir, "data", "test_add", "code")
# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"

htmls = ["code/analysis_normalization.html", "code/analysis_summary.html",
	"index.html", "code/test_python.html",
	"code/data_generate.html", "code/test_bash.html"]

class TestAdd:
	# copy test project to a separate temporary directory
	def setup(self):
		self.project_dir = tempfile.TemporaryDirectory()
		shutil.rmtree(self.project_dir.name)
		shutil.copytree(os.path.join(code_dir, ".."), self.project_dir.name)
		# go to the project dir, where scikick will be run
		os.chdir(self.project_dir.name)
	# delete the tmpdir/everything that was created
	def teardown(self):
		self.project_dir.cleanup()
	# running scikick with different arguments
	def test_add1(self):
		# SETUP
		assert os.system("%s init -yd" % cli_name) == 0
		files_rmd = list(map(lambda x: re.sub(".html$", ".Rmd", x), htmls))
		files_rmd = functools.reduce(lambda x, y: "%s %s" % (x, y), files_rmd)
		## FILES
		os.system("%s add %s" % (cli_name, files_rmd))
		## DEPS
		os.system("%s add %s -d %s" % (cli_name, "code/test_bash.Rmd",
			"code/test_bash.sh"))
		os.system("%s add %s -d %s" % (cli_name, "code/test_python.Rmd",
			"code/test_python.py"))
		os.system("%s add %s -d %s" % (cli_name, "code/analysis_summary.Rmd",
			"code/data_generate.Rmd"))
		os.system("%s add %s -d %s" % (cli_name, "code/analysis_normalization.Rmd",
			"code/analysis_summary.Rmd"))
		# RUN
		os.system("%s run" % cli_name)
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		for curr_file in htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
	def test_add2(self):
		# SETUP
		assert os.system("%s init -yd" % cli_name) == 0
		files_rmd = list(map(lambda x: re.sub(".html$", ".Rmd", x), htmls))
		files_rmd = functools.reduce(lambda x, y: "%s %s" % (x, y), files_rmd)
		## FILES
		# in this test case files are not added first (except for data_generate.Rmd)
		os.system("%s add %s" % (cli_name, "code/data_generate.Rmd"))
		## DEPS
		os.system("%s add %s -d %s" % (cli_name, "code/test_bash.Rmd",
			"code/test_bash.sh"))
		os.system("%s add %s -d %s" % (cli_name, "code/test_python.Rmd",
			"code/test_python.py"))
		os.system("%s add %s -d %s" % (cli_name, "code/analysis_summary.Rmd",
			"code/data_generate.Rmd"))
		os.system("%s add %s -d %s" % (cli_name, "code/analysis_normalization.Rmd",
			"code/analysis_summary.Rmd"))
		# RUN
		os.system("%s run" % cli_name)
		html_dir = os.path.join("report", "out_html")
		assert os.path.isdir(html_dir)
		for curr_file in htmls:
			assert os.path.isfile(os.path.join(html_dir, curr_file))
