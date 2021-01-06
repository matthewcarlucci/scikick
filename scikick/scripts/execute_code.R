#!/usr/bin/env Rscript
# Called from scikick's Snakefile
# Executes R or Rmd code
# All stderr is output during snakemake execution

# Rmd=>md
skknit <- function(input, output,
                   template_dir = "",  
                   data_parent = "output" # currently for knitr cache only
                   ){
    out_base = gsub("\\.Rmd$", "", basename(input),ignore.case=TRUE)
    outdatadir = paste0(file.path(data_parent, out_base), "/")

    script_dir = file.path(template_dir,"../scripts/")
    # Helper functions in template code
    source(file.path(script_dir, "knit_helpers.R"))

    # Set scikick's default knitr methods
    # Can be overrode by the user
    knitr::opts_chunk$set(list(
        #################
        # Visuals
        #################
        dpi = 100,
        fig.width = 10,
        fig.height = 10,
        fig.retina = 2,
        fig.pos = "center",
        #################
        # Code reporting
        #################
        echo = TRUE, # Need true to work with render step HTMLlook$code_folding
        error = FALSE,
        comment = NULL,
        message = FALSE, # Messages sent to stderr
        results = TRUE,
        warning = FALSE, # Warnings sent to stderr
        ################
        # Execution behaviour
        ###############
        # prevent interactive plots from being turned into PNGs
        screenshot.force = FALSE,
        #fig.path = outdatadir,
        cache.path = paste0(outdatadir, "/cache/")
    ))
    options(width=105) # wider display of prints than default

    # package options
    knitr::opts_knit$set(list(
        root.dir = "./",
        base.dir = dirname(output)
    ))

    rmd <- readLines(input)
    #is_homepage = input == index_rmd
    is_homepage = grepl("out_md/index",output)
    if(is_homepage){
        # import system index 
        sysindex <- readLines(file.path(template_dir, "index.Rmd"))
        # When no project index.Rmd exists, index_rmd/rmd will be the system
        # template and nothing else needs to be done 
        if(!identical(rmd, sysindex)){
            rmd <- c(rmd, sysindex)
        }
    } else {
        # Append footer (analysis metadata)
        footer <- readLines(file.path(template_dir, "footer.Rmd"))
        rmd <- c(rmd, footer)
    }

    # used for reporting runtime in the report (footer.Rmd)
    .scikick = new.env()
    .scikick$starttime = Sys.time()

    # execute the Rmd
    # needs to be knitr::knit since render does not accept textConnection
    knitr::knit(textConnection(rmd), output, quiet=TRUE)
    
    ### Knit meta handling for JS libraries
    # save the knitmeta for render step to import
    knitmeta_obj = knitr::knit_meta(clean = FALSE)
    knitmeta_file = sub(output, pattern = ".md$", replacement = ".knitmeta.RDS")
    # save knitmeta only if it's not empty
    if(length(knitmeta_obj) != 0){
        message = sprintf("Saving interactive plot JS libraries to %s",
            knitmeta_file)
        write(message, stderr())
        saveRDS(knitmeta_obj, file = knitmeta_file)
    }

    return(TRUE)
}

# Execute an R or Rmd as Rmd with knitr
main <- function(input, out_md, script_dir){
    file_is_rmd = length(grep(x=input, pattern=".rmd$", ignore.case=TRUE)) > 0
    file_is_r = length(grep(x=input, pattern=".r$", ignore.case=TRUE)) > 0
    if(file_is_rmd){
        rmd = input
    } else if(file_is_r){
        # Convert R to Rmd in tempdir
        tmp_dir = tempdir()
        file.copy(input, tmp_dir, overwrite = T) # overwrite for interactive use
        tmp_r = file.path(tmp_dir, basename(input))
        rmd_out = sub(x=tmp_r, pattern=".R$", replacement=".Rmd", ignore.case=TRUE)
        knitr::spin(tmp_r, format = "Rmd", knit = FALSE)
        rmd = rmd_out
    } else {
        stop("Unexpected file type")
    }
   
    # Execution 
    template_dir = file.path(script_dir,"../template")
    skknit(rmd, out_md, template_dir)
} 

# Allows for debugging by loading functions
if(!interactive()){
    # Relevant: https://stackoverflow.com/questions/1815606/determine-path-of-the-executing-script
    # Getting the path to this script for access to other system files
    full_args <- commandArgs(trailingOnly = FALSE)
    script_name <- sub("--file=", "", full_args[grep("--file=", full_args)])
    script_dir <- dirname(script_name)
    
    args = commandArgs(trailingOnly = TRUE)
    main(input = args[1],
        out_md = args[2],
        script_dir = script_dir)
}


