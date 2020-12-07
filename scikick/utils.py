"""General functions that did not fit into other modules"""
import os
import subprocess
import re
import sys
from shutil import copyfile

# getting the dir of the 'scikick' executable (i.e. this file)
def get_sk_exe_dir():
    """Returns scikick's system directory"""
    return os.path.dirname(os.path.realpath(__file__))

# getting the main snakefile for passing to snakemake
def get_sk_snakefile():
    """Returns the path to scikick's Snakefile"""
    return os.path.join(get_sk_exe_dir(), 'scripts', 'Snakefile')


def skdir():
    """Attempts to find the root directory of a scikick project"""
    curr_dir = os.getcwd()
    while os.path.normpath(curr_dir) != "/":
        if "scikick.yml" in os.listdir(curr_dir):
            return os.path.normpath(curr_dir)
        curr_dir = os.path.join(curr_dir, "..")
    return None


def pop_snakefile():
    """ Get the scikick snakefile for debugging. 
    Currently intended for scikick development only.
    """
    destfile = os.getcwd() + '/Snakefile'
    if os.path.isfile(destfile):
        warn("sk: Snakefile already exists in the current directory, exitting")
    else:
        warn("sk: Copied scikick's main Snakefile to current directory")
        copyfile(get_sk_snakefile(), destfile)

def check_version_r(package, version):
    """Check check whether supplied R libraries are installed
    and wether their versions are higher than
    packages -- library name
    versions -- version string
    """
    earlier_version = subprocess.run( \
        """ Rscript -e 'cat(packageVersion("%s") < "%s", "\n")' """ \
        % (package, version), shell = True, stdout = subprocess.PIPE)
    earlier_version = earlier_version.stdout.decode().strip().split("\n")[-1]
    if earlier_version == "TRUE":
        warn(f"sk: Warning: Version of {package} needs to be at least {version}")

def check_package_r(packages):
    """Check whether Rscript is available,
    then check whether supplied R libraries are installed
    packages -- list of libraries to be checked if installed
    """
    # check for R itself
    if subprocess.call("Rscript -e 'cat()'", \
        shell=True, stdout=open(os.devnull, "wb"), \
        stderr=open(os.devnull, "wb")) != 0:
        warn("sk: Error: R / Rscript not found")
        return 0
    # check for packages
    all_installed = 1
    installed_x = lambda x: subprocess.call(f"Rscript -e 'library({x})'", \
        shell=True, stdout=open(os.devnull, "wb"), \
        stderr=open(os.devnull, "wb"))
    for pkg in packages:
        if installed_x(pkg) != 0:
            warn(f"sk: Error: required R library '{pkg}' is not installed")
            all_installed = 0
    return all_installed


def check_version_generic(min_ver, program, level="Warning"):
    """Check version of a program by calling
    program --version
    in shell and parse the output.
    Then check whether the version is >= min_ver.
    Return 0 or 1 in case of failure or success respectively.
    min_ver -- version against which to compare
    program -- program to be called
    level -- string to be appended to 'sk: ' when printing warning messages
    """
    prog_version_p = subprocess.Popen(f"{program} --version", shell=True, \
        stdout=subprocess.PIPE, stderr=open(os.devnull, "wb"))
    prog_version_p.wait()
    if prog_version_p.returncode != 0:
        warn(f"sk: Warning: {program} not found")
        return 0
    # find the string, which, when divided by '.',
    # returns a list with len >= 2 and 0th and 1st elements are numbers
    version_strs = list(filter(lambda x: len(x.split('.')) >= 2 and \
        (x.split('.')[0].isdigit() and x.split('.')[1].isdigit()), \
        prog_version_p.stdout.readline().decode('utf-8').strip().split(' ')))
    if len(version_strs) == 0:
        warn(f"sk: Warning: Could not parse {program} version")
        return 1
    curr_v = tuple(map(int, version_strs[0].split('.')[0:2]))
    if curr_v < min_ver:
        warn(f"sk: {level}: {program} version " + \
            f">= {'.'.join(map(str, min_ver))} not found")
        return 0
    return 1

def check_requirements():
    """Performs a check for necessary and optional applications/packages"""
    warn("sk: Checking scikick software dependencies")
    # check for required package versions
    pandoc_ver_stat = check_version_generic((2, 0), "pandoc", "Error")
    r_ver_stat = check_package_r(["yaml", "knitr", "rmarkdown", "git2r"])
    check_version_r("git2r", "0.27")
    # exit if not sufficient / found
    if r_ver_stat == 0 or pandoc_ver_stat == 0:
        reterr("sk: Error: Required packages not found")
    # check for optional packages (warnings only)
    check_version_generic((2, 0), "git")
    # if exists
    check_version_generic((0, 0), "singularity")
    check_version_generic((0, 0), "conda")

def git_repo_url():
    """Parse git info regarding branches of the current repository.
    Returns a list of two elements:
    	- url to git repository
    In case of error, "." is returned
    """
    # result in case of error that would not break later
    remote = subprocess.run("Rscript -e 'cat(git2r::remote_url()[1])'",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if remote.returncode != 0:
        return "."
    # remote url
    remote_url = remote.stdout.decode()
    ssh_match = re.match("^git@.*:.*.git$", remote_url)
    https_match = re.match("^https://.*.git$", remote_url)
    if ssh_match is not None:
        return re.sub("^git@(.*):(.*).git$", "https://\\1/\\2", remote_url)
    elif https_match is not None:
        return re.sub(".git$", "", remote_url)
    else:
        return "."

def reterr(msg):
    """Print msg to stderr and exit with a non-zero status"""
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

def warn(msg):
    """Print msg to stderr"""
    sys.stderr.write("%s\n" % msg)


