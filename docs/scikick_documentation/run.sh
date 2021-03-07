### Ensure documentation is up-to-date and ready for git commit

# Keep temp files for sk run -s -t usage
sk run -s --notemp -F

# Clear notebook source file outputs for git commit
echo "Clearing nb outputs"
for nb in $(ls *ipynb); do
    jupyter nbconvert --clear-output --inplace $nb
done

# Run a "touch" execution to treat as up-to-date since
# clearing notebook outputs updates timestamp 
# Removes temp files during execution
sk run -s -t
