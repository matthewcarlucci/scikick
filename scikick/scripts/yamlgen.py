"""Generates yaml files in out_md/"""
import re
from os import getcwd
from os.path import basename, dirname, join, relpath, sep
from ruamel.yaml import YAML
from scikick.config import get_tabs
from scikick.yaml import yaml_in
from scikick.utils import git_repo_url

sk_yaml = snakemake.input[0]
site_yaml = snakemake.output[0]
main_yaml = snakemake.output['main_yml']
inymls = snakemake.output['inner_ymls']

yaml = YAML(typ="rt")
config = yaml_in()

# get tab strucutre
tabs = get_tabs(config)

nav_left = list() # all tabs on the left side
nav_more = list() # more tab
# populating nav_left no need to add the old
# 'Other' part, since it's not relevant anymore
# with the automatic 'report:' generation

nav_left = [{"text": text, "href": "%s.html" % tabs[text][0]} \
    if basename(tabs[text][0]) == text else \
    {"text": text, "menu": \
    [{"text": basename(hr), "href": "%s.html" % hr} for hr in tabs[text]] \
    } for text in tabs.keys()]

# get git repo url

nav_more = {"text": "More", \
    "menu": [{"text" : "Git Repository", "href" : git_repo_url()}]}

output_yaml = {"output_dir": "../out_html", \
    "navbar": {"title": basename(getcwd()), \
        "left": nav_left, "right": [nav_more]}}

yaml.indent(sequence=4, mapping=4, offset=0)
yaml.dump(output_yaml, open(site_yaml, "w"))

# dealing with all the recursive _site.ymls
for inyml in inymls:
    indir = re.sub("(.*?)/out_md/(.*$)", "\\2", dirname(inyml))
    if dirname(inyml) == "%s%s%s" % ("report", sep, "out_md"):
        indir = "./"
    nav_left = [{"text": text, \
        "href": "%s.html" % join(relpath(dirname(tabs[text][0]), indir), \
            basename(tabs[text][0]))} \
        if basename(tabs[text][0]) == text else \
        {"text": text, "menu": \
            [{"text": basename(hr), "href": "%s.html" % \
                join(relpath(dirname(hr), indir), basename(hr)) \
            } for hr in tabs[text]] \
        } for text in tabs.keys()]
    output_yaml = {"output_dir": relpath("../out_html", indir), \
        "navbar": {"title": basename(getcwd()), \
            "left": nav_left, "right": [nav_more]}}
    yaml.indent(sequence=4, mapping=4, offset=0)
    yaml.dump(output_yaml, open(inyml, "w"))
