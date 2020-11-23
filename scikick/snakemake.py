"""Functions that run snakemake with various arguments"""
import os
import re
import subprocess
import sys
from scikick.utils import warn, get_sk_snakefile, get_sk_exe_dir
from scikick.yaml import yaml_in, get_indexes
import scikick.yaml

# Functions for parsing snakemake output during run_snakemake
def detect_page_error(line):
    # Detect messages from other scripts
    skwarn_match = re.match("sk:.*", line)
    if skwarn_match:
        warn(re.sub("\n$", "", line))
    return skwarn_match

def detect_snakemake_progress(line):
    done_match = re.match(".*All rules from .* are complete.*", line)
    ntbd_match = re.match(".*Nothing to be done..*", line)
    layout_match = re.match(".*Creating site layout from scikick.*", \
        line)
    html_match = re.match(".*Generating (.*) html page.*", line)
    # No longer used 
    #quit_fromlines_match = re.match("Quitting from lines.*", line)
    if done_match:
        warn("sk: Done, homepage is report/out_html/index.html")
    elif layout_match:
        warn("sk: Creating site layouts from scikick.yml,"+ \
            " outputting to _site.yml files")
    elif html_match:
        warn("sk: Generating %s.html" % html_match.groups()[0])
    elif ntbd_match:
        warn("sk: Nothing to be done")
    # No longer used
    #elif quit_fromlines_match:
    #    msg = re.sub('\n$', '', line)
    #    warn(f"sk: {msg}")

def detect_snakemake_error(line):
    """
    Return 1 if a snakemake error was detected
    """
    # Common Snakemake errors:
    snakemake_lock_match = re.match("Error: Directory cannot be locked.*", line)
    missing_input_match = re.match("Missing input files for rule execute_code.*", line)
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
    verbose=False, dryrun=False, run_snakeargs=None, rmds=[]):
    """Run snakemake with specified arguments
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    dryrun -- bool
    run_snakeargs -- list (list of additional arguments to snakemake)
    rmds -- string rmd who's output should be targetted
    """
    exe_dir = get_sk_exe_dir()
    yml = yaml_in()
    # logfile created by snakemake
    snake_logfile=""
    
    ### Construct call to snakemake
    # before 'snakemake'
    env_vars = f'SINGULARITY_BINDPATH="{exe_dir}"'
    # after 'snakemake'
    snakemake_args = ""
    snakemake_args += f" --snakefile {snakefile}"
    snakemake_args += f" --directory {workdir}"
    snakemake_args += " --cores 1"
   
    # Translate Rmd script to HTML target 
    # TODO - factor out
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
                    yml = yaml_in() # Must reload the yml since it changed
                else:
                    warn(f"sk: Warning: Will not try to add non-existing file {rmd}")
                    return

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
    if run_snakeargs is not None:
        snakemake_args += f" {run_snakeargs}"
    elif 'snakemake_args' in yml.keys() and yml['snakemake_args'] is not None:
        warn("sk: Warning: snakemake_args is deprecated")
        snakemake_args += f" {' '.join(yml['snakemake_args'])}"
    # add the implied targets (html of Rmd)
    snakemake_args += f" {target_arg}"

    ### Execution
    if verbose:
        warn("sk: Starting snakemake")
        sys.exit(subprocess.call(f"{env_vars} snakemake {snakemake_args}",
            shell=True))
    else:
        snake_p = subprocess.Popen(f"snakemake {snakemake_args}", \
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logs=[]
        sm_err = 0
        page_err = None
        while True:
            line = snake_p.stderr.readline().decode('utf-8')
            if not line:
                break
            # Capture logs
            logs.append(line)
            
            # Report progress
            detect_snakemake_progress(line)
            page_err = detect_page_error(line) or page_err
            
            # In case of snakemake error start writing stderr
            sm_err += detect_snakemake_error(line)
            if sm_err:
                sys.stderr.write(line) 

            logfile_name_match = re.match("^SK INTERNAL: logfile (.*)$", line)
            if logfile_name_match is not None:
                snake_logfile = logfile_name_match.groups()[0]
        snake_p.wait()
        if snake_p.returncode != 0:
            warn("sk: Error: Snakemake returned a non-zero return code")
            if not page_err and not sm_err:
                warn("sk: Warning: scikick was unable to find snakemake error in logs, dumping stderr...")
                for line in logs:
                    sys.stderr.write(line)
                sys.exit(snake_p.returncode)
        if snake_logfile != "":
            warn(f"sk: Complete log: {snake_logfile}")
        sys.exit(snake_p.returncode)
