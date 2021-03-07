##### Project Execution Overview 
# This script contains:
#   - Commands to handle data imports
#   - Various commands to execute scikick
#      - Using singularity + SLURM (default)
#      - Using singularity
# NOTE: This script is not yet ready for direct execution

#### Data Import
# For every project it is necessary to determine how
# to get the data. For this project data comes from
# R packages with built in caching mechanisms
### Copying Bioc data cache into container
# Currently it is necessary to reroute a directory
# to /home/cache since the docker container did not
# give read/write permissions and singularity does
# not have elevated permissions.
# Using the system cache dir to avoid re-downloads
ehub=$(Rscript -e "cat(Sys.getenv('EXPERIMENT_HUB_CACHE'))")
ahub=$(Rscript -e "cat(Sys.getenv('ANNOTATION_HUB_CACHE'))")
# TODO if these variables don't exist in .Renviron an empty directory should be
# provided. This will allow for running on a generic machine
# that is not configured for ExperimentHub or AnnotationHub cache.
# It will still allow for project-instance-level caching.
# Additionally this will check for reproducibility on a naive machine
# and could catch errors from data updates.

# Works with scikick>0.1.2
# sk run -vs --use-singularity \
#	--singularity-args "'-B $ehub:/home/cache/ExperimentHub -B $ahub:/home/cache/AnnotationHub'"

# Run ipynb steps first since singularity is missing these dependencies
# Not longer used
# sk run workflow.ipynb

# Run all with singularity and cluster
sk run -vs --use-singularity -j 10 \
	--singularity-args "'-B $ehub:/home/cache/ExperimentHub -B $ahub:/home/cache/AnnotationHub'" \
	--profile slurm

# Works but has hardcoded sk path
#sk run -s --use-singularity --singularity-args "'-B /external/EPIGENETICS/SCRATCH/mcarlucci/cache:/home/cache -B /external/EPIGENETICS/SCRATCH/ARCHIVE/SOFTWARE/miniconda3/envs/scikick_dev/lib/python3.7/site-packages/scikick-0.1.2.dev0-py3.7.egg/scikick'"

# Run with cluster
# sk run -vs --profile slurm 
