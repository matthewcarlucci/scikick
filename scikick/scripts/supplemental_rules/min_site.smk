# An example of a minimal custom output format

rule min_site:
	input:
		expand('{report_dir}/out_custom/{out_base}.html',
			out_base = skconfig.out_bases, report_dir = skconfig.report_dir)

rule min_site_page:
    input: skconfig.md_pattern
    output: os.path.normpath(os.path.join(skconfig.report_dir, "out_custom", "{out_base}.html"))
    # pandoc must execute from input directory
    params:
        indir=lambda wildcards, input: os.path.dirname(input[0]),
        inname=lambda wildcards, input: os.path.basename(input[0]),
        outname=lambda wildcards, output: os.path.basename(output[0])
    message: "Converting {input} to {output}"
    conda: 'min_site.yml' 
    shell: "(cd {params.indir} && pandoc --standalone {params.inname} > {params.outname}) && mv {params.indir}/{params.outname} {output}" 

