## Developer Notes

All interative CLI documentation can be executed from this directory.

Documentation is self cleaning so should be executable simply with:

```
sk run -s -F
```

Execution can take approximately 10 minutes.

### Dependencies for executing this documentation


Install `env.yml` dependnecies and then:

```
python -m bash_kernel.install
```

To install the bash kernel.

scRNAseq analysis dependencies must also be installed.

Stored notebook source files are not intended for inspection (outputs are cleared for git commits).

Note that on Linux it seems that conda environments are not active in jupyter notebook bash kernels and scikick installations may not be found.
 
### Commiting changes

When executing prior to committing code, use run.sh to clear nb outputs.

Ensure all ipynb are empty prior to committing source files.

In the future git hooks or other measures may help to streamline this.

### Notebook-Repository Pairings

Some notebooks utilize source files in subdirectories:

`hello_world.ipynb`-`HW` - Contains notebooks and images for this tutorial

`SCRNA_walkthrough.ipynb`-`single-cell_analysis` - Contains many files for this tutorial

