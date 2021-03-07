#!/usr/bin/env python3
"""CLI tool script"""
import os
import sys
import argparse
import shutil
import subprocess
from re import sub, match, IGNORECASE
from ruamel.yaml import YAML, dump, RoundTripDumper
from ruamel.yaml.compat import ordereddict
import scikick
import scikick.yaml
from scikick.utils import reterr, warn, get_sk_snakefile, get_sk_exe_dir
from scikick.snakemake import run_snakemake
from scikick.status import snake_status
from scikick.config import ScikickConfig, write_snakefile_arg
from scikick.layout import rearrange_tabs, rearrange_submenus, new_tab_order, get_tabs
from scikick.init import init
from scikick.yaml import yaml_in, yaml_dump, yaml_check
from scikick.move import sk_move_check, sk_move_extras
from scikick.move import sk_move_prepare_src_dest

def sk_run(args):
    """Run the workflow"""
    
    # check for empty analysis unless a script will be added
    need_pages = args.script is None
    skconfig = ScikickConfig(need_pages=need_pages) 
    reportdir = skconfig.report_dir

    if args.snakeargs is not None:
        snakeargs = " ".join(args.snakeargs)
        warn(f"sk: Snakemake arguments received: {snakeargs}")
    else:
        snakeargs = None
    retcode = run_snakemake(snakefile=get_sk_snakefile(), \
                  workdir=os.getcwd(), \
                  dryrun=args.dryrun, \
                  snakeargs=snakeargs, \
                  verbose=args.verbose, \
                  rmds=args.script, \
                  quiet=args.quiet)
    sys.exit(retcode)


def sk_init(args):
    """Initialize scikick project"""
    if not (args.git or args.dirs or args.yaml or args.readme or args.demo):
        args.yaml = True
        warn("sk: No arguments supplied, defaulting to sk init -y")
        init(args)
        warn("sk: See the below arguments for other " + \
             "possible sk init components")
        parser_init.print_help()
        warn("sk: To add an R/Rmd script to the analysis use")
        warn("sk: sk add my.rmd")
        warn("sk: Then, to execute the workflow")
        warn("sk: sk run")
    else:
        init(args)


def sk_add(args):
    """Add Rmds to scikick.yml"""
    scikick.yaml.add(args.script, args.depends_on, args.force, args.copy_deps)


def sk_del(args):
    """Remove Rmds from scikick.yml"""
    scikick.yaml.rm(args.script, args.depends_on)


def sk_mv(args):
    """Rename an Rmd in scikick.yml and associated files"""
    config = yaml_in(need_pages=True)
    # multiple args
    src = [os.path.normpath(p) for p in args.src]
    # only a single arg
    dest = [os.path.normpath(p) for p in args.dest]
    #check if src and dest are valid
    sk_move_check(src, dest)
    # save the (src, dest) pairs (to be used with moves in scikick.yml)
    (new_src, new_dest) = sk_move_prepare_src_dest(src, dest)
    new_src = list(map(os.path.normpath, new_src))
    new_dest = list(map(os.path.normpath, new_dest))
    # leave only unique pairs of (src, dest) files
    mv_dict = ordereddict()
    for k in new_src:
        i = new_src.index(k)
        mv_dict[new_src[i]] = new_dest[i]
    # perform the move operation (using the initial args)
    for s in src:
        git_retcode = 0
        if args.git:
            print(f"sk: git mv {s} {dest[0]}")
            git_res = subprocess.run(f"git mv {s} {dest[0]}", shell=True, \
                stderr=subprocess.PIPE)
            git_retcode = git_res.returncode
            if git_retcode != 0:
                warn("sk: Warning: Git returned an error:")
                warn(git_res.stderr.decode().strip())
                warn("sk: Warning: Falling back to mv")
        if (git_retcode != 0) or (not args.git):
            print(f"sk: mv {s} {dest[0]}")
            shutil.move(s, dest[0])
    sk_move_extras(mv_dict)

def sk_status(args):
    """Get status of the current workflow"""
    snake_status(snakefile=get_sk_snakefile(), \
                 workdir=os.getcwd(), \
                 verbose=args.verbose, \
                 rmd=args.script)


def sk_layout(args):
    """Manipulate the tab order in resulting htmls by changing
    the order of keys of 'analysis' dict in scikick.yml.
    """
    # TODO: optimize this code, too much redundancy
    config = yaml_in(need_pages=True)
    tabs = get_tabs(config)

    # modify the layout of a submenu
    if args.submenu is not None:
        rearrange_submenus(args.submenu[0], args.order, config, tabs)
    else:
        rearrange_tabs(args.order, config, tabs)

# Three usage modes
# 1. sk config 			Show the full config          (get)
# 2. sk config --<arg> 		Show the setting for this arg (get)
# 3. sk config --<arg> <value> 	Assign value to arg           (set)
def sk_config(args):
    skconfig=ScikickConfig()
    config_exists = 'snakefile_args' in skconfig.config.keys()

    # values that will be present if only arg was provided (e.g. sk config --conda)
    const_vals = ["SING_GET", "CONDA_GET", 999999, "BENCH_GET"]
    possible_args = ["singularity", "conda", "threads", "benchmark"]

    # Mode 1 - get all values
    provided_args = list(filter(lambda s: getattr(args, s) is not None, possible_args))
    if len(provided_args) == 0:
        if config_exists:
            dump(skconfig.config['snakefile_args'], sys.stdout, Dumper=RoundTripDumper)
        else:
            print("sk: No config options have been set (see sk config --help for options)")
    else:
        for i in range(len(possible_args)):
            this_arg = possible_args[i]
            given_val = getattr(args, this_arg)
            arg_was_provided = given_val is not None
            val_was_empty = given_val == const_vals[i]  
            # Mode 2 - get one value
            if arg_was_provided and val_was_empty:
                # intent is to view current config for arg
                if config_exists:
                    val_exists = this_arg in skconfig.config['snakefile_args'].keys()
                    if val_exists:
                        set_arg_val = skconfig.config['snakefile_args'][this_arg]
                        print(f"sk: Argument {this_arg} is set to {set_arg_val}")
                    else:
                        print(f"sk: Argument {this_arg} has not been set")
            # Mode 3 - set value
            elif arg_was_provided and not val_was_empty:
                write_snakefile_arg(this_arg, given_val)

parser = argparse.ArgumentParser(
		description="See available scikick commands below")
parser.add_argument("-v", "--version", action="version", \
                    version="%(prog)s {version}".format(version=scikick.__version__))

subparsers = parser.add_subparsers(help="")

# run
parser_run = subparsers.add_parser("run", help="Run pending tasks using snakemake",
                                   description="Run snakemake to execute the workflow specified in scikick.yml")
parser_run.add_argument("script", type=str, nargs="*", \
                        help="Generate htmls only for the listed script (optional)")
parser_run.add_argument("-v", "--verbose", action="store_true")
parser_run.add_argument("-q", "--quiet", action="store_true")
parser_run.add_argument("-d", "--dryrun", action="store_true", \
                        help="Show snakemake's planned execution (wrapper for snakemake -n)")
parser_run.add_argument("-s", "--snakeargs", nargs=argparse.REMAINDER, \
                        help="Pass all trailing arguments to snakemake")
parser_run.set_defaults(func=sk_run, which="run")

# init
parser_init = subparsers.add_parser("init", \
                                    help="Initialize a new scikick project in the current directory",
                                    description="Initialize a new scikick project in the current directory by importing a minimal scikick.yml file. Optionally, import useful template content or import the demo project with a short walkthrough of the main scikick commands.")
parser_init.add_argument("--yaml", "-y", action="store_true", \
                         help="Add a minimal scikick.yml config file to the current directory and add the current Scikick version")
parser_init.add_argument("--dirs", "-d", action="store_true", \
		help="Create directories: input (raw data), output (script outputs), code (scripts/code), report (website)")			 
parser_init.add_argument("--git", "-g", action="store_true", \
                         help="Append relevant directories to .gitignore (only useful when using -d)")
parser_init.add_argument("--readme", action="store_true", \
                         help="Print a message to stdout for a README.md file to clearly indicate scikick is in use for the project")
parser_init.add_argument("--demo", action="store_true", \
                         help="Create and run a demo project demonstrating scikick usage")
parser_init.set_defaults(func=sk_init, which="init")

# add
parser_add = subparsers.add_parser("add", \
                                   help="Add scripts and their dependencies to the workflow",
                                   description="Add scripts and their dependencies to the project configuration file (scikick.yml). All provided dependnecies will be applied to all provided scripts. A dependency list can be applied from an existing script with --copy-deps.")
parser_add.add_argument("script", nargs="+", \
                        help="Script(s) to be added)")
parser_add.add_argument("-d", "--depends-on", \
                        action='append', \
                        help="Dependency to be added to the script(s) (can be used multiple times as sk add script.Rmd -d dep1.Rmd -d dep2.Rmd)")
parser_add.add_argument("--copy-deps", \
                        nargs=1, \
                        help="Copy the dependency list from this file")
parser_add.add_argument("--force", action="store_true", \
                         help="Force addition of a script(s)")
parser_add.set_defaults(func=sk_add, which="add")

# del
parser_del = subparsers.add_parser("del", \
                                   help="Remove scripts and/or their dependencies from the workflow configuration",
                                   description="Remove scripts and their dependencies from the project configuration file (scikick.yml). If no '-d' is provided, the provided script(s) entry will be removed entirely from the configuration file. If the '-d' flag is used, only these dependencies are removed and only from the provided scripts.")
parser_del.add_argument("script", nargs="+", \
                        help="Script(s) entry to modify")
parser_del.add_argument("-d", "--depends-on", \
                        action='append', \
                        help="Remove this dependency from the script(s) entry (can be used multiple times)")
parser_del.set_defaults(func=sk_del, which="del")

# mv
parser_mv = subparsers.add_parser("mv", \
                                  help="Move scripts and change project structure accordingly",
                                  description="Perform a basic mv operation while adjusting scikick.yml paths and moving corresponding files (markdown, knitmeta.RDS and output figures) to avoid re-execution")
parser_mv.add_argument("src", nargs="+", \
                       help="Move from here")
parser_mv.add_argument("dest", nargs=1, \
                       help="Move to here")
parser_mv.add_argument("-g", "--git", action="store_true", \
                       help="Use git mv instead of basic mv to track with git")
parser_mv.add_argument("-v", "--verbose", action="store_true", \
                       help="Show all moves taking place (mainly for debugging)")
parser_mv.set_defaults(func=sk_mv, which="mv")

# status
parser_status = subparsers.add_parser("status", \
                                      help="Show scripts with pending execution", \
                                      description="Show which scripts will be executed and provide a reason for execution with a 3 character code. Codes indicate the following: \n(s--) Script is older than the latest report\n(m--) Script's output report is missing\n(-e-) Upstream script must execute before the script\n(-u-) Upstream script's output is newer than the script's output\n(--i) Imported file is newer than the script's output\n(---) No script execution needed, only the site rendering\n(???) File is not found", formatter_class=argparse.RawTextHelpFormatter)
parser_status.add_argument("script", type=str, nargs="?", \
                           help="Show status of the script and everything it depends on (optional)")
parser_status.add_argument("-v", "--verbose", action="store_true", \
                           help="Show the workflow config for all scripts")
parser_status.set_defaults(func=sk_status, which="status")

# layout
parser_layout = subparsers.add_parser("layout", \
                                      help="Manage the website navigation bar layout",
                                      description="Modify the order of tabs and items within the tabs in the navigation bar of the generated website")
parser_layout.add_argument("order", nargs="*", type=int, \
                           help="Specify a new order (e.g. sk layout 3 2 1)")
parser_layout.add_argument("-s", "--submenu", \
                           nargs=1, \
                           help="Define the layout within a menu/subdirectory")
parser_layout.set_defaults(func=sk_layout, which="layout")

# config
parser_config = subparsers.add_parser("config", \
                                      help="Set or get global configurations for scikick script execution",
                                      description="Set or get global configurations for scikick script execution")
parser_config.add_argument("--singularity", nargs="?", type=str, \
                       const="SING_GET", help="Set singularity image")
parser_config.add_argument("--conda", nargs="?", type=str, \
                       const="CONDA_GET", help="Set conda environment file")
parser_config.add_argument("--threads", nargs="?", type=int, \
                       const=999999,
                       help="Set number of threads for script execution")
parser_config.add_argument("--benchmark", nargs="?", type=str, \
                       const="BENCH_GET", help="Set benchmark output prefix")
parser_config.set_defaults(func=sk_config, which="config")

# clean
def sk_clean(args):
  print("Not yet implemented")

parser_config = subparsers.add_parser("clean", \
                                      help="Clean up unwanted files",
                                      description="By default will simply remove files determined to be old")
parser_config.add_argument("--report", help="Remove all report files (reportdir)")
parser_config.add_argument("--output", help="Remove all output files (data_parent)")
parser_config.add_argument("--reset-notebooks", help="Remove all outputs from notebooks (for better git commits)")
parser_config.set_defaults(func=sk_clean, which="clean")


def main():
    """Parse the arguments and run the according function"""
    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
        return
    if args.which in ["run", "config", "status"]:
        # check for unsupported fields
        ymli = yaml_in()
        yaml_check(ymli)
    func(args)
