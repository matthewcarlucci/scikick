import os
import re
import subprocess
from scikick.yaml import yaml_in
from scikick.utils import warn

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
    reportdir = yaml['reportdir']
    md_dir = os.path.join(reportdir, "out_md")
    site_yaml = os.path.join(reportdir, "out_md/_site.yaml")
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
    # Get all files
    all_files = set()
    for script in scripts:
        all_files.add(script)
        if yaml["analysis"][script] is not None:
            for dep in yaml["analysis"][script]:
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
            _file_md = os.path.join(md_dir, os.path.splitext(_file)[0] + ".md")
            # script's md does not exist
            if not os.path.isfile(_file_md):
                markers[_file] = ["m", "-", "-"]
                continue
            # html is to be generated
            if "_site.yml" in map(os.path.basename, extupds[_file]):
                markers[_file][0] = "-"
            # script itself was modified
            if _file_md in extupds[_file] and _file in intupds[_file]:
                markers[_file][0] = "s"
            # script's external dependencies have been updated
            for eu in extupds[_file]:
                is_script = eu in map(lambda x: os.path.join(md_dir,
                    os.path.splitext(x)[0] + ".md"), scripts)
                if is_script and eu != _file_md:
                    markers[_file][1] = "e"
            # script's internal dependencies have been updated
            if len(intupds[_file]) > 0 + (_file in intupds[_file]):
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
    # print the status
    for key in yaml["analysis"].keys():
        if verbose:
            print(f" {''.join(markers[key])} \t{key}")
            if yaml["analysis"][key] is not None:
                for dep in yaml["analysis"][key]:
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
                                    yaml["analysis"].keys())))
    reexec_no = len(list(filter(lambda k: \
                                "".join(markers[k]) != "   " and \
                                "".join(markers[k]) != "---" and \
                                "".join(markers[k]) != "???", \
                                    yaml["analysis"].keys())))
    up2date_no = len(list(filter(lambda k: \
                                "".join(markers[k]) == "   ", \
                                    yaml["analysis"].keys())))
    missing_no = len(list(filter(lambda k: \
                                "".join(markers[k]) == "???", \
                                    yaml["analysis"].keys())))
    print(f"Scripts to execute: {reexec_no}")
    print(f"HTMLs to compile ('---'): {rehtml_no}")
    if verbose:
        print(f"Up to date ('   '): {up2date_no}")
    if missing_no > 0:
        print(f"Missing ('???'): {missing_no}")
  
def job_to_script(job, scripts):
    exe_pattern = f"^Job.*: Executing R chunks in (.*), outputting to (.*)$"
    htmlgen_pattern = f"^Job.*: Generating (.*) html page$"
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
    extupd_dict = dict()
    for script in scripts:
        extupd_dict[script] = list()
    for i in range(len(reasons)):
        extupd_pattern = f"^.*Input files updated by another job: (.*)$"
        match = re.match(extupd_pattern, reasons[i])
        if match is not None:
            script = job_to_script(jobs[i], scripts)
            updated_files = match.groups()[0].split(", ")
            if script is not None:
                for uf in updated_files:
                    if len(uf) != 0:
                        extupd_dict[script].append(uf)
    return extupd_dict

def internal_updates(scripts, reasons, jobs):
    intupd_dict = dict()
    for script in scripts:
        intupd_dict[script] = list()
    for i in range(len(reasons)):
        # stupid solution currently - cant go around the ';' sign with regex
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
                if os.path.basename(script) == "index.Rmd":
                    continue
                for uf in updated_files:
                    if len(uf) != 0:
                        intupd_dict[script].append(uf)
    return intupd_dict
