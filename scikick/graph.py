from graphviz import Digraph
import graphviz
import os
from scikick.workflow.site_rules.render_site_yamlgen import clean_name

# Note this has potential to be used to link to 
# pages of the website.
# dot -Tcmapx dag.dot -o dag.cmapx
# dot -Tsvg dag.dot -o dag.svg
# cat template2.html dag.cmapx > index2.html
#https://stackoverflow.com/questions/15837283/graphviz-embedded-url
def make_dag(skconfig,engine="dot",path_from_root="",subject=""):
    """ Make a graphviz DAG from the workflow """
    skdot = Digraph('skmap',engine=engine)
    skdot.attr(nodesep="0.1")
    skdot.attr(ranksep="0.3")
    skdot.attr(weight="10")
    skdot.attr(rankdir="LR")

    # Get all files/nodes
    allfiles = []
    for exe in skconfig.exes:
        allfiles += [exe]
        deps = skconfig.analysis[exe]
        if deps is not None:
            for dep in deps:
                if dep not in allfiles:
                    allfiles += [dep]

    # Define all subgraphs
    cgraphs = {}
    for file in allfiles:
        dname = os.path.dirname(file) + '/'
        if dname not in cgraphs.keys():
            cgraphs[dname] = Digraph(name="cluster_" + dname)
            # Styling of cluster/directory group
            cgraphs[dname].attr(label=dname, style='rounded', bgcolor='lightgrey',
                                fontsize='10', fontname="arial", fontcolor="black")

    # Define all nodes within appropriate subgraph
    for file in allfiles:
        dname = os.path.dirname(file) + '/'
        if file in skconfig.exes:
            out_base = skconfig.get_info(file,"out_base")
            # Adjust links to start from out_md/
            # i.e. path_from_root is the path from subject to out_md
            link_path = os.path.join(path_from_root,out_base)
            # Highlight current node
            node_color= '#ff967b' if out_base == subject else 'white'
            # Define the exe node
            cgraphs[dname].node(file, label =
                    clean_name(os.path.basename(out_base)),
                URL=f'{link_path}.html',fontsize='10',margin='0.05,0.05',
                href=f'{link_path}.html',width='0.1',height='0.1',
                shape="box",style="filled",fillcolor=node_color,fontname="arial")
        else:
            # Define non-exe node
            cgraphs[dname].node(file, label = os.path.basename(file),
                fontsize='10',width='0.1',height='0.1',
                shape="note",fillcolor="lightgrey",fontname="arial",
                style="filled",dir="none")
    
    # Define all edges from dependencies to exe
    for exe in skconfig.exes:
        dname = os.path.dirname(exe) + '/'
        if skconfig.analysis[exe] is None:
            continue
        deps = skconfig.analysis[exe]
        for dep in deps:
            dep_dname = os.path.dirname(dep) + '/'
            if dep in skconfig.exes:
                dir = "forward"
            else:
                dir = "none"
            # within same subgraph?
            if dep_dname == dname:
                cgraphs[dname].edge(dep, exe,dir=dir)
            else:
                skdot.edge(dep,exe,dir=dir)

    # Add subgraphs to main graph
    for key in cgraphs.keys():
        skdot.subgraph(cgraphs[key])

    return skdot

# As graph
#import networkx as nx
#G = nx.Graph(sk)
#G
