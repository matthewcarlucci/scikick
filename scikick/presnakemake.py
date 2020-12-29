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
#generate_html_exe = os.path.join(script_dir, "render.R")
generate_html_exe = os.path.join(script_dir, "render_minimal.R")
snake_includes = []
snake_includes.append(os.path.join(script_dir, "custom.smk"))
snake_includes.append(os.path.join(script_dir, "rmarkdown.smk"))

###########################################
# Converting scikick config to I/O deps
# for the snakemake rules
###########################################

site_yaml_files = skconfig.get_site_yaml_files()

# Depending on upstream exes' resulting 'md'
exe_inputs = skconfig.inferred_inputs
#md_outputs =

# For referencing pages without file extension
rmd_dict = {}
for key in skconfig.analysis:
	rmd_dict[os.path.splitext(key)[0]] = key

# add a template index to the workflow if index doesn't exist
sys_index = os.path.join(template_dir, 'index.Rmd')
index_list = list(filter(lambda f: os.path.basename(f) == "index", \
	rmd_dict.keys()))

# Use the template as homepage if there are multiple or no index files
if len(index_list) != 1:
	# Verbose mode only?
	#warn("sk: Include an index.Rmd to add content " +\
	#	"to the required index.html page")
	rmd_dict['index'] = exe_inputs['index'] = [sys_index]
else:
	rmd_dict['index'] = rmd_dict.pop(os.path.splitext(index_list[0])[0], None)
	exe_inputs['index'] = exe_inputs.pop(os.path.splitext(index_list[0])[0], None)
index_rmd = rmd_dict["index"]

# Create dictionaries for each file extension
def get_inputs(exe_inputs,ext):
    # filter exe_inputs for a given file extension
    ret = dict(filter(lambda x: os.path.splitext(x[1][0])[-1].lower()==ext.lower(), exe_inputs.items()))
    return ret

r_inputs = get_inputs(exe_inputs,'.R')
md_inputs = get_inputs(exe_inputs,'.md')
rmd_inputs = get_inputs(exe_inputs,'.Rmd')
ipynb_inputs = get_inputs(exe_inputs,'.ipynb')
