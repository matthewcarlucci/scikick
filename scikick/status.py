"""functions used by 'sk status'"""
import os
import re
import subprocess
from scikick.yaml import yaml_in
from scikick.utils import warn, get_sk_exe_dir

def snake_status(snakefile, workdir, verbose, rmd):
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
    # Get missing outputs
    missing_outs = missing_outputs(reasons)
    # Get which scripts will be executed
    exec_scripts = to_execute(jobs)
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
    # Get all files
    all_files = set()
    for script in analysis.keys():
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
        if _file in analysis.keys():
            #### SETUP
            # define corresponding html and md files for the rmd
            _file_md = os.path.join(os.path.join(reportdir, "out_md"), \
                os.path.splitext(_file)[0] + ".md")
            _file_html = os.path.join(os.path.join(reportdir, "out_html"), \
                os.path.splitext(_file)[0] + ".html")
            if _file == index_file:
                _file_md = os.path.join(os.path.join(reportdir, "out_md"), \
                    "index.md")
                _file_html = os.path.join(os.path.join(reportdir, "out_html"), \
                    "index.html")
            #### FLAG -**
            # html is to be generated
            if ("_site.yml" in map(os.path.basename, extupds[_file])) or \
                (not os.path.isfile(_file_html)) or \
                (_file_md in intupds[_file]):
                markers[_file][0] = "-"
            #### FLAG m--
            # script's md does not exist
            if _file_md in missing_outs:
                markers[_file][0] = "m"
            #### FLAG s**
            # script itself was modified
            if _file in intupds[_file]:
                markers[_file][0] = "s"
            #### FLAG *u* and FLAG *e*
            # script's external dependency md was updated (*e*), but not an rmd (*u*)
            for upd in extupds[_file] + intupds[_file]:
                md_match = re.match(f"^{reportdir}/out_md/.*.md$", upd)
                if (md_match is not None) and upd != _file_md:
                    # if the md doesn't have a corresponding script, *u*, else *e*
                    if os.path.splitext(re.sub(pattern=f"{reportdir}/out_md/", \
                        repl="", string=upd))[0] not in \
                        map(lambda x: os.path.splitext(x)[0], exec_scripts):
                        markers[_file][1] = "u"
                    else:
                        markers[_file][1] = "e"
            #### FLAG **i
            # script's internal dependencies have been updated
            deps = analysis[_file]
            deps = deps if (deps is not None) else list()
            if len(list(filter(lambda d: d in intupds[_file], deps))) > 0:
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
    """Returns a list of files listed as 'Executing R chunks in'"""
    exec_files = list()
    exec_pattern = f"^.*Executing R chunks in (.*), outputting to.*$"
    for job in jobs:
        match = re.match(exec_pattern, job)
        if match is not None:
            exec_files.append(match.groups()[0])
    return exec_files
