"""Functions that run snakemake with various arguments"""
import os
import re
import subprocess
import sys
from scikick.utils import warn, get_sk_snakefile, get_sk_exe_dir
from scikick.yaml import yaml_in


def match_print(line):
    """Print the line if it matches certain patterns"""
    done_match = re.match(".*All rules from .* are complete.*", line)
    ntbd_match = re.match(".*Nothing to be done..*", line)
    layout_match = re.match(".*Creating site layout from scikick.*", \
        line)
    html_match = re.match(".*Generating (.*) html page.*", line)
    skwarn_match = re.match("sk:.*", line)
    quit_fromlines_match = re.match("Quitting from lines.*", line)
    complete_log_match = re.match("Complete log.*", line)
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
    elif complete_log_match is not None:
        warn("sk: %s" % re.sub("\n$", "", line))

def run_snakemake(snakefile=get_sk_snakefile(), workdir=os.getcwd(), \
    verbose=False, dryrun=False, run_snakeargs=None):
    """Run snakemake with specified arguments
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    dryrun -- bool
    run_snakeargs -- list (list of additional arguments to snakemake)
    """
    exe_dir = get_sk_exe_dir()
    yml = yaml_in()
    snakemake_args = ""
    snakemake_args += f" --singularity-args=\"--bind {exe_dir}\" "
    snakemake_args += f" --snakefile {snakefile}"
    snakemake_args += f" --directory {workdir}"
    snakemake_args += " --cores 1"
    # config
    if dryrun:
        snakemake_args += " --dry-run"
    # overwrite scikick.yml snakemake_args if run_snakeargs given
    if run_snakeargs is not None:
        snakemake_args += f" {run_snakeargs}"
    elif 'snakemake_args' in yml.keys() and yml['snakemake_args'] is not None:
        snakemake_args += f" {' '.join(yml['snakemake_args'])}"

    if verbose:
        sys.exit(subprocess.call(f"snakemake {snakemake_args}", shell=True))
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
        snake_p.wait()
        sys.exit(snake_p.returncode)
