"""functions used by 'sk status'"""
import os
import re
import subprocess
from scikick.yaml import yaml_in, get_indexes
from scikick.utils import reterr, warn, get_sk_exe_dir, get_sk_snakefile
from scikick.config import ScikickConfig

### How 'sk status' works:
# Snakemake output is parsed to assign flags to each scikick.yml file which
# indicate what will run and why it needs to run
#
# Details:
# `snakemake --dryrun --reason` output is parsed
# Each job has two lines of output:
#   One matches the pattern "^Job.*"
#   The other matches the pattern "^Reason.*"
# The Job line is used to figure out which file (of which script) is being processed and what type of job is being executed
# The Reason line describes which dependencies (if any) caused the job
#
## Expected patterns from snakemake output:
# Captures a comma-separated list of input files that have been modified
input_files_updated_pattern = "^.*Updated input files: (.*)$"
# Captures a comma-separated list of input files that will be modified
extupd_pattern = "^.*Input files updated by another job: (.*)$"
# 2 patterns needed for input files - cant go around the ';' sign with regex
intupd_pattern = f"^.*Updated input files: (.*)$"
intupd_pattern_sc = f"^.*Updated input files: (.*);.*$"
# Get the 'out_base' for exe(s) that will have an html generated
htmlgen_pattern = f"^Job.*: Converting .*out_md/(.*)\.md to .*out_html/(.*)\.html$"
# Determine which exe will be executed
exe_pattern = f"^Job.*: Executing code in (.*), outputting to .*$"
# Generic job/reason patterns
job_pattern = r"^Job \d+:.*$"
reason_pattern = "^Reason:.*$"

# get job/reason for internal debugging
def run_sk_dryrun(snakefile=get_sk_snakefile(),
    workdir=os.getcwd()):
    # get snakemake --dryrun output with --reason
    # TODO - use python API
    status = subprocess.run(
        ["snakemake", "--snakefile", snakefile, \
            "--directory", workdir, \
            "--dryrun", "--reason"], \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if status.returncode != 0:
        warn("sk: There was an error in snakemake --dry-run, see below")
        reterr(status.stdout.decode("utf-8"))

    stdout = status.stdout.decode("utf-8").split("\n")
    # Filter output for job/reason outputs only 
    stdout = list(filter(lambda l: re.match(job_pattern, l) is not None or 
                        re.match(reason_pattern, l) is not None, stdout))

    # Prevent status from return is something goes wrong
    #assert status.returncode == 0, "snakemake dryrun failed"

    # get "Job..." and "Reason:..." line pairs
    jobs = list(map(lambda i: stdout[i*2], range(0, int(len(stdout)/2))))
    reasons = list(map(lambda i: stdout[i*2+1], range(0, int(len(stdout)/2))))
    return jobs, reasons

# Main - called from sk_status()
def snake_status(snakefile=get_sk_snakefile(),
    workdir=os.getcwd(), verbose=False, rmd=None):
    """Print workflow status
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    rmd -- string (show status for just this file)
    """
    skconf = ScikickConfig(need_pages=True) # OR status with no pages just indicates whether index.html exists
    jobs, reasons = run_sk_dryrun(snakefile, workdir)
    # split jobs/reasons into types
    def subset_jobs(jobs,reasons,jtype):
        # Trying to use only exe_job info
        ret_jobs = []
        ret_reasons = []
        for i, _ in enumerate(jobs):
            if job_type(jobs[i]) == jtype:
                ret_jobs.append(jobs[i])
                ret_reasons.append(reasons[i])
        return ret_jobs, ret_reasons
    exe_jobs, exe_reasons = subset_jobs(jobs,reasons,"exe_to_md")
    md_jobs, md_reasons = subset_jobs(jobs,reasons,"md_to_html")
    unknown_jobs, unknown_reasons = subset_jobs(jobs,reasons,"unknown")

    exes = skconf.exes
    if skconf.index_exe not in exes:
        exes.append(skconf.index_exe)
    ## Parsing job/reason info from snakemake outputs
    # each function matches a snakemake reason string
    # get expected input updates for each script
    expected_input_updates = get_expected_input_updates(exes, exe_reasons, exe_jobs)
    # get updated inputs for each script
    updated_inputs = get_updated_inputs(exes, exe_reasons, exe_jobs)
    # get missing outputs (which are to be generated)
    missing_outs = missing_outputs(exe_reasons)

    ## Parsing job info only
    # get which scripts will be executed (processed as exe => md)
    exec_scripts = [re.match(exe_pattern,exe_job).groups()[0] for exe_job in
            exe_jobs]

    # get status markers (codes ---) for each script
    markers = file_markers(skconf,
                  updated_inputs,
                  expected_input_updates, missing_outs,
                  exec_scripts)

    # Add site status
    for job in md_jobs:
        match = re.match(htmlgen_pattern,job)
        # if the script has an html step fill in the gaps with ---
        if match is not None:
            out_base = match.groups()[0]
            md_job_exe = skconf.get_info(out_base,"exe")
            markers[md_job_exe] = ["-" if x == " " else x for x in
                    markers[md_job_exe]]

    # Checking for valid codes
    # Probably better to be more careful than do this
    nonexe_chars = [' ','-']
    for exe in exec_scripts:
        if all([x in nonexe_chars for x in markers[exe]]):
            markers[exe] = ['*','-','-']
            warn(f"sk: Warning: {exe} must execute for unknown reasons, (was scikick updated since last run?)")

    # Print status or a subset
    if rmd is not None:
        # print only the status of rmd and dependent files
        reduced_analysis = {k: skconf.analysis[k] for k in \
            filter(lambda k: k in skconf.exes, \
                flatten_dependency_tree(rmd, skconf))}
        print_status(reduced_analysis, markers, verbose)
    else:
        config = skconf.analysis
        # Adjustment for system index
        if skconf.index_exe not in config.keys():
            config['system index (homepage)'] = list() # has no inputs
            markers['system index (homepage)'] = markers[skconf.index_exe]
        print_status(config, markers, verbose)

def flatten_dependency_tree(exe, skconf):
    """Returns a list of rmd and its recursive deps"""
    file_list = [exe]
    if exe in skconf.exes and skconf.analysis[exe] is not None:
        for dep in skconf.analysis[exe]:
            file_list += flatten_dependency_tree(dep, skconf)
    return file_list

def file_markers(skconf, inupds, exinupds, missing_outs, exec_scripts):
    """Get markers for each file in scikick.yml
    This part extracts the implied meaning from the matches to snakemake reasons
    skconf -- ScikickConfig object
    inupds -- dict of updated inputs for each script (get_updated_inputs()) 
    exinupds -- dict of inputs expected to be updated for each script (get_expected_input_updates())
    """

    analysis = skconf.config["analysis"]
    reportdir = skconf.report_dir
    # extract all files from the analysis dict (i.e. files that will need markers)
    all_files = set()
    for script in skconf.exes:
        all_files.add(script)
        if skconf.analysis[script] is not None:
            for dep in analysis[script]:
                all_files.add(dep)
    if skconf.index_exe not in all_files:
        all_files.add(skconf.index_exe)
    # Assign markers to files
    # Start by collecting all possible markers for the file, then
    # choose the one with the highest priority
    # This will avoid any issues with the order of the ifs
    # Priorities:
    #     ? > m > s > e > u > - > ' '
    markers = dict()
    for _file in all_files:
        self_markers = [' ']
        ext_markers = [' ']
        int_markers = [' ']
        # assign "? ? ?" if the file doesn't exist
        if not os.path.isfile(_file):
            markers[_file] = ["?", "?", "?"]
            continue
        _file_is_index = _file == skconf.index_exe
        _file_is_exe = _file in skconf.exes or _file_is_index
        if _file_is_exe:
            #### SETUP
            # Get corresponding html and md files for the exe
            _file_md = skconf.get_info(_file,"md")
            _file_html = skconf.get_info(_file,"html")
            ### (*--) Main flag 
            # m if the file's md file doesn't exist
            if _file_md in missing_outs:
                self_markers.append("m")
            # s if the file was modified (newer relative to md file)
            if _file in inupds[_file]:
                self_markers.append('s')

            ### (_*_) External dependency flag
            allinupds = exinupds[_file] + inupds[_file]
            for jobinput in allinupds:
                input_is_out_md = skconf.get_info(jobinput,"md") == jobinput

                # Could this actually happen? Leaving this here to check
                input_is_files_md = jobinput == _file_md
                assert not input_is_files_md

                # i.e. if input file will be produced from another executable
                if input_is_out_md:
                    md_exe_origin = skconf.get_info(jobinput,"exe")
                    is_exinup = jobinput in exinupds[_file] # expected or has already been updated?
                    if is_exinup:
                        # exe=>md expected input file updates
                        # e if an external dependency must execute
                        #   i.e. something must execute before the script
                        assert md_exe_origin in exec_scripts
                        ext_markers.append('e')
                    else:
                        # exe=>md input files have been updated
                        # u if an external dependency was executed on a previous run
                        #   i.e. script must execute because something was updated
                        # i.e. _file must execute because an earlier step has run
                        assert md_exe_origin not in exec_scripts
                        ext_markers.append('u')

            ### (__*) Internal dependency flag
            # i if any internal dependencies have been updated
            deps = analysis[_file] if not _file_is_index else None
            deps = deps if (deps is not None) else list()
            # Note that exes in analysis will not be found in inupds values (their
            # md will be)
            any_intdep_modified = len(list(filter(lambda d: d in inupds[_file], deps))) > 0
            if any_intdep_modified:
                int_markers.append('s')
        else:
            # if _file was not in analysis.keys() it must be an internal
            # dependency
            # if _file is an internal dependency and modified, mark as s--
            # Scan all exes for detected updates to _file
            for key in inupds.keys():
                if _file in inupds[key]:
                    self_markers.append('s')

        def highest_priority_mark(marklist):
            """ Return the highest priority marker
            """
            mark_priorities = ['?','m','s','e','u','*','-',' ']
            idxs = []
            for mark in marklist:
                idxs.append(mark_priorities.index(mark))
            return mark_priorities[min(idxs)]
        markers[_file] = [' ',' ',' ']
        markers[_file][0] = highest_priority_mark(self_markers)
        markers[_file][1] = highest_priority_mark(ext_markers)
        markers[_file][2] = highest_priority_mark(int_markers)

        # complete the marker by adding "-" in empty places
        if markers[_file] != [" "," "," "]:
            markers[_file] = ["-" if x == " " else x for x in markers[_file]]
    return markers

def print_status(analysis, markers, verbose):
    """Print the output for 'sk status [-v]' using the generated file markers
    analysis -- analysis dict from scikick.yml
    markers -- dict of markers to print for each file
    verbose -- bool
    """
    for key in analysis.keys():
        if verbose:
            print(f" {''.join(markers[key])} \t{key}")
            if analysis[key] is not None:
                for dep in analysis[key]:
                    if ''.join(markers[dep]) != "   ":
                        print(f"({''.join(markers[dep])})\t  {dep}")
                    else:
                        print(f" {''.join(markers[dep])} \t  {dep}")
        else:
            if ''.join(markers[key]) != "   ":
                print(f" {''.join(markers[key])} \t{key}")

    # Counts of each job type
    rehtml_no = len(list(filter(lambda k: \
                                "".join(markers[k]) != "???" and \
                                "".join(markers[k]) != "   ", \
                                    analysis.keys())))
    reexec_no = len(list(filter(lambda k: \
                                "".join(markers[k]) != "   " and \
                                "".join(markers[k]) != "---" and \
                                "".join(markers[k]) != "???", \
                                    analysis.keys())))
    up2date_no = len(list(filter(lambda k: \
                                "".join(markers[k]) == "   ", \
                                    analysis.keys())))
    missing_no = len(list(filter(lambda k: \
                                "".join(markers[k]) == "???", \
                                    analysis.keys())))
    print(f"Scripts to execute: {reexec_no}")
    print(f"HTMLs to compile ('---'): {rehtml_no}")
    if verbose:
        print(f"Up to date ('   '): {up2date_no}")
    if missing_no > 0:
        print(f"Missing ('???'): {missing_no}")

def job_type(job):
    """ Get the job type (rule) from the job text
    job -- job string from Snakemake output
    outputs: md_to_html or exe_to_md or unknown
    """
    exe_match = re.match(exe_pattern, job)
    htmlgen_match = re.match(htmlgen_pattern, job)
    # Check which match succeeded
    if exe_match is not None:
        jtype = "exe_to_md"
    elif htmlgen_match is not None:
        jtype = "md_to_html"
    else:
        jtype = "unknown"
    return jtype

def job_to_script(job, skconf):
    """Get the exe-prefix that the "^Job.*" string refers to
    job -- job string from Snakemake output
    scripts -- list of possible scripts (scikick.yml analysis keys)
    """
    exe_match = re.match(exe_pattern, job)
    if exe_match is not None:
        return exe_match.groups()[0]

# Unused
class ScikickDryrunParser:
    def __init__(snakeout = None):
        if snakeout is None:
            self.job, self.reason = run_snake_status()

    def master_job_reason_parser(scripts,reasons,jobs):
        return

def get_expected_input_updates(scripts, reasons, jobs):
    """For each script list input files that are expected to be modified 
    (script: [list of updates])
    scripts -- list of scripts that are executed (listed in scikick.yml)
    reasons -- list of 'Reason' outputs from Snakemake
    jobs -- list of 'Job' outputs from Snakemake
    """
    extupd_dict = dict()
    for script in scripts:
        extupd_dict[script] = list()
    for i, _ in enumerate(reasons):
        match = re.match(extupd_pattern, reasons[i])
        if match is not None:
            assert job_type(jobs[i]) == "exe_to_md"
            script = re.match(exe_pattern,jobs[i]).groups()[0]
            to_update_files = match.groups()[0].split(", ")
            if script is not None:
                for upd_file in to_update_files:
                    assert len(upd_file) != 0
                    extupd_dict[script].append(upd_file)
    return extupd_dict

def get_updated_inputs(exes, reasons, jobs):
    """For each script get the the dictionary of scripts and dependencies that match to 
    snakemakes "Updated input files:" reason. 
    output (<script>: [list of updates]).
    Internal updates - files that are directly used (e.g. sourced scripts)
    exes -- list of exes that are executed (scikick.yml analysis)
    reasons -- list of 'Reason' outputs from Snakemake
    jobs -- list of 'Job' outputs from Snakemake
    """

    # initialize an empty list for each script
    intupd_dict = dict()
    for exe in exes:
        intupd_dict[exe] = list()
    for i, _ in enumerate(reasons):
        match = re.match(intupd_pattern, reasons[i])
        match_sc = re.match(intupd_pattern_sc, reasons[i])
        if match_sc is not None:
            match = match_sc
        if match is not None:
            assert job_type(jobs[i]) == "exe_to_md"
            script = re.match(exe_pattern,jobs[i]).groups()[0]
            updated_files = match.groups()[0].split(", ")
            assert script is not None
            # Is this necessary? Skip system index.Rmd file
            #
            #if script == os.path.join(get_sk_exe_dir(), "template","index.Rmd"):
            #    continue
            for upd_file in updated_files:
                if len(upd_file) != 0:
                    intupd_dict[script].append(upd_file)
    return intupd_dict

def missing_outputs(reasons):
    """Returns a list of files listed as 'Missing output files'"""
    missing_outs = list()
    miou_pattern = f"^.*Missing output files: (.*)$"
    miou_pattern_sc = f"^.*Missing output files: (.*);.*$"
    for reason in reasons:
        match = re.match(miou_pattern, reason)
        match_sc = re.match(miou_pattern_sc, reason)
        if match_sc is not None:
            match = match_sc
        if match is not None:
            missing_outs += match.groups()[0].split(", ")
    return missing_outs

