#!/usr/bin/env Rscript
# Use from commandline for Rmd to md execution
# Called from scikick's Snakefile using shell

main <- function(input,output,templatedir,dataparent,index_rmd,original_input){

    reportfile = input
    reportname = gsub("\\.Rmd$", "", basename(input),ignore.case=TRUE)
    outdatadir = paste0(file.path(dataparent, reportname), "/")

    script_dir = file.path(templatedir,"../scripts/")
    # Helper functions
    source(file.path(script_dir, "knit_helpers.R"))

    # Set scikick's default knitr methods
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
        message = FALSE,
        results = TRUE,
        warning = FALSE,
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

    if(input == index_rmd){
        index <- readLines(file.path(templatedir, "index.Rmd"))
        # when no index.Rmd exists - template is passed
        if(!identical(rmd, index)){
            # if that's the case - we don't include it
            rmd <- c(rmd, index)
        }
    } else {
        # Append footer (analysis metadata)
        footer <- readLines(file.path(templatedir, "footer.Rmd"))
        rmd <- c(rmd, footer)
    }

    # used for reporting calculation start time in the report
    .scikick = new.env()
    .scikick$starttime = Sys.time()

    # execute the Rmd
    # needs to be knitr::knit since render does not accept textConnection
    knitr::knit(textConnection(rmd), output, quiet=TRUE)

    ### Knit meta handling for JS libraries
    # save the knitmeta
    knitmeta_obj = knitr::knit_meta(clean = FALSE)
    knitmeta_file = sub(output, pattern = ".md$", replacement = ".knitmeta.RDS")
    #MC: I don't think this is necessary 
    ## delete old knitmeta
    #if(file.exists(knitmeta_file)){
    #    file.remove(knitmeta_file)
    #}
    # save knitmeta only if it's not empty
    if(length(knitmeta_obj) != 0){
        message = sprintf("Saving interactive plot JS libraries to %s",
            knitmeta_file)
        write(message, stderr())
        saveRDS(knitmeta_obj, file = knitmeta_file)
    }
}

# This file can be used as a script or an R source file
# Below is for script mode only
if(!interactive()){
    # Loading snakefile variables
    args = commandArgs(trailingOnly=TRUE)
    input = args[1]
    output = args[2]
    templatedir = args[3]
    dataparent = args[4]
    index_rmd = args[5]
    original_input = args[6]
    main(input,output,templatedir,dataparent,index_rmd,original_input)
}
