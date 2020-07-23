import os
import re
import subprocess
import tempfile
import shutil
import functools

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_status")
code_dir = os.path.join(test_datadir, "code")
yaml_file = os.path.join(test_datadir, "scikick.yml")
# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"

output_dir = os.path.join(test_datadir, "outputs")

class TestStatus:
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
	def test_status1(self):
		status = subprocess.Popen("%s status" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(output_dir, "output1.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
	def test_status2(self):
		os.system("sk run")
		status = subprocess.Popen("%s status" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(output_dir, "output2.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
	def test_status3(self):
		os.system("sk run")
		os.system("touch code/test_bash.sh")
		status = subprocess.Popen("%s status" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(output_dir, "output3.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
	def test_status3_v(self):
		os.system("sk run")
		os.system("touch code/test_bash.sh")
		status = subprocess.Popen("%s status -v" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(output_dir, "output3_v.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
	def test_status4(self):
		os.system("sk run")
		os.system("touch code/test_bash.sh")
		os.system("rm code/data_generate.Rmd")
		status = subprocess.Popen("%s status" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open(os.path.join(output_dir, "output4.txt"))
		assert current_output == \
			out_file.read()
		out_file.close()
	def test_status_empty_internal(self):
		curr_test_datadir = os.path.join(test_datadir,
			"..", "test_status_empty_internal")
		shutil.copytree(curr_test_datadir, "tsei")
		os.chdir("tsei")
		status = subprocess.Popen("%s status -v" % cli_name, shell=True,
			stdout=subprocess.PIPE)
		current_output = status.stdout.read().decode()
		out_file = open("status_v_output.txt")
		assert current_output == \
			out_file.read()
		out_file.close()
