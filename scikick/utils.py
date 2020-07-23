"""General functions that did not fit into other modules"""
import os
import subprocess
import re
import sys
from git import Repo
from git import InvalidGitRepositoryError, NoSuchPathError

# getting the dir of the 'scikick' executable (i.e. this file)
def get_sk_exe_dir():
    """Returns scikick's system directory"""
    return os.path.dirname(os.path.realpath(__file__))

# getting the main snakefile for passing to snakemake
def get_sk_snakefile():
    """Returns the path to the scikick's Snakefile"""
    return os.path.join(get_sk_exe_dir(), 'usr', 'Snakefile')


def check_version_r(packages):
    """Check vhether Rscript is available,
    then check whether supplied R libraries are installed
    packages -- list of libraries to be checked if installed
    """
    # check for R itself
    warn("sk: Checking if Rscript is available")
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
        warn(f"sk: Checking if R library '{pkg}' is installed")
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
    warn(f"sk: Checking {program} version")
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
    # check for required package versions
    pandoc_ver_stat = check_version_generic((2, 0), "pandoc", "Error")
    r_ver_stat = check_version_r(['yaml', 'knitr', 'rmarkdown'])
    # exit if not sufficient / found
    if r_ver_stat == 0 or pandoc_ver_stat == 0:
        reterr("sk: Error: Required packages not found")
    # check for optional packages (warnings only)
    check_version_generic((2, 0), "git")
    # if exists
    check_version_generic((0, 0), "singularity")
    check_version_generic((0, 0), "conda")

def git_info():
    """Parse git info regarding branches of the current repository.
    Returns a list of two elements:
    	- url to git repository
    	- url to git repository of the current branch
    Works with gitlab and github
    In case of error, [".", "."] is returned
    Used in scikick/usr/Snakefile
    """
    # result in case of error that would not break later
    rep_branch = [".", "."]
    try:
        gitobj = Repo()
    except NoSuchPathError:
        warn("sk: Warning: invalid path to a git repository")
        return rep_branch
    except InvalidGitRepositoryError:
        warn("sk: Warning: not a git repository")
        return rep_branch
    # remote url
    remote = list(gitobj.remote().urls)[0]
    ssh_match = re.match("^git@.*:.*.git$", remote)
    https_match = re.match("^https://.*.git$", remote)
    if ssh_match is not None:
        remote = re.sub("^git@(.*):(.*).git$", "https://\\1/\\2", remote)
    elif https_match is None:
        warn("sk: Unrecognized git repository format")
        return rep_branch
    # branch url
    rep_branch[0] = remote
    rep_branch[1] = "%s/tree/%s" % (remote, gitobj.active_branch.name)
    return rep_branch

def reterr(msg):
    """Print msg to stderr and exit with a non-zero status"""
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

def warn(msg):
    """Print msg to stderr"""
    sys.stderr.write("%s\n" % msg)

def skdir():
    """Returns the root directory of a scikick project"""
    curr_dir = os.getcwd()
    while os.path.normpath(curr_dir) != "/":
        if "scikick.yml" in os.listdir(curr_dir):
            return os.path.normpath(curr_dir)
        curr_dir = os.path.join(curr_dir, "..")
    return None
