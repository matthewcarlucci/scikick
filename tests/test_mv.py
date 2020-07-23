import os
import re
import tempfile
import shutil
import functools
import subprocess
from scikick.yaml import yaml_in

exe_dir = os.path.dirname(os.path.realpath(__file__))
test_datadir = os.path.join(exe_dir, "data", "test_mv")
# get scikick cli name
#exec(open(os.path.join(exe_dir, "cli_name.py")).read())
cli_name = "sk"
command = "tree; cat scikick.yml"

class TestMv:
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
	def test_mv1(self):
		os.chdir("file_to_file")
		assert os.system("sk run") == 0
		assert os.system("`cat command.txt`") == 0
		out_file = open("out.txt")
		desired_output = out_file.read()
		out_file.close()
		command_result = subprocess.run(command, shell=True,
			stdout=subprocess.PIPE).stdout.decode()
		assert command_result == desired_output
	def test_mv2(self):
		os.chdir("file_to_dir")
		assert os.system("sk run") == 0
		assert os.system("`cat command.txt`") == 0
		out_file = open("out.txt")
		desired_output = out_file.read()
		out_file.close()
		command_result = subprocess.run(command, shell=True,
			stdout=subprocess.PIPE).stdout.decode()
		assert command_result == desired_output
	def test_mv3(self):
		os.chdir("dir_to_existing_dir")
		assert os.system("sk run") == 0
		assert os.system("`cat command.txt`") == 0
		out_file = open("out.txt")
		desired_output = out_file.read()
		out_file.close()
		command_result = subprocess.run(command, shell=True,
			stdout=subprocess.PIPE).stdout.decode()
		assert command_result == desired_output
	def test_mv4(self):
		os.chdir("dir_to_nonexisting_dir")
		assert os.system("sk run") == 0
		assert os.system("`cat command.txt`") == 0
		out_file = open("out.txt")
		desired_output = out_file.read()
		out_file.close()
		command_result = subprocess.run(command, shell=True,
			stdout=subprocess.PIPE).stdout.decode()
		assert command_result == desired_output
	def test_mv5(self):
		os.chdir("multiple_to_dir")
		assert os.system("sk run") == 0
		assert os.system("`cat command.txt`") == 0
		out_file = open("out.txt")
		desired_output = out_file.read()
		out_file.close()
		command_result = subprocess.run(command, shell=True,
			stdout=subprocess.PIPE).stdout.decode()
		assert command_result == desired_output
	def test_mv6(self):
		os.chdir("multiple_to_file")
		assert os.system("`cat command.txt`") != 0
	def test_mv7(self):
		os.chdir("multiple_to_nonexistant")
		assert os.system("`cat command.txt`") != 0
