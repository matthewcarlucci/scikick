# sk layout
import os
from ruamel.yaml.compat import ordereddict
from scikick.yaml import yaml_in, yaml_dump, rm_commdir, get_indexes, supported_extensions
from scikick.utils import reterr

# to allow hierarchy #232 this and everything it dependends on will need changes
def get_tabs(skconf):
    """Return a list of tab names determined from scikick.yml
    skconf -- ScikickConfig object
    """
    if len(skconf.analysis) == 0:
        return {}

    # Start with analysis keys
    exes = skconf.exes
    # Remove index from menu building
    if len(skconf.index_exes) == 1:
         exes.remove(skconf.index_exes[0])
    # Find common directory
    nb_root = os.path.commonpath(list(exes))
    # Then build menus accoring to exes order
    tabs = ordereddict()
    for exe in exes:
        tabname = os.path.normpath(rm_commdir(os.path.dirname(exe),nb_root))
        # Add unique tabs for each exe at nb_root
        if tabname == ".":
            out_base = skconf.get_info(exe,"out_base")
            assert not os.path.isdir(out_base)
            tabname = os.path.basename(out_base)
        # Add menus for the rest
        if tabname not in tabs.keys():
            tabs[tabname] = []
        # Add exe to respective tabs
        tabs[tabname].append(os.path.splitext(exe)[0])
    return tabs

def new_tab_order(args_order, tab_keys):
    """Get the new order of tabs based on the user input.
    Expands the user provided order to the full explicit index order.
    Returns a list of indices, which would be used to reorder the
    'analysis' keys in scikick.yml
    args_order -- order provided by the user (list of indices as strings)
    tabs -- list of tab names
    """
    # in case 9 or less tabs, the the order can be without spaces
    if len(args_order) == 1:
        order = list(map(lambda x: int(x) - 1, str(args_order[0])))
    else:
        order = list(map(lambda x: x - 1, args_order))
    if len(set(order)) == len(order) and \
            len(order) <= len(tab_keys) and \
            min(order) >= 0 and max(order) < len(tab_keys):
        # fill the rest of idxs if not all provided
        for i in range(len(tab_keys)):
            if i not in order:
                order.append(i)
        return order
    else:
        reterr("sk: Error: Inputs must be a unique list of tab indices")

# Top level reordering (reorder by directory)
def rearrange_tabs(order, skconf, tabs):
    """Change the order of tabs in the navigation bar
    order -- the new order (list of indices 1...n) of the tabs
    config -- ScikickConfig object
    tabs -- get_tabs(config) output
    """
    # get the full set of indices
    order = new_tab_order(order, tabs.keys())
    # reorder analysis by with the order indices
    new_analysis = reordered_analysis(tabs, skconf, order)
    # Fix missing index (not included in get_tabs output)
    if not skconf.analysis == new_analysis:
        if len(skconf.index_exes)==1:
            new_analysis[skconf.index_exe] = skconf.analysis[skconf.index_exe]
    # Ensure it is fixed
    assert new_analysis == skconf.analysis
    skconf.config['analysis'] = new_analysis
    return skconf

def reordered_analysis(tabs, skconf, order):
    """Reorder the 'analysis' dict in scikick.yml according to the ordering of
    the directories output by get_tabs.
    Returns the reordered 'analysis' dict which produces
    the differently ordered tab list in all pages
    tabs -- list of tab names
    skconf -- ScikickConfig object
    order -- list of indices for tabs
    """
    new_analysis = ordereddict()
    for ord_no in order:
        # Add each exe dict entry to new dict
        for out_base in tabs[list(tabs.keys())[ord_no]]:
            norm_rmd = os.path.normpath(out_base)
            curr_key = list(filter(lambda x: \
                                       os.path.splitext(x)[0] == norm_rmd, \
                                   skconf.analysis.keys()))[0]
            new_analysis[curr_key] = skconf.analysis[curr_key]
    return new_analysis

# Submenu reordering (reorder within directory)
def rearrange_submenus(submenu, order, skconf, tabs):
    """Change the order of submenus under a tab
    submenu -- the name of the tab which to reorder
    order -- the new order (list of indices 1...n) of the submenu
    skconf -- ScikickConfig objects 
    tabs -- get_tabs(config) output
    """
    # Find out_bases in submenu
    submenu_out_bases = tabs[submenu]
    submenu_exes = list(map(lambda out_base: skconf.get_info(out_base,"exe"), submenu_out_bases))
    order = new_tab_order(order, submenu_out_bases)

    ### Build new analysis dict
    new_analysis = skconf.analysis.copy()
    new_analysis.clear()
    # Insert until first submenu is encountered
    for exe in skconf.exes:
        if exe not in submenu_exes:
            new_analysis[exe] = skconf.analysis[exe]
        else:
            break
    # Insert all submenu content in new order
    submenu_exes_neword = [submenu_exes[i] for i in order]
    for exe in submenu_exes_neword:
        new_analysis[exe] = skconf.analysis[exe]
    # Insert rest
    for exe in skconf.exes:
        if exe not in submenu_out_bases and exe not in new_analysis.keys():
            new_analysis[exe] = skconf.analysis[exe]
    skconf.config['analysis'] = new_analysis
    return skconf


