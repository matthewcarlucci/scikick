###########################################
# Imports
###########################################

from scikick.config import ScikickConfig
from scikick.utils import warn, get_sk_exe_dir, get_sk_snakefile
import tempfile
# For debugging outside snakemake context
import os
import sys

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
script_dir = os.path.join(exe_dir, "scripts")
template_dir = os.path.join(exe_dir, "template")
snake_src = get_sk_snakefile()
generate_html_exe = os.path.join(script_dir, "render_minimal.R")

# Add on experimental workflows for explicit usage only
snake_includes = []
snake_includes.append(os.path.join(script_dir, "supplemental_rules/custom.smk"))
snake_includes.append(os.path.join(script_dir, "supplemental_rules/rmarkdown.smk"))

###########################################
# Converting scikick config to I/O deps
# for the snakemake rules
###########################################

site_yaml_files = skconfig.get_site_yaml_files()

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
