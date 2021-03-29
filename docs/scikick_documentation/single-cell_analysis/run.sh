##### Project Execution Overview 
# This script contains:
#   - Commands to handle scRNAseq (project-specific) data imports
#   - Various commands to execute Scikick
#      - Using singularity + SLURM (default)
#      - Using singularity
#### Data Import
# For every project it is necessary to determine how
# to get the data. For this project, data comes from
# R packages with built-in caching mechanisms
### Copying Bioconductor data cache into container
# Currently it is necessary to reroute a directory
# to /home/cache since the docker container does not
# have read/write permissions and singularity does
# not have elevated permissions. Directories are passed to 
# singularity with the -B/--bind argument.
## Best is to use the system cache dir to avoid re-downloads
# ehub=$(Rscript -e "cat(Sys.getenv('EXPERIMENT_HUB_CACHE'))")
# ahub=$(Rscript -e "cat(Sys.getenv('ANNOTATION_HUB_CACHE'))")
## For ease, creating dedicated directories for data downloads
mkdir -p input/cache/ExperimentHub
mkdir -p input/cache/AnnotationHub

### Analysis Execution Commands
## Run all with Singularity and on a SLURM cluster
# Note that the singularity pull can require tmp space which can be set prior to the run with:
#   TMPDIR = /tmpdir/with/space
# The snakemake profile "slurm" must be confiugured prior to executing this command
sk run -v -s --use-singularity \
	--singularity-args "'-B input/cache/ExperimentHub:/home/cache/ExperimentHub -B input/cache/AnnotationHub:/home/cache/AnnotationHub'" \
	--profile slurm

## Singularity usage
# sk run -v -s --use-singularity \
#	--singularity-args "'-B input/cache/ExperimentHub:/home/cache/ExperimentHub -B input/cache/AnnotationHub:/home/cache/AnnotationHub'"
