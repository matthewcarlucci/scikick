###########################################
# Imports
###########################################

from scikick.config import ScikickConfig
from scikick.utils import warn, get_sk_exe_dir, get_sk_snakefile
import tempfile
# For debugging outside snakemake context
import os
import sys
import glob

###########################################
# Workflow variables
###########################################

# import the scikick.yml config file
skconfig = ScikickConfig(need_pages=False) # no pages means empty site

# Getting properties
report_dir = skconfig.report_dir # directories
data_parent = "output"

# scikick system files
exe_dir = get_sk_exe_dir()
workflow_dir = os.path.join(exe_dir, "workflow")
snake_src = get_sk_snakefile()
generate_html_exe = os.path.join(workflow_dir,"site_rules", "render_minimal.R")

# Add on experimental workflows for explicit usage only
snake_includes = glob.glob(os.path.join(workflow_dir,"experimental_rules") + "/*.smk")

###########################################
# Converting scikick config to I/O deps
# for the snakemake rules
###########################################

# Depending on upstream exes' resulting 'md'
exe_inputs = skconfig.inferred_inputs

# Create dictionaries for each file extension
def get_inputs(exe_inputs,ext):
    # filter exe_inputs for a given file extension
    ret = dict(filter(lambda x: os.path.splitext(x[1][0])[-1].lower()==ext.lower(), exe_inputs.items()))
    return ret

r_inputs = get_inputs(exe_inputs,'.R')
md_inputs = get_inputs(exe_inputs,'.md')
rmd_inputs = get_inputs(exe_inputs,'.Rmd')
ipynb_inputs = get_inputs(exe_inputs,'.ipynb')
py_inputs = get_inputs(exe_inputs,'.py')
