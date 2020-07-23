# scikick/setup.py
"""Functions used by `sk init`"""
import os
import shutil
import snakemake
import ruamel.yaml
import scikick
from scikick.utils import warn, check_requirements
from scikick.yaml import yaml_dump
from scikick.yaml import yaml_in

def add_version_info():
    """Add python package version info to scikick.yml"""
    yml_read = yaml_in()
    if 'version_info' not in yml_read.keys():
        yml_read['version_info'] = { \
            "snakemake" : snakemake.__version__, \
            "ruamel.yaml" : ruamel.yaml.__version__, \
            "scikick" : scikick.__version__ \
        }
        yaml_dump(yml_read)
        return True
    return False

def copy_file(src, dest):
    """copy files without overwriting them"""
    if os.path.exists(dest):
        return 0
    shutil.copy2(src, dest)
    return 1

def init_yaml(usr_dir, project_dir):
    """Create an initial scikick.yml config file"""
    yaml_file = "scikick.yml"
    check_requirements()
    if copy_file(os.path.join(usr_dir, yaml_file), \
        os.path.join(project_dir, yaml_file)):
        warn("sk: Created analysis configuration file scikick.yml")
    else:
        warn("sk: File scikick.yml already exists")
    if add_version_info():
        warn("sk: Added scikick version info to scikick.yml")

def init_git(usr_dir):
    """Add certain entries to .gitignore"""
    gitignore = ".gitignore"
    anything_appended = False
    if copy_file(os.path.join(usr_dir, gitignore), \
        os.path.join(gitignore)):
        warn("sk: File .gitignore created")
    else:
        existing_gitignore = open(gitignore, 'r').readlines()
        template_gitignore = open(os.path.join(usr_dir, \
            gitignore), 'r').readlines()
        append_existing = open(gitignore, "a")
        for ignore_entry in template_gitignore:
            if ignore_entry.strip() not in map(str.strip, \
                existing_gitignore):
                append_existing.writelines(ignore_entry)
                warn("sk: Added \'%s\' to .gitignore" % \
                    ignore_entry.rstrip())
                anything_appended = True
        append_existing.close()
        if not anything_appended:
            warn("sk: .gitignore already has all the required entries")

def init_readme():
    """Print a message indicating that the project uses scikick"""
    print("### Scikick")
    print("This project uses a python3 CLI application *scikick* " + \
        "which executes the workflow described in " + \
        "its configuration file `scikick.yml`.")
    print("To download scikick, use:\n\t`pip3 install scikick==%s`" % \
        scikick.__version__)
    print("To run the project, use:\n\t`scikick run`")

def init_dirs(project_dir):
    """Create default project directories"""
    anything_created = False
    dirs_to_create = ['report', 'input', 'output', 'code']
    for curr_dir in dirs_to_create:
        inproj_dir = os.path.join(project_dir, curr_dir)
        if not os.path.exists(inproj_dir):
            os.mkdir(inproj_dir)
            warn("sk: Directory %s/ created" % curr_dir)
            anything_created = True
    if not anything_created:
        warn("sk: All default directories already exist")

def init(system_dir, args):
    """Initialize a new scikick project
    system_dir -- string (directory of scikick system files)
    args -- argument list
    """
    project_dir = os.getcwd()
    # system directories
    usr_dir = os.path.join(system_dir, 'usr')
    # files to be copied
    # optional copies
    if args.yaml:
        init_yaml(usr_dir, project_dir)
    if args.dirs:
        init_dirs(project_dir)
    if args.git:
        init_git(usr_dir)
    if args.readme:
        init_readme()
