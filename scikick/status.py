"""functions used by 'sk status'"""
import os
import re
import subprocess
from scikick.yaml import yaml_in
from scikick.utils import warn, get_sk_exe_dir

def snake_status(snakefile, workdir, verbose):
    """Print workflow status
    snakefile -- string (path to the main snakefile)
    workdir -- string
    verbose -- bool
    """
    # read the yaml
    yaml = yaml_in()
    if yaml['analysis'] is None or len(yaml['analysis']) == 0:
        warn("sk: Warning: no pages have been added to scikick.yaml, " + \
            "this can be done with\nsk: sk add my.rmd")
        return
    # useful variables
    scripts = list(yaml["analysis"].keys())
    # get the index file
    index_list = list(filter(lambda f: \
        os.path.splitext(os.path.basename(f))[0] == "index", \
        scripts))
    index_file = None if len(index_list) != 1 else index_list[0]

    status = subprocess.run(
        ["snakemake", "--snakefile", snakefile, \
            "--directory", workdir, \
            "--dryrun", "--reason"], \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    # get snakemake dryrun output with '--reason'
    stdout = status.stdout.decode("utf-8").split("\n")
    stdout = list(filter(lambda l: re.match(r"^Job \d+:.*$", l) is not None or \
                         re.match("^Reason:.*$", l) is not None, stdout))
    # get "Job..." and "Reason:..."
    jobs = list(map(lambda i: stdout[i*2], range(0, int(len(stdout)/2))))
    reasons = list(map(lambda i: stdout[i*2+1], range(0, int(len(stdout)/2))))
    ## Parsing info from snakemake outputs
    # Get external upadtes for each script
    extupds = external_updates(scripts, reasons, jobs)
    # Get internal upadtes for each script
    intupds = internal_updates(scripts, reasons, jobs)
    markers = file_markers(scripts, yaml, intupds, extupds, index_file)
    print_status(yaml["analysis"], markers, verbose)

def file_markers(scripts, config, intupds, extupds, index_file):
    """Get markers for each file in scikick.yml
    scripts -- list of keys of the analysis dict
    analysis -- analysi dict from scikick.yml
    reportdir -- reportdir from scikick.yml
    intupds -- output from internal_updates()
    extupds -- output from external_updates()
    """
    analysis = config["analysis"]
    reportdir = config["reportdir"]
    # Get all files
    all_files = set()
    for script in scripts:
        all_files.add(script)
        if analysis[script] is not None:
            for dep in analysis[script]:
                all_files.add(dep)
    markers = dict()
    # assign markers to files
    for _file in all_files:
        markers[_file] = [" ", " ", " "]
        # file doesn't exist
        if not os.path.isfile(_file):
            markers[_file] = ["?", "?", "?"]
            continue
        if _file in scripts:
            _file_md = os.path.join(os.path.join(reportdir, "out_md"), \
                os.path.splitext(_file)[0] + ".md")
            # script's md does not exist
            if not os.path.isfile(_file_md):
                if _file != index_file:
                    markers[_file] = ["m", "-", "-"]
                    continue
                elif not os.path.isfile(os.path.join(\
                    reportdir, "out_md", "index.md")):
                    markers[_file] = ["m", "-", "-"]
                    continue
            # html is to be generated
            if "_site.yml" in map(os.path.basename, extupds[_file]):
                markers[_file][0] = "-"
            # script itself was modified
            #if _file_md in extupds[_file] and _file in intupds[_file]:
            if _file in intupds[_file]:
                markers[_file][0] = "s"
            # script's external dependencies have been updated
            for ext_upd in extupds[_file]:
                is_script = ext_upd in map(lambda x: os.path.join( \
                    os.path.join(reportdir, "out_md"),
                    os.path.splitext(x)[0] + ".md"), scripts)
                if is_script and ext_upd != _file_md:
                    markers[_file][1] = "e"
            # script's internal dependencies have been updated
            if len(intupds[_file]) > 0 + (_file in intupds[_file]) + \
                (_file_md in intupds[_file]) + \
                ("_site.yml" in map(os.path.basename, intupds[_file])):
                markers[_file][2] = "i"
        else:
            # if not a script and modified mark "s--"
            for key in intupds.keys():
                if _file in intupds[key]:
                    markers[_file] = ["s", "-", "-"]
        # complete the marker
        if "".join(markers[_file]) != "   ":
            for i in range(3):
                if markers[_file][i] == " ":
                    markers[_file][i] = "-"
    return markers

def print_status(analysis, markers, verbose):
    """Print the output for 'sk status'
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
    """Get the script that is executed in a job
    job -- job string from Snakemake output
    scripts -- list of scripts that are executed (listed in scikick.yml)
    """
    exe_pattern = f"^Job.*: Executing R chunks in (.*), outputting to (.*)$"
    htmlgen_pattern = f"^Job.*: Generating .*/out_html/(.*) html page$"
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
    """Get the dictionary of external updates for each script
    External updates - files that are not directly used (e.g. other Rmds)
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
    """Get the dictionary of internal updates for each script
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
        intupd_pattern = f"^Reason: Updated input files: (.*).*$"
        intupd_pattern_sc = f"^Reason: Updated input files: (.*);.*$"
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
