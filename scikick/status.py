"""functions used by 'sk status'"""
import os
import re
import subprocess
from scikick.yaml import yaml_in
from scikick.utils import warn, get_sk_exe_dir

## How 'sk status' works:
# `snakemake --dryrun --reason` is executed
# each job has two description lines:
#   One matches the pattern "^Job.*"
#   The other matches the pattern "^Reason.*"
# The Job line is used to figure out which file (of which script) is being processed
# The Reason line describes which dependencies (if any) caused the job

# Examples of patterns from which certain information is parsed:
## "^.*Updated input files: (.*)$"
### captures a comma-separated list of internal updates
## "^Job.*: Generating .*/out_html/(.*) html page$"
### message from snakefile used to determine which script will have an html generated
## "^.*Input files updated by another job: (.*)$"
### captures a comma-separated list of md files of external dependencies

# Flags are set according to the lists of files parsed from specific snakemake outputs

def snake_status(snakefile, workdir, verbose=False, rmd=None):
    """Print workflow status
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    rmd -- string
    """
    # read the yaml
    yaml = yaml_in(need_pages=True)
    scripts = list(yaml["analysis"].keys())
    # get which script will be used to create the main index.html (homepage)
    index_list = list(filter(lambda f: \
        os.path.splitext(os.path.basename(f))[0] == "index", \
        scripts))
    index_file = None if len(index_list) != 1 else index_list[0]

    # get snakemake dryrun output with '--reason'
    status = subprocess.run(
        ["snakemake", "--snakefile", snakefile, \
            "--directory", workdir, \
            "--dryrun", "--reason"], \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    stdout = status.stdout.decode("utf-8").split("\n")
    stdout = list(filter(lambda l: re.match(r"^Job \d+:.*$", l) is not None or \
                         re.match("^Reason:.*$", l) is not None, stdout))
    # get "Job..." and "Reason:..." line pairs
    jobs = list(map(lambda i: stdout[i*2], range(0, int(len(stdout)/2))))
    reasons = list(map(lambda i: stdout[i*2+1], range(0, int(len(stdout)/2))))
    ## Parsing info from snakemake outputs
    # get external updates for each script
    extupds = external_updates(scripts, reasons, jobs)
    # get internal updates for each script
    intupds = internal_updates(scripts, reasons, jobs)
    # get missing outputs (which are to be generated)
    missing_outs = missing_outputs(reasons)
    # get which scripts will be executed (processed as rmd => md)
    exec_scripts = to_execute(jobs)
    # get status markers (codes ---) for each script
    markers = file_markers(yaml, intupds, extupds, missing_outs, exec_scripts, index_file)
    if rmd is not None:
        # print only the status of rmd and dependent files
        reduced_analysis = {k: yaml["analysis"][k] for k in \
            filter(lambda k: k in yaml["analysis"].keys(), \
                flatten_dependency_tree(rmd, yaml["analysis"]))}
        print_status(reduced_analysis, markers, verbose)
    else:
        print_status(yaml["analysis"], markers, verbose)

def flatten_dependency_tree(rmd, analysis):
    """Returns a list of rmd and its recursive deps"""
    file_list = [rmd]
    if rmd in analysis.keys() and analysis[rmd] is not None:
        for dep in analysis[rmd]:
            file_list += flatten_dependency_tree(dep, analysis)
    return file_list

def file_markers(config, intupds, extupds, missing_outs, exec_scripts, index_file):
    """Get markers for each file in scikick.yml
    config -- dict of scikick.yml
    intupds -- output from internal_updates()
    extupds -- output from external_updates()
    index_file -- name of the homepage rmd
    """
    analysis = config["analysis"]
    reportdir = config["reportdir"]
    # extract all files from the analysis dict (files that will need markers)
    all_files = set()
    for script in analysis.keys():
        all_files.add(script)
        if analysis[script] is not None:
            for dep in analysis[script]:
                all_files.add(dep)
    markers = dict()
    # assign markers to files
    # since the assignment of each symbol of the flag is done sequentially,
    # each symbol can be overwritten by the next check,
    # so the order of 'if' statements is important. Priorities are:
    #     ?>m>s>e>u>->' '
    for _file in all_files:
        markers[_file] = [" ", " ", " "]
        # assign "? ? ?" if the file doesn't exist
        if not os.path.isfile(_file):
            markers[_file] = ["?", "?", "?"]
            continue
        # if the file is a script 
        if _file in analysis.keys():
            #### SETUP
            # define corresponding html and md files for the rmd
            _file_md = os.path.join(os.path.join(reportdir, "out_md"), \
                os.path.splitext(_file)[0] + ".md")
            _file_html = os.path.join(os.path.join(reportdir, "out_html"), \
                os.path.splitext(_file)[0] + ".html")
            # in case the script generates the homepage, md and html names are generated differently
            if _file == index_file:
                _file_md = os.path.join(os.path.join(reportdir, "out_md"), \
                    "index.md")
                _file_html = os.path.join(os.path.join(reportdir, "out_html"), \
                    "index.html")
            ### (*--) Main flag 
            # - if the html must be generated
            site_file_update = "_site.yml" in map(os.path.basename, extupds[_file])
            _file_html_missing = not os.path.isfile(_file_html)
            _file_html_update = _file_md in intupds[_file]
            if site_file_update or _file_html_missing or _file_html_update:
                markers[_file][0] = "-"
            # m if the file's md file doesn't exist
            if _file_md in missing_outs:
                markers[_file][0] = "m"
            # s if the file was modified (newer relative to md file)
            if _file in intupds[_file]:
                markers[_file][0] = "s"
            ### (_*_) External dependency flag
            # e if an external dependency must execute
            # u if an external dependency md was -
            # e>u
            for upd in extupds[_file] + intupds[_file]:
                md_match = re.match(f"^{reportdir}/out_md/.*.md$", upd)
                if (md_match is not None) and upd != _file_md:
                    # if the md does not have a corresponding script, *u*, else *e*
                    if os.path.splitext(re.sub(pattern=f"{reportdir}/out_md/", \
                        repl="", string=upd))[0] not in \
                        map(lambda x: os.path.splitext(x)[0], exec_scripts):
                        markers[_file][1] = "u"
                    else:
                        markers[_file][1] = "e"
            ### (__*) Internal dependency flag 
            # i if any internal dependencies have been updated
            deps = analysis[_file]
            deps = deps if (deps is not None) else list()
            any_intdep_modified = len(list(filter(lambda d: d in intupds[_file], deps))) > 0
            if any_intdep_modified:
                markers[_file][2] = "i"
        else:
            # if is an internal dependency and modified, mark as s--
            for key in intupds.keys():
                if _file in intupds[key]:
                    markers[_file] = ["s", "-", "-"]
        # complete the marker by adding "-" in empty places
        if "".join(markers[_file]) != "   ":
            for i in range(3):
                if markers[_file][i] == " ":
                    markers[_file][i] = "-"
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

def job_to_script(job, scripts):
    """Get the script that the "^Job.*" string refers to
    job -- job string from Snakemake output
    scripts -- list of possible scripts (scikick.yml analysis keys)
    """
    exe_pattern = f"^Job.*: Executing R code in (.*), outputting to (.*)$"
    htmlgen_pattern = f"^Job.*: Converting .* to .*/out_html/(.*)\.html$"
    noext_scripts = list(map(lambda x: os.path.splitext(x)[0], scripts))
    # Get both matches
    exe_match = re.match(exe_pattern, job)
    htmlgen_match = re.match(htmlgen_pattern, job)
    # Check which match succeeded
    if exe_match is not None:
        return exe_match.groups()[0]
    elif htmlgen_match is not None:
        htmlgen_match_string = htmlgen_match.groups()[0]
        if htmlgen_match_string in noext_scripts:
            return list(filter(lambda x: \
                        os.path.splitext(x)[0] == htmlgen_match_string,
                               scripts))[0]

def external_updates(scripts, reasons, jobs):
    """Get the dictionary of external updates for each script (script: [list of updates])
    External updates - files that are not directly used (e.g. other Rmds),
    so the outputs (md files) of those rmds are the dependencies
    scripts -- list of scripts that are executed (listed in scikick.yml)
    reasons -- list of 'Reason' outputs from Snakemake
    jobs -- list of 'Job' outputs from Snakemake
    """
    extupd_dict = dict()
    for script in scripts:
        extupd_dict[script] = list()
    for i, _ in enumerate(reasons):
        extupd_pattern = f"^.*Input files updated by another job: (.*)$"
        match = re.match(extupd_pattern, reasons[i])
        if match is not None:
            script = job_to_script(jobs[i], scripts)
            updated_files = match.groups()[0].split(", ")
            if script is not None:
                for upd_file in updated_files:
                    if len(upd_file) != 0:
                        extupd_dict[script].append(upd_file)
    return extupd_dict

def internal_updates(scripts, reasons, jobs):
    """Get the dictionary of internal updates for each script (script: [list of updates])
    Internal updates - files that are directly used (e.g. sourced scripts)
    scripts -- list of scripts that are executed (listed in scikick.yml)
    reasons -- list of 'Reason' outputs from Snakemake
    jobs -- list of 'Job' outputs from Snakemake
    """
    intupd_dict = dict()
    for script in scripts:
        intupd_dict[script] = list()
    for i, _ in enumerate(reasons):
        # simple solution currently - cant go around the ';' sign with regex
        intupd_pattern = f"^.*Updated input files: (.*)$"
        intupd_pattern_sc = f"^.*Updated input files: (.*);.*$"
        match_sc = re.match(intupd_pattern_sc, reasons[i])
        match = re.match(intupd_pattern, reasons[i])
        if match_sc is not None:
            match = match_sc
        if match is not None:
            script = job_to_script(jobs[i], scripts)
            updated_files = match.groups()[0].split(", ")
            if script is not None:
                # Skip system index.Rmd file
                if script == \
                    os.path.join(get_sk_exe_dir(), "template","index.Rmd"):
                    continue
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

def to_execute(jobs):
    """Returns a list of files listed as 'Executing R code in',
    the ones that will be executed ond processed into md files"""
    exec_files = list()
    exec_pattern = f"^.*Executing R code in (.*), outputting to.*$"
    for job in jobs:
        match = re.match(exec_pattern, job)
        if match is not None:
            exec_files.append(match.groups()[0])
    return exec_files
