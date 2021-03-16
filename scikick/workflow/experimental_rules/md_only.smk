# By default sk_exe_ipynb from execute_code.smk takes priority
ruleorder: sk_exe_ipynb > sk_noexe_ipynb
rule sk_noexe_ipynb:
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
    shell: "jupyter nbconvert --to markdown --ExecutePreprocessor.timeout -1 --output-dir='{params.outdir}' '{input.exe}' > '{log}' 2>&1"

