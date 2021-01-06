"""General scikick.yml modifier functions"""
import os
import re
from scikick.utils import reterr, warn, get_sk_exe_dir
from scikick.yaml import yaml_in, yaml_dump, rm_commdir, get_indexes, supported_extensions

# This should be simplified or split
class ScikickConfig:
    """
    A class for storing and manipulating the configuration
    """

    def read(self, need_pages=False):
        """Read scikick.yml, eventually to replace yaml_in()"""
        self.config = yaml_in(self.filename, need_pages)

    def __init__(self, filename="scikick.yml",need_pages=False):
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
        return os.path.normpath(self.config['reportdir'])

    ### Snakemake wildcard patterns
    @property
    def html_pattern(self):
        return os.path.normpath(os.path.join(self.report_dir,'out_html','{out_base}.html'))
    @property
    def md_pattern(self):
        return os.path.normpath(os.path.join(self.report_dir,'out_md','{out_base}.md'))


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
    def exes(self):
        """ Get all user defined exes (i.e. excluding system index)
        """
        return list(self.analysis.keys())

    @property
    def index_exes(self):
        """ Get all user defined index exes
        """
        ret = get_indexes(self.config)
        return ret

    @property
    def index_exe(self):
        """ Which source file to use for index page
        """
        if len(self.index_exes) == 1:
            return self.index_exes[0]
        else:
            return os.path.join(get_sk_exe_dir(),"template", 'index.Rmd')

    @property
    def homepage(self):
        return os.path.normpath(os.path.join(self.report_dir,'out_html','index.html'))

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
        for exe in self.exes:
            out_base = self.get_info(exe,"out_base")
            deps[out_base] = [exe] # script itself is an input file
            if isinstance(self.analysis[exe], list):
                for dep in self.analysis[exe]:
                    depext = os.path.splitext(dep)[-1]
                    depisexeable = depext.lower() in [x.lower() for x in supported_extensions]
                    depisexe = dep in self.exes
                    if depisexeable and depisexe:
                        deps[out_base].append(self.get_info(dep,"md"))
                    elif not depisexeable and depisexe:
                        warn("sk: Unsupported executable found in scikick.yml")
                    else:
                        deps[out_base].append(dep)
        if self.index_exe not in self.exes:
            deps['index'] = [self.index_exe]
        return deps

    def get_site_yaml_files(self):
        ret=[os.path.normpath(os.path.join(self.report_dir, "out_md", dir,
            "_site.yml"))
        for dir in set([os.path.dirname(a) for a in self.exes])]
        index_site_yaml = os.path.normpath(os.path.join(self.report_dir,
            "out_md", "_site.yml"))
        if index_site_yaml not in ret:
            ret.append(index_site_yaml)
        return ret

    # Creating universal translation between exe=>md=>html
    @property
    def exe_core_outputs(self):
        """
        For each exe, return a list of exe, md, html, base, out_base, ext
        This function is meant to contain all of the logic of expected I/O
        Every string in the result should be unique
        """
        ret = []
        for exe in self.exes:
            base = os.path.splitext(exe)[0]
            ext = os.path.splitext(exe)[-1]
            if len(self.index_exes) == 1 and exe in self.index_exes:
                md = os.path.normpath(f"{self.report_dir}/out_md/index.md")
                html = os.path.normpath(f"{self.report_dir}/out_html/index.html")
                out_base = 'index'
            else:
                md = os.path.normpath(f"{self.report_dir}/out_md/{base}.md")
                html = os.path.normpath(f"{self.report_dir}/out_html/{base}.html")
                out_base = base
            ret.append([exe,md,html,base,out_base,ext])
        # If using the system index, add it as well
        if len(self.index_exes)==0:
            exe = self.index_exe
            base = os.path.splitext(exe)[0]
            ext = os.path.splitext(exe)[-1]
            md = os.path.normpath(f"{self.report_dir}/out_md/index.md")
            html = os.path.normpath(f"{self.report_dir}/out_html/index.html")
            out_base = 'index'
            ret.append([exe,md,html,base,out_base,ext])
        return ret

    # Accessing various workflow properties
    @property
    def out_bases(self):
        return [element[4] for element in self.exe_core_outputs]
    @property
    def bases(self):
        return [element[3] for element in self.exe_core_outputs]

    def get_info(self,value,element='all'):
        """
        Generic and flexible accesor of paths associated with a file
        input an exe/md/html/base/out_base and get the matching set
        value -- a path to lookup
        element -- which path to return
        """
        # labels matching exe_core_output indicies
        labs = ['exe', 'md', 'html', 'base', 'out_base', 'ext']
        for blob in self.exe_core_outputs:
            if os.path.normpath(value) in blob:
                if element == 'all':
                    return blob
                else:
                    return blob[labs.index(element)]

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


