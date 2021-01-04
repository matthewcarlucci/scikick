# Currently depends on variables from main Snakefile
# Each rule here handles exe => md weaving 

rule sk_exe_rmd:
    input:
        deps = lambda wildcards: rmd_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe"),
        sk_knit = os.path.join(script_dir, "knit.R") 
    output:
        md = skconfig.md_pattern    
    message: "Executing code in {input.exe}, outputting to {output.md}"
    params:
        simplified_input = len("{input.exe}"),
        data_parent = data_parent,
        template_dir = template_dir,
        script_dir = script_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' {params.template_dir} \
        {params.data_parent} {params.script_dir} '{logger.logfile}' \
        '{skconfig.index_exe}'" \
        % os.path.join(script_dir, "execute_code.R")

rule sk_exe_r:
    input:
        deps = lambda wildcards: r_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe"),
        sk_knit = os.path.join(script_dir, "knit.R") 
    output:
        md = skconfig.md_pattern
    message: "Executing code in {input.exe}, outputting to {output.md}"
    params:
        simplified_input = len("{input.exe}"),
        data_parent = data_parent,
        template_dir = template_dir,
        script_dir = script_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.exe}' '{output.md}' {params.template_dir} \
        {params.data_parent} {params.script_dir} '{logger.logfile}' \
        '{skconfig.index_exe}'" \
        % os.path.join(script_dir, "execute_code.R")

rule sk_exe_ipynb:
    input:
        deps = lambda wildcards: ipynb_inputs[wildcards.out_base],
        exe = lambda wildcards: skconfig.get_info(wildcards.out_base,"exe"),
    output:
        md = skconfig.md_pattern 
    message: "Executing code in {input.exe}, outputting to {output.md}"
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{out_base}" if skconfig.snakefile_arg("benchmark") != "" else ""
    params:
        outdir=lambda wildcards, output: os.path.dirname(output[0])
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "jupyter nbconvert --to markdown --execute --output-dir='{params.outdir}' '{input.exe}'" 

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
    shell: "cp {input} {output}"


