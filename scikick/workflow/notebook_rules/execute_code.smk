# Currently depends on variables from main Snakefile
# Each rule here handles exe => md weaving 

# Notes:
# log files take stdout and stderr. 2>&1 redirects stderr to stdout

rule sk_exe_rmd:
    input:
        deps = lambda wildcards: rmd_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe")
    output:
        md = skconfig.md_pattern    
    message: "Executing code in {input.exe}, outputting to {output.md}"
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else os.path.join(skconfig.report_dir,'benchmark','{out_base}')
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' > '{log}' 2>&1" \
        % os.path.join(workflow_dir,"notebook_rules", "execute_code.R")

rule sk_exe_r:
    input:
        deps = lambda wildcards: r_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe")
    output:
        md = skconfig.md_pattern
    message: "Executing code in {input.exe}, outputting to {output.md}"
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else os.path.join(skconfig.report_dir,'benchmark','{out_base}')
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' > '{log}' 2>&1" \
        % os.path.join(workflow_dir,"notebook_rules", "execute_code.R")

rule sk_exe_ipynb:
    input:
        deps = lambda wildcards: ipynb_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe")
    output:
        md = skconfig.md_pattern 
    message: "Executing code in {input.exe}, outputting to {output.md}"
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else os.path.join(skconfig.report_dir,'benchmark','{out_base}')
    params:
        outdir=lambda wildcards, output: os.path.dirname(output[0])
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "jupyter nbconvert --to markdown --ExecutePreprocessor.timeout -1 --execute --output-dir='{params.outdir}' '{input.exe}' > '{log}' 2>&1" 

# WIP for py script execution as ipynb
# Currently is not compatible with projects also containing ipynb
# rule sk_exe_py:
#     input: exe ="{out_base}.ipynb"
#     output:
#         md = skconfig.md_pattern
#     params:
#         outdir=lambda wildcards, output: os.path.dirname(output[0])
#     message: "Executing code in {input.exe}, outputting to {output.md}"
#     log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
#     shell: "jupyter nbconvert --to markdown --execute --output-dir='{params.outdir}' '{input.exe}' > '{log}' 2>&1" 
# rule sk_exe_py_convert:
#     input: lambda wildcards: py_inputs[wildcards.out_base]
#     output: temp("{out_base}.ipynb")
#     shell: "jupytext --to notebook {input}"

rule sk_exe_md: 
    input: 
        deps = lambda wildcards: md_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe")
    output:
        md = skconfig.md_pattern
    message: "Executing code in {input.exe}, outputting to {output}"
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    shell: "cp {input.exe} {output} > '{log}' 2>&1"


