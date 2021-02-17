rule generate_pdf:
    input: expand(skconfig.md_pattern,out_base = skconfig.out_bases)
    output: "test.pdf"
    shell: "pandoc {input} --to pdf > {output}"
