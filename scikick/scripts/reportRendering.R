#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

input = args[1]
out_md = args[2]
template_dir = args[3]
data_parent = args[4]
script_dir = args[5]
logfile = args[6]
index_rmd = args[7]

simplified_input = input
if(dirname(input) == template_dir){
    simplified_input = paste("system's template", basename(input))
}

message = sprintf("sk: Executing R chunks in %s, outputting to %s",
    simplified_input, out_md)
write(message, stderr())

run_system = function(cmd){
    tmpf = tempfile()
    retcode = system(paste(cmd, "2>", tmpf), intern=FALSE,
        ignore.stdout=TRUE, ignore.stderr=FALSE)
    for(line in readLines(tmpf)){
        msg = paste("sk:  ", line)
        write(msg, file=stderr())
        write(msg, file=logfile, append=TRUE)
    }
    stopifnot(retcode == 0)
}

if(length(grep(x=input, pattern=".rmd$", ignore.case=TRUE)) > 0){
    run_system(paste("Rscript", file.path(script_dir, "knit.R"),
        input, out_md, template_dir, data_parent, index_rmd))
} else if(length(grep(x=input, pattern=".r$", ignore.case=TRUE)) > 0){
    tmp_dir = tempdir()
    tmp_r = file.path(tmp_dir, basename(input))
    rmd_out = sub(x=tmp_r, pattern=".R$", replacement=".Rmd", ignore.case=TRUE)
    # copy the R file to a tempdir
    file.copy(input, tmp_dir)
    # R => Rmd
    run_system(paste("Rscript", file.path(script_dir, "spin.R"), tmp_r))
    # Rmd => md
    run_system(paste("Rscript", file.path(script_dir, "knit.R"),
        rmd_out, out_md, template_dir, data_parent, index_rmd))
}
