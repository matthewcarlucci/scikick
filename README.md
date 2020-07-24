[![PyPI version](https://badge.fury.io/py/scikick.svg)](https://badge.fury.io/py/scikick)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/scikick)](https://pypistats.org/packages/scikick)
[](https://pypi.python.org/pypi/scikick/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/scikick.svg)](https://pypi.python.org/pypi/scikick/)
![](https://img.shields.io/badge/lifecycle-maturing-blue.svg)

### Preface: simple workflow definitions for complex notebooks

A thorough data analysis in 
[Rmarkdown](https://rmarkdown.rstudio.com/) or [Jupyter](https://jupyter.org/) 
will involve multiple notebooks which must be executed in a specific order. 
Consider this two stage data analysis where `QC.Rmd` provides a cleaned dataset 
for `model.Rmd` to perform modelling:

```
|-- input/raw_data.csv
|-- code
│   |-- QC.Rmd
│   |-- model.Rmd
|-- output/QC/QC_data.csv
|-- report/out_md
|   |-- _site.yml
|   |-- QC.md
|   |-- model.md
|-- report/out_html
|   |-- QC.html
|   |-- model.html
```

Each of these notebooks may be internally complex, but the essence of this workflow is:

**`QC.Rmd` must run before `model.Rmd`**

This simple definition can be applied to:

- Reproducibly re-execute the notebook collection.
- Avoid unecessary execution of `QC.Rmd` when `model.Rmd` changes.
- Build a shareable report from the rendered notebooks (*e.g.* using `rmarkdown::render_website()`).

Researchers need to be able to get these benefits from simple workflow definitions 
to allow for focus to be on the data analysis.

## **scikick** - your sidekick for managing notebook collections

*scikick* is a command-line-tool for integrating data analyses 
with a few simple commands. The `sk run` command will apply dependency definitions to execute steps in the correct order and build a website of results. 

Common tasks for *ad hoc* data analysis are managed through scikick:

 - Awareness of up-to-date results (via Snakemake)
 - Website rendering and layout automation (by project directory structure)
 - Collection of page metadata (session info, page runtime, git history)
 - Simple dependency tracking of two types:
   - notebook1 must execute before notebook2 (external dependency)
   - notebook1 uses the file functions.R (internal dependency)
 - Automated execution of `.R` as a notebook (with `knitr::spin`) 

Commands are inspired by git for configuring the workflow: `sk init`, `sk add`, `sk status`, `sk del`, `sk mv`.

[Example Output](https://petronislab.camh.ca/pub/scikick_tests/master/)

Scikick currently supports `.R` and `.Rmd` for notebook rendering.

### Getting Started

The following should be installed prior to installing scikick.

|**Requirements**   |**Recommended**|
|---|---|
|python3 (>=3.6)   | [git >= 2.0](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) |
|R + packages `install.packages(c("rmarkdown", "knitr", "yaml","git2r"))`   | [singularity >= 2.4](http://singularity.lbl.gov/install-linux)  |
|[pandoc > 2.0](https://pandoc.org/installing.html)   | [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)   |

### Installation

```
pip install scikick
```

Installation with an environment manager such as [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) is recommended but not required.

```
# To install from GitHub, clone and
python3 setup.py install
```

Begin by executing the demo project or reviewing the main commands of scikick below.

### Demo Project

To initiate a walkthrough of scikick commands (using a demo project).

```
mkdir sk_demo
cd sk_demo
sk init --demo
```

### Main Commands

Below are some brief descriptions of the most useful commands. Run `sk <command> --help` for details and available arguments. Run `sk --help` for the full list of commands.

##### sk init

```
sk init
```

Like `git init`, this should be executed at the project root in an existing or an empty project.

It will check for required dependencies and create `scikick.yml` to store the workflow definition which will be configured using other commands. 

`sk init` can also be used to create data analysis directories and add to `.gitignore` for the project.

##### sk add

```
sk add hw.Rmd
```

Adds the `hw.Rmd` file to the workflow. Supports wildcards for adding in bulk.

##### sk status

`sk add` added `hw.Rmd` to `scikick.yml` and now `sk status` can be used to inspect the workflow state.

```
sk status
#  m--    hw.Rmd
# Scripts to execute: 1
# HTMLs to compile ('---'): 1
```

`sk status` uses a 3 character encoding to show that hw.Rmd requires execution where
the 'm' marking in the first slot indicates the corresponding output file (`report/out_md/hw.md`) is missing.

##### sk run

```
sk run
```

Call on the snakemake backend to generate all out-of-date or missing output files (html pages). 

After execution is finished, the directory structure should look like

```
.
├── hw.Rmd
├── report
│   ├── donefile
│   ├── out_html
│   │   ├── hw.html
│   │   └── index.html
│   └── out_md # has many files we can ignore for now
└── scikick.yml
```

The `report/` directory contains all of scikick's output.

Opening `report/out_html/index.html` in a web browser should show the website 
homepage with one menu item for hw.html (hw.Rmd's output).

### Tracking out-of-date files

Running `sk status` again will result in no jobs to be run.

```
sk status
# Scripts to execute: 0
# HTMLs to compile ('---'): 0
```

And `sk run` will do nothing.

```
sk run
<...>
sk: Nothing to be done.
<...>
```

scikick tracks files using their timestamp (using snakemake) to determine if the report is up-to-date.
For example, if we make changes to hw.Rmd and run scikick

```
touch hw.Rmd
sk run
```

then scikick re-executes to create `report/out_html/hw.html` from scratch.

### Using dependencies

If the project has dependencies between different files, we can make scikick aware of these.

Let's say we have `greets.Rmd` which sources an R script `hello.R`.

```
# Run this to create the files
mkdir code
# code/hello.R
echo 'greeting_string = "Hello World"' > code/hello.R
# code/greets.Rmd
printf "%s\n%s\n%s\n" '```{r, include = TRUE}' 'source("code/hello.R")
print(greeting_string)' '```' > code/greets.Rmd

# Add the Rmd to the workflow
sk add code/greets.Rmd 
```

Be aware that while `code/greets.Rmd` and `code/hello.R` are in the same
directory, all code in scikick is executed from the project root. This means that
`source("hello.R")` will return an error, so instead we need `source("code/hello.R")`.

Let's run `sk run` to create `report/out_html/greets.html`.

Then let's simulate changes to `code/hello.R` to demonstrate what will happen next.

```
touch code/hello.R
sk run
```

Nothing happens since scikick does not know that `code/greets.Rmd` is using `code/hello.R`.
In order to make scikick re-execute `greets.Rmd` when `hello.R` is modified, we have to add it as a dependency with `sk add -d`.

##### sk add -d

```
# add dependency 'code/hello.R' to 'code/greets.Rmd'
sk add code/greets.Rmd -d code/hello.R
```

Now whenever we change `hello.R` and run `sk run`, the file that depends on it (`greets.Rmd`) will be rerun as its results may change.

### Other Useful Commands

##### sk status -v

Use this command to view the full scikick configuration where dependencies for
each file are indented below it.
Out-of-date files are marked with a three symbol code which shows
the reason for their update on the next `sk run`.

##### sk mv

While rearranging files in the project, use `sk mv` so scikick can adjust the workflow definition accordingly.

```
mkdir code
sk mv hw.Rmd code/hw.Rmd
```

If you are using git, use `sk mv -g` to use `git mv`.
Both individual files and directories can be moved with `sk mv`.

##### sk del

We can remove `hw.Rmd` from our analysis with

```
sk del hw.Rmd
```

If the flag '-d' is used (with a dependency specified), only the dependency is removed.

Note that this does not delete the hw.Rmd file.

### Using a Project Template

In order to make our project more tidy, we can create some dedicated directories with

```
sk init --dirs
# creates:
# report/ - output directory for scikick
# output/ - directory for outputs from scripts
# code/ - directory containing scripts (Rmd and others)
# input/ - input data directory
```

If git is in use for the project, directories `report`, `output`, `input` are not
recommended to be tracked.
They can be added to `.gitignore` with

```
sk init --git
```

and git will know to ignore the contents of these directories.

## sk layout

The order of tabs in the website can be configured using `sk layout`.
Running the command without arguments

```
sk layout
```

returns the current ordered list of tab indices and their names:

```
1:  hw.Rmd
2:  greets.Rmd
3:  dummy1.Rmd
4:  dummy2.Rmd
```

The order can be changed by specifying the new order of tab indices, e.g.

```
# to reverse the tab order:
sk layout 4 3 2 1
# the list does not have to include all of the indices (1 to 4 in this case):
sk layout 4 # move tab 4 to the front
# the incomplete list '4' is interpreted as '4 1 2 3'
```

Output after running `sk layout 4`:

```
1:  dummy2.Rmd
2:  hw.Rmd
3:  greets.Rmd
4:  dummy1.Rmd
```

Also, items within menus can be rearranged similarly with

```
sk layout -s <menu name>
```

## Homepage Modifications

The `index.html` is required for the homepage of the website. scikick will create
this content from a template and will also include any content from an `index.Rmd`
added to the workflow with `sk add code/index.Rmd`. 

## Rstudio with scikick

Rstudio, by default, executes code relative to opened Rmd file's location. This
can be changed by going to `Tools > Global Options > Rmarkdown > Evaluate chunks in directory`
and setting to "Current".

## Other scikick files in `report/`
- `donefile` - empty file created during the snakemake workflow that is executed by scikick
- `out_md/`
  - `out_md/*.md` - markdown files that were `knit` from Rmarkdown files
  - `out_md/_site.yml` - YAML file specifying the structure of the to-be-created website
  - `out_md/knitmeta/` - directory of RDS files containing information about javascript libraries that need to be included when rendering markdown files to HTMLs.
  - `out_html/` - contains the resulting HTML files

## External vs Internal Dependencies

**Internal dependencies** - code or files the Rmd uses directly during execution  
**External dependencies** - code that must be executed prior to the page

scikick assumes that any depedency that is not added as a page (i.e. `sk add <page>`) is an internal dependency. 

Currently, only `Rmd` and `R` files are supported as pages. In the future, executables and other file types may be
supported by scikick to allow easy usage of arbitrary scripts as pages.

## Snakemake Backend

Data pipelines benefit from improved workflow execution tools 
(Snakemake, Bpipe, Nextflow), however, *ad hoc* data analysis is often left out of 
this workflow definition. Using scikick, projects can quickly configure reports
to take advantage of the snakemake backend with:

- Basic depedency management (i.e. GNU Make)  
- Distribution of tasks on compute clusters (thanks to snakemake's `--cluster` argument)    
- Software virtualization (Singularity, Docker, Conda)  
- Other snakemake functionality

Users familiar with snakemake can add trailing snakemake arguments during execution with `sk run -v -s`.

### Singularity

In order to run all Rmds in a singularity image, we have to do two things: specify the singularity image and use the snakemake flag that singularity, as a feature, should be used.

```
# specify a singularity image
sk config --singularity docker://rocker/tidyverse
# run the project within a singularity container
# by passing '--use-singularity' argument to Snakemake
sk run -v -s --use-singularity
```
Only the Rmarkdown files are run in the singularity container, the scikick dependencies are
still required outside of the container with this usage.

### Conda

The same steps are necessary to use conda, except the needed file is a conda environment YAML file.

```
# create an env.yml file from the current conda environment
conda env export > env.yml
# specify that this file is the conda environment file
sk config --conda env.yml
# run
sk run -v -s --use-conda
```

## Incorporating with other Pipelines

Additional workflows written in [snakemake](http://snakemake.readthedocs.io/en/stable/) should play nicely with the scikick workflow.

These jobs can be added to the begining, middle, or end of scikick related tasks:

- Beginning 
  - `sk add first_step.rmd -d pipeline_donefile` (where pipeline_donefile is the last file generated by the Snakefile)
- Middle
  - Add `report/out_md/first_step.md` as the input to the first job of the Snakefile.
  - `sk add second_step.rmd -d pipeline_donefile`
- End 
  - Add `report/out_md/last_step.md` as the input to the first job of the Snakefile.
