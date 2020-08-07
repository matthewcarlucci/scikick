# loading snakefile variables
args = commandArgs(trailingOnly=TRUE)
input = args[1]
output = args[2]
templatedir = args[3]
dataparent = args[4]
index_rmd = args[5]
original_input = args[6]
reportfile = input
reportname = gsub("\\.Rmd$", "", basename(input),ignore.case=TRUE)
outdatadir = paste0(file.path(dataparent, reportname), "/")
source(file.path(templatedir, "outputLook.R"))
source(file.path(templatedir, "functions.R"))
knitr::opts_chunk$set(optionsRender$knitr$opts_chunk)
rmd <- readLines(input)
if(input == index_rmd){
    index <- readLines(file.path(templatedir, "index.Rmd"))
    # when no index.Rmd exists - template is passed
    if(!identical(rmd, index)){
        # if that's the case - we don't include it
        rmd <- c(rmd, index)
    }
} else {
    footer <- readLines(file.path(templatedir, "footer.Rmd"))
    rmd <- c(rmd, footer)
}

knitr::opts_knit$set(root.dir = "./")
knitr::opts_knit$set(base.dir = dirname(output))
# to prevent interactive plots from being turned into PNGs
knitr::opts_chunk$set(screenshot.force = FALSE)
knitr::opts_chunk$set(fig.path = outdatadir)
knitr::opts_chunk$set(cache.path = paste0(outdatadir, "/cache/"))
# used for reporting calculation start time in the report
.scikick = new.env()
.scikick$starttime = Sys.time()
# execute the Rmd
knitr::knit(textConnection(rmd), output, quiet=TRUE)
# save the knitmeta
knitmeta_obj = knitr::knit_meta(clean = FALSE)
knitmeta_file = sub(output, pattern = ".md$", replacement = ".knitmeta.RDS")
# delete old knitmeta
if(file.exists(knitmeta_file)){
    file.remove(knitmeta_file)
}
# save knitmeta only if it's not empty
if(length(knitmeta_obj) != 0){
    message = sprintf("Saving interactive plot JS libraries to %s",
        knitmeta_file)
    write(message, stderr())
    saveRDS(knitmeta_obj, file = knitmeta_file)
}
