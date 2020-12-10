.scikick_get_gitlog = function(
    input=NULL # if provided a page, only show history for the page
    ){
    
    git2r_commits = tryCatch({
        suppressWarnings({git2r::commits(git2r::repository("."), path=input)})
    }, error=function(e){
        list()
    })
    log_exists = length(git2r_commits)>0
    if(log_exists) {
        gitlog = tryCatch(
            expr={
                df = data.frame(Author=sapply(git2r_commits, function(x) x$author$name),
                    Message=sapply(git2r_commits, function(x) x$summary),
                    Date=sapply(git2r_commits, function(x) as.character(x$author$when)),
                    SHA=sapply(git2r_commits, function(x) strtrim(x$sha, 8)),
                    stringsAsFactors=FALSE)

                # trim if summary line is too long to fit on screen
                df$Message = ifelse(nchar(df$Message) > 80, paste0(strtrim(df$Message, 80), "..."), df$Message)
                # Remove troublesome markdown characters
                df$Message = gsub("_", " ", df$Message)
                # Avoid all commit message character issues by surrounding with "`"
                df$Message = paste('`',df$Message,'`',sep="")
                df
            },
            error=function(e) {
                #write(e, stderr())
                if(packageVersion("git2r") < "0.27"){
                    ver_msg = paste0("Warning: git2r R package version",
                        "is <0.27, pages will lack git logs")
                    write(ver_msg, stderr())
                }
                return(NULL)
            })
    } else {
        gitlog = NULL
    }
    
    return(gitlog)
}
