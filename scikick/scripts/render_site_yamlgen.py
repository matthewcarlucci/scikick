"""Generate _site.yml files in out_md/"""
import re
from os import getcwd
from os.path import basename, dirname, join, relpath, sep
from ruamel.yaml import YAML
from scikick.config import ScikickConfig
from scikick.layout import get_tabs
from scikick.utils import git_repo_url, get_sk_template_file

#https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def clean_name(name):
    words = name.replace("_"," ").replace("-"," ").split(" ")
    capitalized_words = [word[0].upper() + word[1:] if len(word) != 0 else
            word for word in words]
    ret = ' '.join(capitalized_words)
    # TODO - camel case splitting
    return ret

def main():
    yaml = YAML(typ="rt")
    skconfig = ScikickConfig()

    # get tab strucutre
    tabs = get_tabs(skconfig.config)
    site_yaml_files = skconfig.get_site_yaml_files()

    # get git repo url
    nav_more = {"text": "More", \
        "menu": [{"text" : "Git Repository", "href" : git_repo_url()}]}

    # translating the desired layout (get_tabs) to _site.yml format
    for site_yaml_file in site_yaml_files:
        nav_left = list()
        # path from the site yaml to the output root
        path_to_root = relpath(join(skconfig.report_dir,'out_md'),start=dirname(site_yaml_file))
        for tab, items in tabs.items():
            human_text = clean_name(tab)
            # if first value is the key, this is a file
            tabisfile = basename(items[0]) == tab
            if tabisfile:
                path_from_site_to_html = join(path_to_root,items[0])
                this_item = {"text": human_text, "href": "%s.html" % path_from_site_to_html}
            else:
                this_item = {"text": human_text, "menu":[]} 
                for item in items:
                    path_from_site_to_html = join(path_to_root,item)
                    sub_item = {"text": clean_name(basename(item)), "href": "%s.html" % path_from_site_to_html}
                    this_item['menu'].append(sub_item)
            nav_left.append(this_item) 

        site_yaml= { "navbar": {"title": clean_name(basename(getcwd())), \
                "left": nav_left, "right": [nav_more]}}

        if 'output' in skconfig.config.keys():
            output_yaml = skconfig.config
        else:
            # TODO merge with scikick.yml
            output_yaml = yaml.load(open(get_sk_template_file("default_output.yml"),"r")) 
        site_yaml.update(output_yaml)

        yaml.indent(sequence=4, mapping=4, offset=0)
        yaml.dump(site_yaml, open(site_yaml_file, "w"))

if __name__ == "__main__":
    main()
