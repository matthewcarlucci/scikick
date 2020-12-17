"""basic functions used to modify and read scikick.yml"""
import os
import re
import ruamel.yaml as yaml
from ruamel.yaml.compat import ordereddict
from scikick.utils import reterr, warn, get_sk_exe_dir
import scikick

# supported extensions will be executed to generate a md file
supported_extensions = [".R", ".Rmd", ".md",".ipynb"]
supported_yaml_fields = ["reportdir", "analysis", "version_info", "snakefile_args","yaml_header"]

def yaml_check(config):
    """Checks for unsupported fields in scikick.yml
    config -- dict of scikick.yml
    """
    for k in config.keys():
        if k not in supported_yaml_fields:
            warn(f"sk: Warning: Unrecognized scikick.yml field '{k}'")

def get_indexes(config):
    """Returns a list of 'index.R(md)' files in scikick.yml
    config -- dict of scikick.yml
    """
    return list(filter(lambda f: \
        os.path.splitext(os.path.basename(f))[0] == "index", \
        config["analysis"].keys()))

def rm_commdir(text, commpath):
    """Removes path (prefix) commpath from text
    with a check if the commpath is of length 0
    text - string to be modified
    commpath - the prefix that is removed
    """
    if len(commpath) != 0:
        ntxt = text[(len(commpath) + 1):]
        return ntxt if ntxt != "" else "./"
    return text

def yaml_dump(ymli):
    """(Over)write a dictionary to scikick.yml.
    ymli -- dict
    """
    ymlo = yaml.YAML()
    ymlo.dump(ymli, open("scikick.yml", "w"))

def yaml_in(ymlpath='scikick.yml',need_pages=False):
    """Read scikick.yml.
    Returns an ordereddict.
    need_pages -- logical, whether to error if analysis is empty
    """
    #Exit with an error message if scikick.yml is not found
    if not os.path.isfile(ymlpath):
        reterr(f"sk: Error: {ymlpath} not found," + \
               "to get a template, run\nsk: sk init")

    ymli = yaml.YAML()
    ymli = ymli.load(open(ymlpath, "r"))
    if ymli is None:
        warn("sk: Warning: scikick.yml is empty")
        ymli = dict()
    # make sure that mandatory fields are present
    if "analysis" not in ymli.keys():
        if need_pages:
            reterr("sk: Error: no pages have been added to scikick.yml, " + \
                "this can be done with\nsk: sk add my.rmd")
        else:
            warn("sk: Warning: scikick.yml is missing analysis field") 
            ymli["analysis"] = ordereddict()
    else:
        if ymli["analysis"] is None:
            warn("sk: Warning: analysis should not be None") 
            ymli["analysis"] = ordereddict()
    if "reportdir" not in ymli.keys():
        warn("sk: Warning: scikick.yml is missing reportdir field") 
        ymli["reportdir"] = ""
    return ymli

def rename(name_a, name_b):
    """Rename file 'a' in scikick.yml to 'b'
    a -- string (filename)
    b -- string (filename)
    """
    found = 0
    ymli = yaml_in()
    ## rename keys (ana)
    if name_a in ymli["analysis"].keys():
        index_a = list(ymli["analysis"].keys()).index(name_a)
        ymli["analysis"].insert(index_a, name_b, ymli["analysis"].pop(name_a))
        found = 1
    ## rename values (deps)
    if ymli["analysis"] is not None:
        for k in ymli["analysis"].keys():
            if ymli["analysis"][k] is not None and \
                name_a in ymli["analysis"][k]:
                ymli["analysis"][k][ymli["analysis"][k].index(name_a)] = \
                    name_b
                found = 1
    yaml_dump(ymli)
    return found

def set_arg(arg, val):
    """Set value of 'arg' in scikick.yml to 'val'.
    Result: scikick.yml:
    arg -- string
    val -- string
    """
    ymli = yaml_in()
    ymli[arg] = val
    warn("sk: Argument \'%s\' set to \'%s\'" % (arg, val))
    yaml_dump(ymli)

def get_arg(arg):
    """Read value of field 'arg' in scikick.yml.
    Returns a string
    arg -- string
    """
    ymli = yaml_in()
    if arg in ymli.keys():
        return ymli[arg]
    return ""

### Check functions for add()
wildcard_symbols = ["*", "?", "[", "{", "]", "}", "\\"]
def add_check(fname, ymli, force, deps):
    """Performs a check if fname can be added to scikick.yml as a key"""
    pages = ymli["analysis"].keys()
    if fname in pages:
        warn(f"sk: Found existing entry for {fname}")
        return False
    # filenames cannot currently have wildcard symbols
    if True in [i in fname for i in wildcard_symbols]:
        warn(f"sk: Error: Filename ({fname}) cannot have wildcard symbols ({' '.join(wildcard_symbols)})")
        return False
        # check if the file extension is supported
    fext = os.path.splitext(fname)[-1]
    f_exe_support = fext.lower() in [x.lower() for x in supported_extensions]
    if not f_exe_support:
        extension_list_str = ', '.join(supported_extensions)
        warn("sk: Error: Only %s files can be added as pages (%s)" % \
            (extension_list_str, fname))
        return False
    # error if the directory doesn't exist
    dirname = os.path.dirname(fname)
    if dirname != "":
        if not os.path.isdir(dirname):
            reterr(f"sk: Error: Directory {dirname} does not exist.")
    # create the file if it doesn't exist
    if not os.path.isfile(fname):
        warn(f"sk: Warning: File {fname} doesn't exist")
        warn(f"sk: Creating new file {fname}")
        open(fname, "a").close()
    if fname not in pages:
        # Check for other files with same basename (and therefore same md output file)
        fname_base = os.path.splitext(fname)[0]
        page_basenames = map(lambda x: os.path.splitext(x)[0], pages) 
        page_basename_exists = fname_base in page_basenames
        if page_basename_exists:
            warn(f"sk: Error: Page {fname_base} is already to be compiled from another file.")
            return False
        # check for "index.Rmd"s
        index_list = get_indexes(ymli)
        if os.path.splitext(os.path.basename(fname))[0] == "index":
            if len(index_list) == 0:
                warn(f"sk: An index file {fname} has been added and will be used as the homepage")
                # touch the added index file to ensure execution
                os.utime(fname, None)
            elif len(index_list) == 1:
                if not force:
                    reterr(f"sk: Error: An index file {index_list[0]} already exists\n" + \
                        "sk: Error: An additional one can be added, but neither will be used as a homepage\n" + \
                        f"sk: Error: To persist, use 'sk add --force {fname}'")
                else:
                    warn(f"sk: Warning: A redundant index file has been added\n" +
                        "sk: Warning: Neither of the added index files will be used as a homepage")
                    os.utime(os.path.join(get_sk_exe_dir(), "template", "index.Rmd"), None)
            elif len(index_list) > 1:
                warn(f"sk: Warning: A redundant index file has been added\n" +
                    "sk: Warning: Neither of the added index files will be used as a homepage")
    return True


def add_dep_checks(fname, ymli, force, dep):
    """ Check if dependency can be added to fname """
    if not os.path.isfile(dep):
        warn(f"sk: Warning: {dep} does not exist or is not a file")
    fdeps = ymli['analysis'][fname]
    if fdeps is not None:
        if dep in fdeps:
            warn(f"sk: {dep} is already a dependency of {fname}")
            return False
    if True in [i in dep for i in wildcard_symbols]:
       warn(f"sk: Error: Filename ({dep}) cannot have wildcard symbols ({' '.join(wildcard_symbols)})")
       return False
    return True


def add(files, deps=list(), force=False, copy_deps=None):
    """ Add files and dependencies to them
    files -- page file list
    deps -- dependency file list
    force -- bool whether to add additional index files
    copy_deps -- file to copy dependencies from
    """
    if deps is None:
        deps = list()
    ymli = yaml_in()
    if copy_deps is not None:
        # copy_deps(src,dest)
        copy_deps = copy_deps[0]
        if copy_deps not in ymli["analysis"]:
            reterr(f"sk: Error: file {copy_deps} is not included")
        deps2copy = ymli["analysis"][copy_deps]
        if not ((deps2copy is None) or (len(deps2copy) == 0)):
            deps = list(set(deps + deps2copy))
            warn(f"sk: Copying {copy_deps} dependencies")
        else:
            warn(f"sk: Warning: {copy_deps} has no dependencies")
    # add files
    for fname in files:
        # Add script
        # Should the script be addded?
        add_fname = add_check(fname, ymli, force, deps) 
        if add_fname: 
            # add near scripts in the same directory
            if len(ymli["analysis"].keys()) > 0:
                commpath = os.path.commonpath(list(ymli["analysis"].keys()))
            else:
                commpath = ""
            tab_name = os.path.dirname(rm_commdir(fname, commpath))
            all_tabs = list(map(lambda f:
                os.path.dirname(rm_commdir(f, commpath)),
                ymli["analysis"].keys()))
            tab_matches = list(filter(lambda i:
                all_tabs[i] == tab_name, range(len(all_tabs))))
            if (tab_name != "") and (len(tab_matches) != 0):
                ymli["analysis"].insert(tab_matches[-1] + 1, fname, [])
            else:
                ymli['analysis'][fname] = None
            warn(f"sk: Added {fname}")
        # Add dependencies
        for dep in deps:
            # Should the dep be added?
            add_dep = add_dep_checks(fname, ymli, force, dep) 
            if add_dep:
                if ymli['analysis'][fname] is None:
                    ymli['analysis'][fname] = []
                ymli['analysis'][fname].append(dep)
                warn(f"sk: Added dependency {dep} to {fname}")
                if dep in ymli["analysis"].keys():
                    warn(f"sk:   {fname} will be executed after any executions of {dep}")
                else:
                    warn(f"sk:   {fname} will be executed after any modifications to {dep}")
    yaml_dump(ymli)

def rm(files, deps):
    """ Delete files and dependencies from them
    files - page file list
    deps - dependency file list
    """
    if deps is None:
        deps = list()
    ymli = yaml_in(need_pages=True)
    for fname in files:
        # check if rmd included
        if fname not in ymli['analysis'].keys():
            warn(f"sk: Warning: File {fname} not included")
            continue
        # delete script entry if no dependencies specified
        if len(deps) == 0:
            del ymli['analysis'][fname]
            warn(f"sk: {fname} removed")
            # Check if fname was a dependency for other scripts
            for val in ymli['analysis'].values():
                if val is not None:
                    if fname in val:
                        warn(f"sk: Warning: {fname} is still a dependency of other scripts")
                        warn(f"sk:   Use sk del -d {fname} <script> to change this")  
        # delete only deps if deps specified
        else:
            if ymli['analysis'][fname] is None:
                warn(f"sk: Warning: File {fname} has no dependencies")
                continue
            for dep in deps:
                if dep in ymli['analysis'][fname]:
                    ymli['analysis'][fname].remove(dep)
                    warn(f"sk: dependency {dep} removed from {fname}")
                else:
                    warn(f"sk: no dependency {dep} found for {fname}")
                if len((ymli['analysis'][fname])) == 0:
                    ymli['analysis'][fname] = None
        if os.path.splitext(os.path.basename(fname))[0] == "index":
            index_list = get_indexes(ymli)
            if len(index_list) == 0:
                warn(f"sk: Using system template index.Rmd as homepage")
                os.utime(os.path.join(get_sk_exe_dir(), "template", "index.Rmd"), None)
            elif len(index_list) == 1:
                os.utime(index_list[0], None)
    yaml_dump(ymli)

def site(args):
    """Adds the custom link to the 'More' tab"""
    ymli = yaml_in()
    if "site" not in ymli.keys():
        ymli["site"] = dict()
    # print the links
    if args.get:
        for k in ymli["site"].keys():
            print(f"{k} => {ymli['site'][k]}")
        return
    if args.delete and args.name is None:
        reterr("sk: Error: '--name' has to be specified for deletion")
    if args.delete:
        # handle deletion
        del_ret = ymli["site"].pop(args.name[0], None)
        if del_ret is not None:
            print(f"sk: Removed link named '{args.name[0]}'")
        else:
            print(f"sk: Link '{args.name[0]}' not found")
        yaml_dump(ymli)
        return
    if (args.name is None) or (args.link is None):
        reterr("sk: Error: both '--name' and '--link' have to be specified")
    ymli["site"][args.name[0]] = args.link[0]
    print(f"sk: Added link {args.link[0]} under {args.name[0]}")
    yaml_dump(ymli)
