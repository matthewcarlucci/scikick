# Example scikick project

An example project, meant as an introduction to scikick.

## Files

```bash
code/
├── r_version.Rmd  # 0. Print the R version
├── generate.sh    # 1. Shell script to generate sample data
├── generate.Rmd   # 2. Run the shell script and print its results
└── base_plot.Rmd  # 3. Plot the results from the shell script
```

## Using scikick

Firstly, initiate a scikick project.

```bash
# Create a scikick.yml config
sk init
# Create an output/ dir
mkdir output
```

Add files to scikick.yml that will base the completed website

```bash
# Add generate.Rmd, which depends on the shell script
sk add code/generate.Rmd -d code/generate.sh
# Add base_plot.Rmd, which depends on the results of generate.Rmd
sk add code/base_plot.Rmd -d code/generate.Rmd
# r_version.Rmd doesn't depend on anything
sk add code/r_version.Rmd
```

Run scikick to create the webpage

```bash
sk run
# resulting webpage in report/out_ht
```

## Bonus: singularity

File `report/out_html/code/r_version.html` should print the current R version.
To run the Rmds in a container using `singularity`:

```bash
# Use container with R version 4.0.0
# Since the container needs to include 'rmarkdown' package, 
# 'rocker/tidyverse' is used instead of 'r-base'
sk snake --singularity docker://rocker/tidyverse:4.0.0
# To use the container which we just set,
# an argument needs to be passed to Snakemake
touch code/*
sk run -s '--use-singularity'
```
After running this, `report/out_html/code/r_version.html` should include R version 4.0.0.
