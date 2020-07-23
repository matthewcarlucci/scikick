# loading snakefile variables
suppressWarnings({
args = commandArgs(trailingOnly=TRUE)
input = args[1]
knitr::spin(input, format = "Rmd", knit = FALSE)
})
