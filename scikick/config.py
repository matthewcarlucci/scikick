"""General scikick.yml modifier functions"""
import os
import re
from ruamel.yaml.compat import ordereddict
from scikick.utils import reterr, warn
from scikick.yaml import yaml_in, yaml_dump, rm_commdir, get_indexes, supported_extensions


class ScikickConfig:
    """
    A class for storing and manipulating the configuration
    """

    def read(self, need_pages=False):
        """Read scikick.yml, eventually to replace yaml_in()"""
        self.config = yaml_in(self.filename, need_pages)

    def __init__(self, filename=None,need_pages=False):
        if filename is None:
            self.filename = "scikick.yml"
        else:
            self.filename = filename
        self.read(need_pages=need_pages)

    @property
    def analysis(self):
        """Get 'analysis:' dict from scikick.yml"""
        if self.config['analysis'] is not None:
            return self.config['analysis']
        reterr("No analysis field found in scikick config")
        return None

    @property
    def report_dir(self):
        """Get the value of 'reportdir' from scikick.yml"""
        if self.config['reportdir'] is None:
            reterr("sk: Error: Report directory (reportdir) has not been set in scikick.yml")
            # Eventually it may be safe to set this value dynamically
            #warn("sk: Warning: Setting reportdir to 'report' and writing to scikick.yml")
            #self.config['reportdir'] = "report"
            # yaml_dump may be unsafe if self.config has been changed elsewhere
            # A direct modification of reportdir would be better
            # yaml_dump(self.config)    
        return self.config['reportdir']
    
    def snakefile_arg(self, arg, set_default=False):
        """ Get a valid snakefile_arg option """ 
        if arg not in ["singularity", "conda", "benchmark", "threads"]:
            value = None
        else:
            # Use default values that snakemake will accept
            if arg is "threads":
                value = int(1)
            else:
                value = "" 
            # Get the real value if it exists
            yml = self.config 
            if "snakefile_args" in yml.keys():
                if arg in yml["snakefile_args"]:
                     value = yml["snakefile_args"][arg]
        return value


    @property
    def inferred_inputs(self):
        """Return dictionary of {exe -> [dependencies], ...}
        For use while defining snakemake rules I/O
        Assumptions: 
        1. All analysis keys have a rule for exe.* => exe.md
        2. deps that are also exe files actually depend on exe.md
        3. deps that are not exe depend on the file itself
        """
        deps = {}
        for exe in self.analysis.keys():
            exe_name = os.path.splitext(exe)[0]
            deps[exe_name] = [exe] # script itself is an input file
            if isinstance(self.analysis[exe], list):
                for dep in self.analysis[exe]:
                    depext = os.path.splitext(dep)[-1]
                    depisexeable = depext.lower() in [x.lower() for x in supported_extensions]
                    depisexe = dep in self.analysis.keys()
                    if depisexeable and depisexe:
                        out_md_file = os.path.join(self.report_dir, "out_md", \
                                                   re.sub(f'{depext}$', ".md", dep, \

                                                          flags=re.IGNORECASE))
                        deps[exe_name].append(out_md_file)
                    elif not depisexeable and depisexe:
                        warn("sk: Unsupported executable found in scikick.yml")
                    else:
                        deps[exe_name].append(dep)
        return deps


    def get_site_yaml_files(self):     
        ret=[os.path.join(self.report_dir, "out_md", dir, "_site.yml")
        for dir in set([os.path.dirname(a) for a in self.analysis.keys()])]
        index_site_yaml = os.path.join(self.report_dir, "out_md", "_site.yml")
        if index_site_yaml not in ret:
            ret.append(index_site_yaml)

        return ret


# to allow hierarchy #232 this and everything it dependends on will need changes
def get_tabs(config):
    """Return a list of tab names determined from scikick.yml
    'analysis:' dict
    config -- scikick.yml as an ordereddict
    """
    # remove index file beforehand
    index_list = get_indexes(config)
    if len(index_list) == 1:
        config["analysis"].pop(index_list[0], None)
    # get tab strucutre
    tabs = {}
    for i in config["analysis"].keys():
        tabname = os.path.dirname(i)
        if tabname == "":
            tabname = "./"
        if tabname not in tabs.keys():
            tabs[tabname] = []
        if tabname == "./":
            tabs[tabname].append("./%s" % os.path.splitext(i)[0])
        else:
            tabs[tabname].append(os.path.splitext(i)[0])
    # get the common dir suffix for all files
    commpath = os.path.commonpath(tabs.keys())
    tabs = ordereddict(map(lambda k: (rm_commdir(k, commpath), tabs[k]), \
                           tabs.keys()))
    # all files in './' have their own tab
    if "./" in tabs.keys():
        wd_idx = list(tabs.keys()).index("./")
        tabs["./"].reverse()
        for root_file in tabs["./"]:
            fname = os.path.basename(root_file)
            if fname in tabs.keys():
                fname = f"{fname}.Rmd"
            tabs.insert(wd_idx, fname, [root_file])
        del tabs["./"]
    return tabs

# sk layout

def rearrange_submenus(submenu, order, config, tabs):
    """Change the order of submenus under a tab
    submenu -- the name of the tab which to reorder
    order -- the new order (list of indices 1...n) of the submenu
    config -- yaml_in() output
    tabs -- get_tabs(config) output
    """
    if submenu not in tabs:
       reterr(f"sk: Error: No tab named \"{submenu}\"")
    submenu_contents = get_submenu_items(config, submenu)
    if len(order) == 0:
        for i in range(len(submenu_contents)):
            print(f"{i + 1}:  {submenu_contents[i]}")
    else:
        order = new_tab_order(order, submenu_contents)
        if order is None:
            reterr("sk: Wrong index list provided, " + \
                   "must be a unique list of tab indices")
        config["analysis"] = reordered_submenu(config["analysis"],
                                               submenu_contents, order)
        yaml_dump(config)
        # print layout again
        submenu_contents = get_submenu_items(config, submenu)
        for i in range(len(submenu_contents)):
            print(f"{i + 1}:  {submenu_contents[i]}")

def rearrange_tabs(order, config, tabs):
    """Change the order of tabs in the navigation bar
    order -- the new order (list of indices 1...n) of the tabs
    config -- yaml_in() output
    tabs -- get_tabs(config) output
    """
    if len(order) == 0:
        for i in range(len(tabs.keys())):
            print(f"{i + 1}:  {list(tabs.keys())[i]}")
        return
    # get the new ordering based on the argument list
    order = new_tab_order(order, tabs.keys())
    if order is None:
        reterr("sk: Wrong index list provided, " + \
               "must be a unique list of tab indices")
    # do the reordering of config['analysis']
    new_analysis = reordered_analysis(tabs, config['analysis'], order)
    # copy each item one by one from the new dict to the old one
    config['analysis'].clear()
    for k in new_analysis.keys():
        config['analysis'][k] = new_analysis[k]
    yaml_dump(config)
    # print layout again
    tabs = get_tabs(config)
    for i in range(len(tabs.keys())):
        print(f"{i + 1}:  {list(tabs.keys())[i]}")

def new_tab_order(args_order, tab_keys):
    """Get the new order of tabs based on the user input.
    Returns a list of indices, which would be used to reorder the
    'analysis' keys in scikick.yml
    args_order -- order provided by the user (list of indices as strings)
    tabs -- list of tab names
    """

    # in case 9 or less tabs, the the order can be without spaces
    if len(args_order) == 1:
        order = list(map(lambda x: int(x) - 1, str(args_order[0])))
    else:
        order = list(map(lambda x: x - 1, args_order))
    if len(set(order)) == len(order) and \
            len(order) <= len(tab_keys) and \
            min(order) >= 0 and max(order) < len(tab_keys):
        # fill the rest of idxs if not all provided
        for i in range(len(tab_keys)):
            if i not in order:
                order.append(i)
        return order
    return None


def reordered_analysis(tabs, old_analysis, order):
    """Reorder the 'analysis' dict in scikick.yml.
    Returns the reordered 'analysis' dict which produces
    the differently ordered tab list in all pages
    tabs -- list of tab names
    old_analysis -- 'analysis' dict from scikick.yml
    order -- list of indices
    """
    new_analysis = ordereddict()
    for ord_no in order:
        for rmd in tabs[list(tabs.keys())[ord_no]]:
            norm_rmd = os.path.normpath(rmd)
            curr_key = list(filter(lambda x: \
                                       os.path.splitext(x)[0] == norm_rmd, \
                                   old_analysis.keys()))[0]
            new_analysis[curr_key] = old_analysis[curr_key]
    return new_analysis

# Submenus

def get_submenu_items(config, submenu):
    '''Get names of all submenu items in the same order
    as in the submenu in the HTML
    config -- scikick.yml dict
    submenu -- name of tab/submenu
    '''
    rmds = list(config["analysis"].keys())
    commpath = os.path.commonpath(rmds)
    trimmed_rmds = map(lambda r: rm_commdir(r, commpath), rmds)
    submenu_rmds = filter(lambda r:
        os.path.dirname(r) == submenu or \
        ((not os.path.isdir(os.path.join(commpath, r[:len(submenu)]))) and \
        r[:len(submenu)] == submenu),
        trimmed_rmds)
    full_rmds = list(map(lambda r: os.path.join(commpath, r), submenu_rmds))
    return full_rmds

def reordered_submenu(analysis, submenu_contents, order):
    '''reorder config['analysis'] based on the submenu ordering
    config -- scikick.yml dict
    submenu_contents -- list of rmds belonging to the submenuu
    order -- list of integers specifying order
    '''
    first_item_no = list(analysis.keys()).index(submenu_contents[0])
    new_order = list(map(lambda i: i + first_item_no, order))
    new_analysis = analysis.copy()
    new_analysis.clear()
    for i in range(0, len(analysis.keys())):
        key = list(analysis.keys())[i]
        if i < first_item_no:
            new_analysis[key] = analysis[key]
        elif i < first_item_no + len(new_order):
            neword_key = list(analysis.keys())[new_order[i - first_item_no]]
            new_analysis[neword_key] = analysis[neword_key]
        else:
            new_analysis[key] = analysis[key]
    return new_analysis

### Snakefile arguments

def write_snakefile_arg(arg, val):
    """Set the specified arg's value in scikick.yml
    args -- name of the argument
    val -- value of the argument
    """
    yml = yaml_in()
    if "snakefile_args" not in yml.keys():
        yml["snakefile_args"] = dict()
    yml["snakefile_args"][arg] = val
    warn(f"sk: Argument {arg} set to {yml['snakefile_args'][arg]}")
    yaml_dump(yml)


