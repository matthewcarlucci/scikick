[![PyPI version](https://badge.fury.io/py/scikick.svg)](https://badge.fury.io/py/scikick)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/scikick)](https://pypistats.org/packages/scikick)
[](https://pypi.python.org/pypi/scikick/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/scikick.svg)](https://pypi.python.org/pypi/scikick/)
![](https://img.shields.io/badge/lifecycle-maturing-blue.svg)
[![Snakemake](https://img.shields.io/badge/snakemake-≥5.6.0-brightgreen.svg?style=flat)](https://snakemake.readthedocs.io)

### Preface: simple workflow definitions for complex notebooks in R or Python

A thorough data analysis will involve multiple notebooks (e.g. in [Rmarkdown](https://rmarkdown.rstudio.com/) or [Jupyter](https://jupyter.org/)), but methods for maintaining simple connections between notebooks are not straightforward. 
Consider this two stage data analysis where `QC.Rmd` provides a cleaned dataset 
for `model.Rmd` to perform modeling:

<pre>
|-- input/raw_data.csv
|-- code
<b>│   |-- QC.Rmd</b>
<b>│   |-- model.Rmd</b>
|-- output/QC/QC_data.csv
|-- report/out_html
|   |-- QC.html
|   |-- model.html
</pre>

Each of these notebooks may be internally complex, but the essence of this workflow is:

**`QC.Rmd` must run before `model.Rmd`**

This simple definition can be applied to:

- Re-execute the notebook collection in the correct order.
- Avoid unnecessary execution of `QC.Rmd` when only `model.Rmd` changes.
- Build a shareable report from the rendered notebooks.
- Collect relevant provenance information.

These features enable use of the notebook format for complex analyses, however, 
current methods for achieving this require too much configuration.
Researchers require simple tools to get these benefits and allow for focus to remain on the data analysis. 

## **scikick** - your sidekick for managing notebook collections

*scikick* is a command-line-tool for connecting and executing data analyses 
with a few simple commands. 

![](docs/source/sk_demo.gif)

Common tasks for *ad hoc* data analysis are managed through scikick:

 - Awareness of up-to-date results
 - Website generated according to the project directory structure
 - Collection of page metadata (session info, page runtime, git history)
 - Simple ordering of script executions
 - Defining other script dependencies (e.g. notebook imports `functions.R`)
 - Automated execution of `.R` as R markdown (with `knitr::spin`) 

Commands are inspired by git for configuring the workflow: `sk init`, `sk add`, `sk status`, `sk del`, `sk mv`.

Scikick currently supports `.R` and `.Rmd` for notebook rendering (`.ipynb` can be supported via `jupytext` [paired notebooks](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html)).

[Output website for demo project (`sk init --demo`)](https://petronislab.camh.ca/pub/scikick_tests/master/)

### Installation

|**Requirements**   |**Recommended**|
|---|---|
|python3 (>=3.6)   | [git >= 2.0](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) |
|R + packages `install.packages(c("rmarkdown", "knitr", "yaml","git2r","bookdown"))`   | [singularity >= 2.4](http://singularity.lbl.gov/install-linux)  |
|[pandoc > 2.0](https://pandoc.org/installing.html)   | [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)   |

With the requirements above installed, scikick can be installed using pip:

```
pip install scikick
```

Full installation of requirements within a virtual environment with [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) is still experimental, but may be attempted with:

```
conda install -c tadasbar -c bioconda -c conda-forge scikick
```

To install or upgrade to the latest version of scikick (master branch) directly from GitHub:

```
pip install --upgrade git+https://github.com/matthewcarlucci/scikick.git#egg=scikick
```

## Getting Started

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

`sk status` shows scripts that must be executed and uses a 3 character encoding to show the reason for execution. The 'm' in the first slot here indicates the output file for `hw.Rmd` (`report/out_md/hw.md`) is missing.

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

### Project Templates with `sk init` flags

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
1:  hw
2:  greets
3:  dummy1
4:  dummy2
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
1:  dummy2
2:  hw
3:  greets
4:  dummy1
```

Also, items within menus can be rearranged similarly with

```
sk layout -s <menu name>
```

## Website Homepage

The `index.html` is required for the homepage of the website. Scikick includes
some default content for this page and will add the content to any project defined 
`index.*` file (only one `index.*` file allowed per project).

## Rstudio with scikick projects

If using Rstudio, default code execution will be relative to the Rmd file location. This
can be changed by going to `Tools > Global Options > Rmarkdown > Evaluate chunks in directory`
and setting to "Current".

Additionally, the "knit" button must also be set to execute from the project
directory. 

More [details here](https://bookdown.org/yihui/rmarkdown-cookbook/working-directory.html).

## File hierarchy notes

Scikick allows for hierarchical file structure of Rmd. This is highly useful for 
organization and used by scikick for the website layout.
This use of hierarchy may not support some `md` conversion features of `bookdown::html_document2`.

## Other files in `report/` generated by scikick
- `out_md/`
  - `out_md/*.md` - markdown files that were generated from script execution.
  - `out_md/_site.yml` - YAML file specifying the structure of the to-be-created website
  - `out_md/knitmeta/` - contains RDS files describing required javascript libraries for the final HTML.
  - `out_html/` - contains the resulting HTML files

## External vs Internal Dependencies

`sk add -d` is used to add all dependencies even though "dependency" can have two meanings. Typically everything behaves
as one would expect. Internally dependency type is represented as:

**Internal dependencies** - code or files the Rmd uses directly during execution  
**External dependencies** - code that must be executed prior to the page

Scikick assumes that a script dependency that has also been configured to execute (i.e. `sk add <dependent page>`) is an external dependency and must be executed before the script. Otherwise it is assumed the script must execute after changes to the dependency.

## Snakemake Backend

Data pipelines benefit from improved workflow execution tools 
(Snakemake, Bpipe, Nextflow), however, *ad hoc* data analysis projects often do
not apply these tools. 
Users can quickly configure reports
to take advantage of the snakemake backend and use snakemake arguments with `sk run -v -s <snakemake arguments>`. 
Snakemake is responsible for:

- Basic dependency management (i.e. Make-like execution)  
- Parallelization: `sk run -s -j <number of cores>` where scikick assumes each page
uses just a single core.
- Distribution of tasks on compute clusters (Using snakemake's `--cluster` or `--profile` arguments)    
- Software virtualization with: Singularity, Docker, Conda  
- Other snakemake functionality (via passed arguments)

### Singularity

In order to run all Rmds in a singularity image, specify the singularity image and use the singularity snakemake flag.

```
# specify a singularity image
sk config --singularity docker://rocker/tidyverse
# run the project within a singularity container
# by passing '--use-singularity' argument to Snakemake
sk run -v -s --use-singularity
```
Scripts will be run inside the singularity container. The container must
have at least the R dependencies installed (most R-based containers have these 
packages installed).

### Conda

Similar steps are used to execute projects in a conda environment. 
In this case, the config should point to a conda environment YAML file.

```
# create an env.yml file from the current conda environment
conda env export > env.yml
# specify that this file is the conda environment file
sk config --conda env.yml
# run
sk run -v -s --use-conda
```

### Incorporating with Other Pipelines

Additional workflows written in [snakemake](http://snakemake.readthedocs.io/en/stable/) should play nicely with the scikick workflow. By default, a `Snakefile` at the project root will be included in the `sk run` execution (Using the snakemake `include:` directive).

These jobs can be added to the beginning, middle, or end of scikick related tasks:

- Beginning 
  - `sk add first_step.rmd -d pipeline_donefile` (where pipeline_donefile is the last file generated by the Snakefile)
- Middle
  - Add `report/out_md/first_step.md` as the input to the first job of the Snakefile.
  - `sk add second_step.rmd -d pipeline_donefile`
- End 
  - Add `report/out_md/last_step.md` as the input to the first job of the Snakefile.
