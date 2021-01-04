"""functions for 'sk mv' subcommand"""
import os
import time
import shutil
from re import sub, IGNORECASE
from scikick.utils import reterr, warn
from scikick.layout import rm_commdir
from scikick.yaml import yaml_in, rename, supported_extensions

def sk_move_walk(src):
    """Walks through the directory that is contained inside src
    returns a list of files in the directory
    and other directories inside it (recursively)
    src -- list containing a directory name
    """
    while len(list(filter(lambda x: os.path.isdir(x), src))) > 0:
        files = list(filter(lambda x: os.path.isfile(x), src))
        dirs = list(filter(lambda x: os.path.isdir(x), src))
        new_dirs = list()
        for d in dirs:
            walk_res = os.walk(d)
            for w in walk_res:
                for wd in w[1]:
                    files.append(os.path.join(w[0], wd))
                for wf in w[2]:
                    new_dirs.append(os.path.join(w[0], wf))
        files = list(set(files))
        dirs = list(set(new_dirs))
        src = files + dirs
    return src

def sk_move_check(src, dest):
    """Perform checks on src and dest
    and quit if bad arguments are given
    src -- list of files to move
    des -- list containing the file/dir to move to
    """
    config = yaml_in()
    for s in src:
        if not os.path.exists(s):
            reterr(f"sk: Error: file or directory {s} doesn't exist")
    if len(src) > 1:
        if not os.path.isdir(dest[0]):
            reterr("sk: Error: moving multiple files to a single one")
    elif len(src) == 1 and (not os.path.isdir(dest[0])):
        old_ext = os.path.splitext(src[0])[1]
        new_ext = os.path.splitext(dest[0])[1]
        if old_ext.lower() != new_ext.lower():
            warn("sk: Warning: changing file extension")
        if (src[0] in config["analysis"].keys()) and \
            (new_ext.lower() not in map(str.lower, supported_extensions)):
            reterr(f"sk: Error: only extensions {', '.join(supported_extensions)} are supported ({new_ext} given)")

def sk_move_prepare_src_dest(src, dest):
    """Returns two lists of corresponding
    files in src and dest
    src -- list of files to move
    des -- list containing the file/dir to move to
    """
    if len(src) == 1:
        # if src holds a single file - handle the same as if multiple
        if os.path.isdir(src[0]):
            new_src = sk_move_walk(src)
            if not os.path.exists(dest[0]):
                new_dest = list(map(lambda f: \
                    os.path.join(dest[0], rm_commdir(f, src[0])), \
                    new_src))
            else:
                new_dest = list(map(lambda f: \
                    os.path.join(dest[0], os.path.basename(src[0]),
                        rm_commdir(f, src[0])), \
                    new_src))
            return (new_src, new_dest)
        if os.path.isfile(src[0]) and \
            (not os.path.isdir(dest[0])):
            return (src, dest)
    # if dest[0] doesn't exist, or is a file
    # shutil.move will take care of that
    # so dest[0] is an existing directory
    new_src = list()
    new_dest = list()
    for s in src:
        if os.path.isfile(s):
            new_src.append(s)
            new_dest.append(os.path.join(dest[0], os.path.basename(s)))
        if os.path.isdir(s):
            dir_src = sk_move_walk([s])
            new_src += dir_src
            new_dest += list(map(lambda f: \
                os.path.join(dest[0], os.path.basename(s), \
                    rm_commdir(f, s)), dir_src))
    return (new_src, new_dest)

def sk_move_extras(mv_dict):
    """Performs move operations specific to scikick
    Moves md files, figures in output/ directories
    and renames files in scikick.yml
    mv_dict -- dict with keys as src and values as dest files
    """
    # Moving mds, knitmetas and output figures in out_md/; 
    ## No need to change _site.ymls, since
    ## they are recreated after each change in scikick.yml
    yaml_dict = yaml_in()
    analysis = yaml_dict["analysis"]
    reportdir = yaml_dict["reportdir"]
    for src, dest in mv_dict.items():
        # if not in analysis.keys -> regular file
        # in this case, rename and continue
        if src not in analysis.keys():
            if 1 == rename(src, dest):
                warn("sk: %s renamed to %s in ./scikick.yml" % (src, dest))
            else:
                warn("sk: Warning: %s not found in ./scikick.yml" % src)
            continue
        md_rootdir = os.path.join(reportdir, "out_md")
        md_destdir = os.path.join(md_rootdir, os.path.dirname(dest))
        md_srcdir = os.path.join(md_rootdir, os.path.dirname(src))
        if not os.path.isdir(md_destdir):
            os.makedirs(md_destdir)
        # Move .md
        md_src = os.path.join(md_rootdir, os.path.splitext(src)[0] + ".md")
        md_dest = os.path.join(md_destdir, os.path.splitext(os.path.basename(dest))[0] + ".md")
        if os.path.isfile(md_src):
            shutil.move(md_src, md_dest)
        # Move knitmeta
        k_src = sub(pattern="\.md$", repl=".knitmeta.RDS",
                    string=md_src)
        k_dest = sub(pattern="\.md$", repl=".knitmeta.RDS",
                     string=md_dest)
        if os.path.isfile(k_src):
            shutil.move(k_src, k_dest)
        # Move markdown outputs (figures)
        tabname_src = sub(string=os.path.basename(md_src),
            pattern="\.md$", repl="")
        tabname_dest = sub(string=os.path.basename(md_dest),
            pattern="\.md$", repl="")
        md_srcfigdir = os.path.join(md_srcdir, "output", tabname_src)
        md_destfigdir = os.path.join(md_destdir, "output", tabname_dest)
        if os.path.isdir(md_srcfigdir):
            dest_dirname = os.path.dirname(md_srcfigdir)
            if not os.path.isdir(dest_dirname):
                os.makedirs(dest_dirname, exist_oke=True)
            print(f"sk: mv {md_srcfigdir} {md_destfigdir}")
            shutil.move(md_srcfigdir, md_destfigdir)
            # rename the output/ directory name in the dest md
            ## get the initial timestamp
            initial_timestamp = os.path.getmtime(md_dest)
            md_file = open(md_dest, 'r+')
            md_lines = [sub(string=line,
                pattern=f'src="output/{tabname_src}',
                repl=f'src="output/{tabname_dest}')
                for line in md_file]
            md_file.seek(0)
            for l in md_lines:
                md_file.write(l)
            md_file.close()
            # set the initial timestamp back to avoid reexecution
            os.utime(md_dest, (initial_timestamp, initial_timestamp))
        # rename all entries in scikick.yml from from to f_dest
        if 1 == rename(src, dest):
            warn("sk: %s renamed to %s in ./scikick.yml" % (src, dest))
        else:
            warn("sk: Warning: %s not found in ./scikick.yml" % src)
