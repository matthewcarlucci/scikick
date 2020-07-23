optionsRender <- list()
optionsRender$rmarkdown <- rmarkdown::html_document(
    code_folding = "hide",
    highlight = "zenburn",
    theme = "journal",
    template = "default",
    toc = TRUE,
    css = "template/custom.css",
    toc_depth = 5,
    self_contained = TRUE
)
optionsRender$knitr <- list(opts_chunk = list(
    #################
    # Visuals
    #################
    dpi = 100,
    fig.width = 10,
    fig.height = 10,
    fig.retina = 2,
    fig.pos = "center",
    #################
    # Code
    #################
    echo = TRUE, # Need true to work with HTMLlook$code_folding
    error = FALSE,
    comment = NULL,
    message = FALSE,
    results = TRUE,
    warning = FALSE
))
options(width=105)
