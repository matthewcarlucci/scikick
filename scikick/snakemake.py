"""Functions that run snakemake with various arguments"""
import os
import re
import subprocess
import sys
from scikick.utils import warn, get_sk_snakefile, get_sk_exe_dir
from scikick.yaml import yaml_in, get_indexes


def match_print(line):
    """Print the line if it matches certain patterns"""
    done_match = re.match(".*All rules from .* are complete.*", line)
    ntbd_match = re.match(".*Nothing to be done..*", line)
    layout_match = re.match(".*Creating site layout from scikick.*", \
        line)
    html_match = re.match(".*Generating (.*) html page.*", line)
    skwarn_match = re.match("sk:.*", line)
    quit_fromlines_match = re.match("Quitting from lines.*", line)
    # Error matches:
    snakemake_lock_match = re.match("Error: Directory cannot be locked.*", line)
    missing_input_match = re.match("Missing input files for rule execute_code.*", line)
    if done_match is not None:
        warn("sk: Done, homepage is report/out_html/index.html")
    elif layout_match is not None:
        warn("sk: Creating site layouts from scikick.yml,"+ \
            " outputting to _site.yml files")
    elif html_match is not None:
        warn("sk: Generating %s.html" % html_match.groups()[0])
    elif ntbd_match is not None:
        warn("sk: Nothing to be done")
    elif skwarn_match is not None:
        warn(re.sub("\n$", "", line))
    elif quit_fromlines_match is not None:
        warn("sk: %s" % re.sub('\n$', '', line))
    elif snakemake_lock_match is not None:
        warn("sk: Error: Directory cannot be locked")
        warn("sk: Error: A snakemake process might already be running. To unlock, run:")
        warn("sk: Error:     sk run -v -s --unlock")
    elif missing_input_match is not None:
        warn("sk: Error: Missing files. Run 'sk status' to see which")

def run_snakemake(snakefile=get_sk_snakefile(), workdir=os.getcwd(), \
    verbose=False, dryrun=False, run_snakeargs=None, rmds=[]):
    """Run snakemake with specified arguments
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    dryrun -- bool
    run_snakeargs -- list (list of additional arguments to snakemake)
    """
    exe_dir = get_sk_exe_dir()
    yml = yaml_in()
    # logfile created by snakemake
    snake_logfile=""
    # what comes before 'snakemake'
    env_vars = f'SINGULARITY_BINDPATH="{exe_dir}"'
    # what comes after 'snakemake'
    snakemake_args = ""
    snakemake_args += f" --snakefile {snakefile}"
    snakemake_args += f" --directory {workdir}"
    snakemake_args += " --cores 1"
    # add rmds listed
    target_arg = ""
    index_rmds = get_indexes(yml)
    if len(rmds) > 0:
        for rmd in rmds:
            if rmd in yml["analysis"].keys():
                # if the rmd is the index
                if (len(index_rmds) == 1) and (index_rmds[0] == rmd):
                    target_arg += " " + os.path.join(yml["reportdir"], \
                        "out_html", "index.html")
                else:
                    target_arg += " " + os.path.join(yml["reportdir"], \
                        "out_html", os.path.splitext(rmd)[0] + ".html")
            else:
                warn(f"sk: Warning: {rmd} is not to be executed in scikick.yml")
    # config
    if dryrun:
        snakemake_args += " --dry-run"
    # overwrite scikick.yml snakemake_args if run_snakeargs given
    if run_snakeargs is not None:
        snakemake_args += f" {run_snakeargs}"
    elif 'snakemake_args' in yml.keys() and yml['snakemake_args'] is not None:
        snakemake_args += f" {' '.join(yml['snakemake_args'])}"
    # add the targets
    snakemake_args += f" {target_arg}"
    if verbose:
        sys.exit(subprocess.call(f"{env_vars} snakemake {snakemake_args}",
            shell=True))
    else:
        snake_p = subprocess.Popen(f"snakemake {snakemake_args}", \
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        warn("sk: Starting snakemake")
        lines = list()
        while True:
            line = snake_p.stderr.readline().decode('utf-8')
            if not line:
                break
            lines.append(line)
            match_print(line)
            logfile_name_match = re.match("^SK INTERNAL: logfile (.*)$", line)
            if logfile_name_match is not None:
                snake_logfile = logfile_name_match.groups()[0]
        snake_p.wait()
        if snake_p.returncode != 0:
            warn("sk: Warning: Snakemake returned a non-zero return code")
        if snake_logfile != "":
            warn(f"sk: Complete log: {snake_logfile}")
        sys.exit(snake_p.returncode)
