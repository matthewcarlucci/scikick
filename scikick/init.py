# scikick/init.py
"""Functions used by `sk init`"""
import os
import shutil
import snakemake
import ruamel.yaml
import scikick
from scikick.utils import warn, check_requirements, get_sk_exe_dir

def add_version_info(ymli):
    """Add python package version info to scikick.yml"""
    if 'version_info' not in ymli.keys():
        ymli['version_info'] = { \
            "snakemake" : snakemake.__version__, \
            "ruamel.yaml" : ruamel.yaml.__version__, \
            "scikick" : scikick.__version__ \
        }
        return ymli
    return ymli

def copy_file(src, dest):
    """copy files without overwriting them"""
    if os.path.exists(dest):
        return 0
    shutil.copy2(src, dest)
    return 1

def init_yaml():
    """Create an initial scikick.yml config file"""
    template_yaml_path = os.path.join(get_sk_exe_dir(), 'usr/scikick.yml')
    project_dir = os.getcwd()
    proj_yaml_path = os.path.join(project_dir, "scikick.yml")
    yml_loader = ruamel.yaml.YAML()
    check_requirements()
    if os.path.exists(proj_yaml_path): 
        warn("sk: File scikick.yml already exists")
        yml_out = yml_loader.load(open(proj_yaml_path, "r"))
    else:
        warn("sk: Importing template analysis configuration file")
        yml_out = yml_loader.load(open(template_yaml_path, "r"))
    yml_out = add_version_info(yml_out)
    warn("sk: Writing to scikick.yml") 
    yml_loader.dump(yml_out, open(proj_yaml_path,"w"))

def init_git():
    """Add certain entries to .gitignore"""
    usr_dir = os.path.join(get_sk_exe_dir(), 'usr')
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

readme_template = r"""
### Scikick
This data analysis project is executed using a python tool called 
[*scikick*](https://github.com/matthewcarlucci/scikick).
The workflow is defined in the `scikick.yml` configuration file.
Scripts are executed with the command: `sk run`.
Files in the results directory (the `reportdir: directory` 
in `scikick.yml`) are computer generated and should not be
editted by hand.
"""

def init_dirs():
    """Create default project directories"""
    project_dir = os.getcwd()
    dirs_to_create = ['report', 'input', 'output', 'code']
    made_dirs=[]
    for curr_dir in dirs_to_create:
        inproj_dir = os.path.join(project_dir, curr_dir)
        if not os.path.exists(inproj_dir):
            os.mkdir(inproj_dir)
            made_dirs.append(curr_dir)
    anything_created = len(made_dirs) > 0
    if anything_created:
        warn("sk: Created dir(s): %s" % ', '.join(made_dirs))
    else:
        warn("sk: All default directories already exist")
    

def init(args):
    """Initialize a new scikick project"""
    # optional procedures
    if args.yaml:
        init_yaml()
    if args.dirs:
        init_dirs()
    if args.git:
        init_git()
    if args.readme:
        print(readme_template)
    if args.demo:
        init_demo()

def print_demo(msg):
    print(f"SCIKICK DEMO: {msg}")

def print_exec(cmd):
    print(f"$ {cmd}")
    os.system(cmd)

def init_demo():
    # start stage1 only if cwd is empty
    if len(os.listdir(".")) == 0:
        run_demo_stage1()
        open(".skdemo_stage1", 'a').close()
    elif os.path.isfile(".skdemo_stage1"):
        run_demo_stage2()
        open(".skdemo_stage2", 'a').close()
        os.remove(".skdemo_stage1")
    elif os.path.isfile(".skdemo_stage2"):
        run_demo_stage3()
        open(".skdemo_stage3", 'a').close()
        os.remove(".skdemo_stage2")
    elif os.path.isfile(".skdemo_stage3"):
        run_demo_stage4()
        open(".skdemo_stage4", 'a').close()
        os.remove(".skdemo_stage3")
    elif os.path.isfile(".skdemo_stage4"):
        run_demo_stage5()
        open(".skdemo_stage5", 'a').close()
        os.remove(".skdemo_stage4")
    elif os.path.isfile(".skdemo_stage5"):
        run_demo_stage6()
        open(".skdemo_stage6", 'a').close()
        os.remove(".skdemo_stage5")
    elif os.path.isfile(".skdemo_stage6"):
        print_demo("The demo is complete")
    else:
        print_demo("The demo can only be initialized in an empty directory")

def run_demo_stage1():
    print_demo("A demo project will be used to demonstrate some features of scikick.")
    print("")
    print_demo("----------  Starting a New Project  ----------")
    print_demo("A new scikick project can be initialized with sk init which will:")
    print_demo("check some software dependencies,")
    print_demo("add the scikick.yml config file (-y),")
    print_demo("and make some useful directories (-d).")

    print_exec("sk init -yd")
    # copy the files
    demo_templatedir = os.path.join(get_sk_exe_dir(), "template", "demo")
    for f in ["generate.Rmd", "PCA.Rmd", "analysis_config.txt", \
        "PC_score_statistics.Rmd", "index.Rmd"]:
        shutil.copy(os.path.join(demo_templatedir, f), os.path.join("code", f))
    print_demo("Demo project has been initialized.")
    print_demo("Run sk init --demo again to continue.")

def run_demo_stage2():
    print_demo("----------  Adding Some Notebooks  -----------")
    print_demo("Documents can be added to the project with sk add.")
    print_demo("-d is used to specify which documents must run")
    print_demo("before or are used by the added notebook. ")

    print_exec("sk add code/index.Rmd")
    print_exec("sk add code/generate.Rmd")
    print_exec("sk add code/PCA.Rmd -d code/generate.Rmd -d code/analysis_config.txt")
    print_exec("sk add code/PC_score_statistics.Rmd -d code/PCA.Rmd")

    print_demo("Run sk init --demo again to continue.")

def run_demo_stage3():
    print_demo("----------       Check Status       ----------")
    print_demo("sk status will show which notebooks require execution.")

    print_exec("sk status")

    print_demo("Run sk init --demo again to continue.")

def run_demo_stage4():
    print_demo("----------     Execute Notebooks    ----------")
    print_demo("sk run will execute all tasks needed to generate the final website.")

    print_exec("sk run")

    print_demo("The completed site is located at")
    print_demo(f"{os.getcwd()}/report/out_html/")
    print_demo("The index.html homepage can be opened in any web-browser.")
    print("")
    print_demo("----------        What Next?        ----------")
    print_demo("This should be all you need to get started. After reviewing")
    print_demo("the resulting website you could do one of:")
    print_demo("1. Run sk init --demo again to see more demonstrations.")
    print_demo("2. Perform your own testing with this project.")
    print_demo("3. Start managing your own notebooks with scikick!")

def run_demo_stage5():
    print_demo("----------   Rerunning The Workflow ----------")
    print_demo("Trying to rerun the workflow.")

    print_exec("sk run")

    print_demo("Since no changes have been made, the workflow is not reexecuted.")
    print_demo("Run sk init --demo again to continue.")

def run_demo_stage6():
    print_demo("---------- Intermediate File Change ----------")
    print_demo("Let's change some intermediate file in the workflow.")

    print_exec("echo -e 'versicolor\\nvirginica' > code/analysis_config.txt")

    print_demo("Now flower data only of species versicolor and virginica will be processed with PCA.")

    print_exec("sk run")

    print_demo("code/generate.Rmd was not executed, since it does not depend on the file that was changed.")
    print_demo("----------     The Demo Is Done     ----------")
