from shutil import copyfile
from scikick.workflow import *
import scikick

# Currently depends on variables from main Snakefile

yaml_gen_script = os.path.join(script_dir, 'render_site_yamlgen.py')

localrules: generate_html, generate_site_files

# Generate all _site.yml files
rule generate_site_files:
    input: 
        "scikick.yml",
        yaml_gen_script
    output: skconfig.get_site_yaml_files()
    message: " Creating site layout from scikick.yml"
    script: yaml_gen_script

rule md_postprocess:
   input: 
       md = skconfig.md_pattern,
       yml = 'scikick.yml'
   output: temp("report/out_md/{out_base}_tmp.md")
   message: " Adding project map to {input.md} as {output}"
   run:
      # Content
      with open(input.md,"r") as orig:
          with open(output[0],"w") as out:
              out.write(orig.read())
      # Append svg - allow for failures in this step as it is non-essential
      try:
          outdir = os.path.dirname(wildcards.out_base)
          md_root = os.path.join(skconfig.report_dir,"out_md")
          path_to_root = os.path.relpath(md_root, os.path.join(md_root,outdir))
          dg = make_dag(skconfig,"dot",path_from_root=path_to_root,subject=wildcards.out_base)
          proj_map = '<details><summary> Next (Project Map) </summary>\n'
          svg = dg.pipe(format="svg").decode('utf-8')
          # Remove doctype string
          proj_map = proj_map + '\n'.join(svg.split('\n')[3:])
          proj_map = proj_map + '</details><hr></hr>'
      except Exception as e:
          warn(f"sk:  Warning: error during project map addition: {e}")
          pass
      else:
          with open(output[0], "a") as md:
              md.write(proj_map)

# md => HTML via rmarkdown::render
rule generate_html:
	input:
        # Should be just the _site.yml in the same directory (would need to split out_base into dir/file)
		yaml = skconfig.get_site_yaml_files(),
		md = "report/out_md/{out_base}_tmp.md"
	output:
		html = skconfig.html_pattern 
    # input.md must match expected md files for sk status
	message: "  Converting {input.md} to {output.html}"
	params:
        # path to index.html from output.html 
		index_html = lambda w: os.path.join(os.path.relpath(
			os.path.join(report_dir, "out_md"),
			os.path.dirname(os.path.join(report_dir,
				"out_md", "%s.md" % w.out_base))), "index.html")
    # Replace with generic envs that should cover most use cases
	conda: skconfig.snakefile_arg("conda") # 'env/rmarkdown.yml'
	singularity: skconfig.snakefile_arg("singularity") # 'docker://rocker/tidyverse'
	# using 'shell:' instead of 'script:' for compatibility with renv
	shell: "Rscript {generate_html_exe} '{input.md}' '{output}' '{params.index_html}'"

