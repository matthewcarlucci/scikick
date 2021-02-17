Snakemake workflow which utilize a Scikick project's scikick.yml configuration file.

Two main sets of rules are used:

`notebook_rules` to execute various formats of notebooks to generate markdown outputs.

`site_rules` rules generate a final report from the markdown outputs.

`experimental_rules` can be called on explicitly to generate other output formats.

A Snakefile given in a users project root will also be included in the workflow to execute project-specific processing tasks.

