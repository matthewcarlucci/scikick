# Currently depends on variables from main Snakefile

yaml_gen_script = os.path.join(script_dir, 'render_site_yamlgen.py')

localrules: generate_html, generate_site_files

# Generate all _site.yml files
rule generate_site_files:
    input:
        "scikick.yml",
        yaml_gen_script
    output: site_yaml_files
    message: "Creating site layout from scikick.yml"
    script: yaml_gen_script

# md => HTML via rmarkdown::render
rule generate_html:
	input:
        # Should be the _site.yml in the same directory
		yaml = "{report_dir}/out_md/_site.yml",
		md = "{report_dir}/out_md/{report_step}.md"
	output:
		html = "{report_dir}/out_html/{report_step}.html"
	message: "Converting {input.md} to {output.html}"
	params:
		template_dir = template_dir,
		index_html = lambda w: os.path.join(os.path.relpath(
			os.path.join(report_dir, "out_md"),
			os.path.dirname(os.path.join(report_dir,
				"out_md", "%s.md" % w.report_step))), "index.html")
    # Replace with generic envs that should cover most use cases
	conda: skconfig.snakefile_arg("conda") 
	singularity: skconfig.snakefile_arg("singularity") 
	# using 'shell:' instead of 'script:' for compatibility with renv
	shell: "Rscript {generate_html_exe} '{input.md}' '{output}' {params.template_dir} '{params.index_html}'"

