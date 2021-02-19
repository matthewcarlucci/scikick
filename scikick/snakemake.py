"""Functions that run snakemake with various arguments"""
import os
import re
import subprocess
import sys
from scikick.utils import warn, get_sk_snakefile, get_sk_exe_dir
from scikick.yaml import yaml_in, get_indexes
import scikick.yaml
from scikick.config import ScikickConfig

# Functions for parsing snakemake output during run_snakemake
def detect_page_error(line):
    # Detect 'sk:' messages from scripts
    skwarn_match = re.match("sk:.*", line)
    if skwarn_match:
        sys.stderr.write(line)
    # Match output from loghandler.py
    skerr_match = re.match("sk: Error while .*",line)
    if skerr_match:
        return 1
    return 0

def detect_snakemake_progress(line, quiet=False):
    ntbd_match = re.match(".*Nothing to be done..*", line)
    job_match = re.match("^Job .*: (.*)$",line)
    if ntbd_match:
        warn("sk: Nothing to be done")
    elif job_match:
        # sanitize system index.Rmd path
        job_msg = job_match.groups()[0].replace(get_sk_exe_dir(),"system's ")
        if job_msg[0] ==' ' and quiet:
            return
        warn("sk: " + job_msg)


def detect_snakemake_error(line):
    """
    Return 1 if a snakemake error was detected
    """
    # Common Snakemake errors:
    snakemake_lock_match = re.match("Error: Directory cannot be locked.*", line)
    missing_input_match = re.match("Missing input files for rule .*", line)
    wflow_error_match =  re.match("WorkflowError:.*", line)
    # Snakemake errors (errors not related to analysis code)
    ret=1
    if snakemake_lock_match:
        warn("sk: Error: Directory cannot be locked")
        warn("sk: Error: A snakemake process might already be running. To unlock, run:")
        warn("sk: Error:     sk run -v -s --unlock")
    elif missing_input_match:
        warn("sk: Error: Missing files. Run 'sk status' to see which")
    elif wflow_error_match:
        warn("sk: Error: Snakemake WorkflowError")
    else:
        ret=0
    return ret

def run_snakemake(snakefile=get_sk_snakefile(), workdir=os.getcwd(), \
    verbose=False, dryrun=False, snakeargs=None, rmds=[], quiet=False):
    """Run snakemake with specified arguments
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    dryrun -- bool
    snakeargs -- list (list of additional arguments to snakemake)
    rmds -- string rmd who's output should be targetted
    """
    exe_dir = get_sk_exe_dir()
    loghandler = os.path.join(exe_dir, 'workflow/loghandler.py')

    skconf = ScikickConfig()
    yml = skconf.config

    # logfile created by snakemake
    snake_logfile=""

    ### Construct call to snakemake
    # before 'snakemake'
    env_vars = f'SINGULARITY_BINDPATH="{exe_dir}"'
    # after 'snakemake'
    snakemake_args = ""
    snakemake_args += f" --snakefile {snakefile}"
    snakemake_args += f" --directory '{workdir}'"
    snakemake_args += " --cores 1"
    snakemake_args += f" --log-handler-script {loghandler}"

    # Translate Rmd script to HTML target 
    # TODO - factor out
    # TODO - move this to sk_run as an additional snake_arg
    # to reduce skconfig read ins
    target_arg = ""
    if len(rmds) > 0:
        for rmd in rmds:

            # Try to add rmd if it is not in scikick.yml
            if yml['analysis'] is None:
                rmd_found = False
            elif rmd not in yml["analysis"].keys():
                rmd_found = False
            else:
                rmd_found = True
            if not rmd_found:
                warn(f"sk: Warning: {rmd} was not found in scikick.yml")
                if os.path.exists(rmd):
                    scikick.yaml.add([rmd])
                    # Must reload or modify the yml since it changed
                    skconf = ScikickConfig()
                    yml = skconf.config
                else:
                    warn(f"sk: Warning: Will not try to add non-existing file {rmd}")
                    return 0

            # Set target. Index file is treated differently
            index_rmds = get_indexes(yml)
            if (len(index_rmds) == 1) and (index_rmds[0] == rmd):
                target_arg += " " + os.path.join(yml["reportdir"], \
                    "out_html", "index.html")
            else:
                target_arg += " " + os.path.join(yml["reportdir"], \
                    "out_html", os.path.splitext(rmd)[0] + ".html")

    # set more snakemake arguments
    if dryrun:
        snakemake_args += " --dry-run"
    # Add user defined snakemake arguments
    if snakeargs is not None:
        snakemake_args += f" {snakeargs}"
    if 'snakemake_args' in yml.keys() and yml['snakemake_args'] is not None:
        warn("sk: Warning: snakemake_args is deprecated")
        snakemake_args += f" {' '.join(yml['snakemake_args'])}"
    # add the implied targets (html of Rmd)
    snakemake_args += f" {target_arg}"
    # Check for a user defined snakefile (imported by scikick Snakefile)
    user_snakefile = os.path.join(os.getcwd(), "Snakefile")
    if os.path.isfile(user_snakefile):
        warn("sk: Including Snakefile found in project directory")
    ### Execution
    if verbose:
        warn("sk: Starting snakemake")
        cmd = f"{env_vars} snakemake {snakemake_args}"
        print(cmd)
        sys.exit(subprocess.call(cmd, shell=True))
    else:
        snake_p = subprocess.Popen(f"snakemake {snakemake_args}", \
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logs=[]
        sm_err = 0
        page_err = 0
        while True:
            line = snake_p.stdout.readline().decode('utf-8')
            if not line:
                break
            # Capture logs
            logs.append(line)

            # Report progress
            detect_snakemake_progress(line,quiet)
            page_err = detect_page_error(line) or page_err

            # In case of snakemake error start writing stderr
            sm_err += detect_snakemake_error(line)
            if sm_err:
                sys.stderr.write(line) 

            logfile_name_match = re.match("^SK INTERNAL: logfile (.*)$", line)
            if logfile_name_match is not None:
                # Use the first found match
                if snake_logfile == "":
                    snake_logfile = logfile_name_match.groups()[0]
        snake_p.wait()
        if snake_p.returncode != 0:
            if not page_err:
                warn("sk: Error: Snakemake returned a non-zero return code")
                if not sm_err:
                    warn("sk: Warning: scikick was unable to find snakemake error in logs, dumping stderr...")
                    for line in logs:
                        sys.stderr.write(line)
                    return snake_p.returncode
        else:
            if not os.path.exists(skconf.homepage):
                warn(f"sk: Warning: Expected homepage {skconf.homepage} is missing")
        if snake_logfile != "":
            rellog=os.path.relpath(snake_logfile,start=os.getcwd())
            if snake_p.returncode!=0:
                warn(f"sk: Complete log: {rellog}")
        return snake_p.returncode
