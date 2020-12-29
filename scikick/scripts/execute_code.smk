
# Currently depends on variables from main Snakefile
# Each rule here handles exe => md weaving 

rule sk_exe_rmd:
    input:
        deps = lambda wildcards: rmd_inputs[wildcards.report_step],
        rmd = lambda wildcards: rmd_dict[wildcards.report_step],
        sk_knit = os.path.join(script_dir, "knit.R") 
    output:
        md = os.path.join(skconfig.report_dir, "out_md", "{report_step}.md")
    message: "Executing code in {input.rmd}, outputting to {output.md}"
    params:
        simplified_input = len("{input.rmd}"),
        data_parent = data_parent,
        template_dir = template_dir,
        script_dir = script_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{report_step}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.rmd}' '{output.md}' {params.template_dir} \
        {params.data_parent} {params.script_dir} '{logger.logfile}' \
        '{index_rmd}'" \
        % os.path.join(script_dir, "execute_code.R")

rule sk_exe_r:
    input:
        deps = lambda wildcards: r_inputs[wildcards.report_step],
        rmd = lambda wildcards: rmd_dict[wildcards.report_step],
        sk_knit = os.path.join(script_dir, "knit.R") 
    output:
        md = os.path.join(skconfig.report_dir, "out_md", "{report_step}.md")
    message: "Executing code in {input.rmd}, outputting to {output.md}"
    params:
        simplified_input = len("{input.rmd}"),
        data_parent = data_parent,
        template_dir = template_dir,
        script_dir = script_dir
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{report_step}" if skconfig.snakefile_arg("benchmark") != "" else ""
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "Rscript %s '{input.rmd}' '{output.md}' {params.template_dir} \
        {params.data_parent} {params.script_dir} '{logger.logfile}' \
        '{index_rmd}'" \
        % os.path.join(script_dir, "execute_code.R")

rule sk_exe_ipynb:
    input:
        deps = lambda wildcards: ipynb_inputs[wildcards.report_step],
        ipynb = lambda wildcards: rmd_dict[wildcards.report_step]
    output:
        md = os.path.join(skconfig.report_dir, "out_md", "{report_step}.md")
    message: "Executing code in {input.ipynb}, outputting to {output.md}"
    conda: skconfig.snakefile_arg("conda")
    singularity: skconfig.snakefile_arg("singularity")
    threads: skconfig.snakefile_arg("threads")
    benchmark: skconfig.snakefile_arg("benchmark") + "{report_step}" if skconfig.snakefile_arg("benchmark") != "" else ""
    params:
        outdir=lambda wildcards, output: os.path.dirname(output[0])
    # 'script:' section causes directories to not get found when using singularity, so 'shell:' is used
    shell: "jupyter nbconvert --to markdown --execute --output-dir='{params.outdir}' '{input.ipynb}'" 

# WIP for py script execution as ipynb
#rule sk_exe_py:
#    input: "{report_step}.py"
#    output: temp("{report_step}.ipynb")
#    shell: "jupyter convert --to notebook {input}"

rule sk_exe_md: 
    input: lambda wildcards: md_inputs[wildcards.report_step]
    output:
        md = os.path.join(skconfig.report_dir, "out_md", "{report_step}.md")
    message: "Executing code in {input}, outputting to {output}"
    shell: "cp {input} {output}"


