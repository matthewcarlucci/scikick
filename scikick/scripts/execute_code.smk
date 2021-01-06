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
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' > {log} 2>&1" \
        % os.path.join(script_dir, "execute_code.R")

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
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' > {log} 2>&1" \
        % os.path.join(script_dir, "execute_code.R")

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
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    params:
        outdir=lambda wildcards, output: os.path.dirname(output[0])
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "jupyter nbconvert --to markdown --execute --output-dir='{params.outdir}' '{input.exe}' > {log} 2>&1" 

# WIP for py script execution as ipynb
#rule sk_exe_py:
#    input: "{out_base}.py"
#    output: temp("{out_base}.ipynb")
#    shell: "jupyter convert --to notebook {input}"

rule sk_exe_md: 
    input: lambda wildcards: md_inputs[wildcards.out_base]
    output:
        md = skconfig.md_pattern
    message: "Executing code in {input}, outputting to {output}"
    log: '%s/logs/{out_base}_logs.txt' % skconfig.report_dir
    shell: "cp {input} {output} > {log} 2>&1"


