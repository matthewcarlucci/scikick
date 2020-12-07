.scikick_get_gitlog = function(input=NULL){

    default_gitlog = data.frame(author="user", summary="no git history",
        date=Sys.Date(), sha="00000000", stringsAsFactors=FALSE)

    gitlog = tryCatch({
        suppressWarnings({git2r::commits(git2r::repository("."), path=input)})
    }, error=function(e){
        list()
    })
    ver_msg = paste0("Warning: Version of R package git2r ",
        "is earlier than 0.27, page will lack git logs")
    if(length(gitlog) > 0) {
        gitlog = tryCatch(
            expr={data.frame(author=sapply(gitlog, function(x) x$author$name),
                summary=sapply(gitlog, function(x) x$summary),
                date=sapply(gitlog, function(x) as.character(x$author$when)),
                sha=sapply(gitlog, function(x) strtrim(x$sha, 8)),
                stringsAsFactors=FALSE)},
            error=function(e) {
                if(packageVersion("git2r") < "0.27"){
                    write(ver_msg, stderr())
                }
                return(default_gitlog)
            })
    } else{
        gitlog = default_gitlog
    }
    return(gitlog)
}
