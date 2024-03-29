

# Scikick - Notebook-Centric Analysis Workflows <img src="docs/scikick_documentation/icon.svg" align="right" width="120" />

[](https://pypi.python.org/pypi/scikick/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/scikick.svg)](https://pypi.python.org/pypi/scikick/)
![](https://img.shields.io/badge/lifecycle-maturing-blue.svg)
[![Snakemake](https://img.shields.io/badge/snakemake-≥5.9.0-brightgreen.svg?style=flat)](https://snakemake.readthedocs.io)
[![](https://img.shields.io/badge/doi-10.1371/journal.pone.0289171/btz834-green.svg)](https://doi.org/10.1371/journal.pone.0289171)

## Overview

Collections of computational notebooks often lose coherence as projects grow. Scikick is a command line utility for managing this growth with simple commands for workflow configuration, report generation, and state management.

![](docs/scikick_documentation/figure1.svg)

*Figure 1b from [Carlucci M. et al, 2023](https://doi.org/10.1371/journal.pone.0289171).*

-----------------------------------------------------

## Quick-Start

Scikick is currently tested on Unix systems (i.e. macOS, Linux etc.) and can be installed with:

```
pip install scikick
```

Initializing a Scikick project with `sk init` will create a `scikick.yml` file and identify any further missing software requirements. 

## Demonstrations and Documentation

[Read the introduction](https://petronislab.camh.ca/pub/scikick/stable/docs/report/out_html/introduction.html) for further details and installation requirements.

See the [tutorial](https://petronislab.camh.ca/pub/scikick/stable/docs/report/out_html/hello_world.html) for a simple example usage of Scikick.

[View a data analysis report generated by Scikick.](https://petronislab.camh.ca/pub/scikick/stable/docs/single-cell_analysis/report/out_html/index.html)

Use the [issue board](https://github.com/matthewcarlucci/scikick/issues) to provide feedback on Scikick (feature requests, bugs, and further software-related comments).

## Citation

See further discussion about Scikick in the accompanying article:

>Carlucci M, Bareikis T, Koncevičius K, Gibas P, Kriščiūnas A, Petronis A, et al. (2023) Scikick: A sidekick for workflow clarity and reproducibility during extensive data analysis. PLoS ONE 18(7): e0289171. https://doi.org/10.1371/journal.pone.0289171
