#!/usr/bin/env python3
"""CLI tool script"""
import os
import sys
import argparse
import shutil
import subprocess
from re import sub, match, IGNORECASE
from ruamel.yaml import YAML
from ruamel.yaml.compat import ordereddict
import scikick
import scikick.yaml
from scikick.utils import reterr, warn, get_sk_snakefile, get_sk_exe_dir
from scikick.snakemake import run_snakemake
from scikick.status import snake_status
from scikick.config import new_tab_order, get_tabs
from scikick.config import read_snakefile_arg, write_snakefile_arg
from scikick.config import rearrange_tabs, rearrange_submenus
from scikick.init import init
from scikick.yaml import yaml_in
from scikick.move import sk_move_check, sk_move_extras
from scikick.move import sk_move_prepare_src_dest

def run(args):
    """Run the workflow"""
    # check for empty analysis:
    analysis = yaml_in()['analysis']
    if analysis is None or len(analysis) == 0:
        reterr("sk: Error: no pages have been added to scikick.yml, " + \
               "this can be done with\nsk: sk add my.rmd")

    if args.snakeargs is not None:
        run_snakeargs = " ".join(args.snakeargs)
        warn(f"sk: Snakemake arguments received: {run_snakeargs}")
    else:
        run_snakeargs = None
    run_snakemake(snakefile=get_sk_snakefile(), \
                  workdir=os.getcwd(), \
                  dryrun=args.dryrun, \
                  run_snakeargs=run_snakeargs, \
                  verbose=args.verbose)


def init_loc(args):
    """Initialize scikick project"""
    if not (args.git or args.dirs or args.yaml or args.readme or args.demo):
        args.yaml = True
        warn("sk: No arguments supplied, defaulting to sk init -y")
        init(get_sk_exe_dir(), args)
        warn("sk: See the below arguments for other " + \
             "possible sk init components")
        parser_init.print_help()
        warn("sk: To add an R/Rmd script to the analysis use")
        warn("sk: sk add my.rmd")
        warn("sk: Then, to execute the workflow")
        warn("sk: sk run")
    else:
        init(get_sk_exe_dir(), args)


def add(args):
    """Add Rmds to scikick.yml"""
    scikick.yaml.add(args.rmd, args.deps, args.force)


def delete(args):
    """Remove Rmds from scikick.yml"""
    scikick.yaml.rm(args.rmd, args.deps)


def mv(args):
    """Rename an Rmd in scikick.yml and associated files"""
    config = yaml_in()
    if config["analysis"] is None:
        reterr("sk: Error: no pages have been added to scikick.yml")

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
    # clear repetitions and rateint the order in scikick.yml
    mv_dict = ordereddict()
    for k in config["analysis"]:
        if k in new_src:
            i = new_src.index(k)
            mv_dict[new_src[i]] = new_dest[i]
    # perform the move operation (using the initial args)
    for s in src:
        if args.git:
            print(f"sk: git mv {s} {dest[0]}")
            git_res = subprocess.run(f"git mv {s} {dest[0]}", shell=True, \
                stderr=subprocess.PIPE)
            if git_res.returncode != 0:
                reterr(f"sk: Git error: {git_res.stderr.decode().strip()}")
        else:
            print(f"sk: mv {s} {dest[0]}")
            shutil.move(s, dest[0])
    sk_move_extras(mv_dict)

def status(args):
    """Get status of the current workflow"""
    snake_status(snakefile=get_sk_snakefile(), \
                 workdir=os.getcwd(), \
                 verbose=args.verbose)


def layout(args):
    """Manipulate the tab order in resulting htmls by changing
    the order of keys of 'analysis' dict in scikick.yml.
    """
    # TODO: optimize this code, too much redundancy
    config = yaml_in()
    if config["analysis"] is None:
        reterr("sk: Error: no pages have been added to scikick.yml")
    tabs = get_tabs(config)

    # modify the layout of a submenu
    if args.submenu is not None:
        rearrange_submenus(args.submenu[0], args.order, config, tabs)
    else:
        rearrange_tabs(args.order, config, tabs)

def snake_config(args):
    possible_args = ["singularity", "conda", "threads", "benchmark"]
    const_vals = ["SING_GET", "CONDA_GET", 999999, "BENCH_GET"]
    if len(list(filter(lambda s: getattr(args, s) is not None,
        possible_args))) == 0:
        parser_snake_config.print_help()
    none_set = True
    # read first...
    for i in range(len(possible_args)):
        given_val = getattr(args, possible_args[i])
        if given_val == const_vals[i]:
            set_arg_val = read_snakefile_arg(possible_args[i])
            if set_arg_val is not None:
                none_set = False
                print(f"sk: Argument {possible_args[i]} is set to {set_arg_val}")
            else:
                print(f"sk: Arguemnt {possible_args[i]} has not been set")
    # ...then write
    for i in range(len(possible_args)):
        given_val = getattr(args, possible_args[i])
        if (given_val is not None) and (given_val != const_vals[i]):
            write_snakefile_arg(possible_args[i], given_val)

def site(args):
    scikick.yaml.site(args)

parser = argparse.ArgumentParser(
		description="See available scikick commands below")
parser.add_argument("-v", "--version", action="version", \
                    version="%(prog)s {version}".format(version=scikick.__version__))

subparsers = parser.add_subparsers(help="")

parser_run = subparsers.add_parser("run", help="Run pending tasks using snakemake",
                                   description="Run snakemake to execute the workflow specified in scikick.yml")
parser_run.add_argument("-v", "--verbose", action="store_true")
parser_run.add_argument("-d", "--dryrun", action="store_true", \
                        help="Show snakemake's planned execution (wrapper for snakemake -n)")
parser_run.add_argument("-s", "--snakeargs", nargs=argparse.REMAINDER, \
                        help="Pass all trailing arguments to snakemake")
parser_run.set_defaults(func=run)


parser_init = subparsers.add_parser("init", \
                                    help="Initialize a new scikick project in the current directory",
                                    description="Initialize a new scikick project in the current directory by creating template files, such as a template workflow configuration file scikick.yml (--yaml), base directories (--dirs), .gitignore with specific directories included (--git), or get a markdown indicator that the current project is using scikick (--readme)")
parser_init.add_argument("--yaml", "-y", action="store_true", \
                         help="Add a minimal scikick.yml config file to the current directory")
parser_init.add_argument("--dirs", "-d", action="store_true", \
		help="Create directories: input (raw data), output (script outputs), code (scripts/code), report (website)")			 
parser_init.add_argument("--git", "-g", action="store_true", \
                         help="Append relevant directories to .gitignore (only useful when using -d)")
parser_init.add_argument("--readme", action="store_true", \
                         help="Print a message to stdout for a README.md file to clearly indicate scikick is in use for the project")
parser_init.add_argument("--demo", action="store_true", \
                         help="Create and run a demo project demonstrating scikick usage")
parser_init.set_defaults(func=init_loc)

parser_add = subparsers.add_parser("add", \
                                   help="Add scripts and their dependencies to the workflow",
                                   description="Add scripts and their dependencies to the current project's configuration file (scikick.yml). Multiple dependencies can be added to the same script and the same dependency list can be added to multiple scripts")
parser_add.add_argument("rmd", nargs="+", \
                        help="Script(s) to be added)")
parser_add.add_argument("-d", "--deps", \
                        nargs="+", \
                        help="Dependencies to be added to the script(s)")
parser_add.add_argument("--force", action="store_true", \
                         help="Force addition of a script(s)")
parser_add.set_defaults(func=add)

parser_del = subparsers.add_parser("del", \
                                   help="Remove scripts and their dependencies from the workflow",
                                   description="Remove scripts and their dependencies from the current project's configuration file (scikick.yml). If only scripts are specified, they will be removed with their dependencies. If the '-d' flag is used, only dependencies are removed from the scripts.")
parser_del.add_argument("rmd", nargs="+", \
                        help="Remove scripts and/or their dependencies to the workflow")
parser_del.add_argument("-d", "--deps", \
                        nargs="+", \
                        help="Dependencies to be removed from the script(s)")
parser_del.set_defaults(func=delete)

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
parser_mv.set_defaults(func=mv)

parser_status = subparsers.add_parser("status", \
                                      help="Show scripts with pending execution",
                                      description="Show scripts with pending execution. A 3 character code is used to mark the reason for pending tasks on a script: (s--) indicates the script itself is outdated, (m--) indicates a missing markdown output from the script, (--i) indicates an imported dependency has been updated, (-e-) indicates an upstream step/script must be re-executed, (---) indicates only the html rendering needs updating, (???) indicates the file is not found.")
parser_status.add_argument("-v", "--verbose", action="store_true",
                           help="Show the workflow config for all scripts")
parser_status.set_defaults(func=status)

parser_layout = subparsers.add_parser("layout", \
                                      help="Manage the website navigation bar layout",
                                      description="Modify the order of tabs and items within the tabs in the navigation bar of the generated website")
parser_layout.add_argument("order", nargs="*", type=int, \
                           help="Specify a new order (e.g. sk layout 3 2 1)")
parser_layout.add_argument("-s", "--submenu", \
                           nargs=1, \
                           help="Define the layout within a menu/subdirectory")
parser_layout.set_defaults(func=layout)

parser_snake_config = subparsers.add_parser("config", \
                                      help="Set or get global snakemake directives for scikick",
                                      description="Set or get global snakemake directives for scikick")
parser_snake_config.add_argument("--singularity", nargs="?", type=str, \
                       const="SING_GET", help="Set singularity image")
parser_snake_config.add_argument("--conda", nargs="?", type=str, \
                       const="CONDA_GET", help="Set conda environment file")
parser_snake_config.add_argument("--threads", nargs="?", type=int, \
                       const=999999,
                       help="Set number of threads for conversion to md (i.e. for script execution)")
parser_snake_config.add_argument("--benchmark", nargs="?", type=str, \
                       const="BENCH_GET", help="Set benchmark output prefix")
parser_snake_config.set_defaults(func=snake_config)

parser_site = subparsers.add_parser("site", \
                                    help="Set sites in the 'More' tab",
                                    description="Modify links in the 'More' tab. Both '--name' and '--link' need to be specified in order to add a link. In order to delete a link, both '--delete' and '--name' have to be specified.")
parser_site.add_argument("--name", nargs=1, type=str, \
                       help="Set the name for a link")
parser_site.add_argument("--link", nargs=1, type=str, \
                       help="Set the link for the text")
parser_site.add_argument("-d", "--delete", action="store_true",
                           help="Remove the link for the given '--text' argument")
parser_site.add_argument("-g", "--get", action="store_true",
                           help="Get all the links")
parser_site.set_defaults(func=site)


def main():
    """Parse the arguments and run the according function"""
    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
        return
    func(args)
