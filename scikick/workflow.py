from graphviz import Digraph
import graphviz
import os
from scikick.scripts.render_site_yamlgen import clean_name

# Note this has potential to be used to link to 
# pages of the website.
# dot -Tcmapx dag.dot -o dag.cmapx
# dot -Tsvg dag.dot -o dag.svg
# cat template2.html dag.cmapx > index2.html
#https://stackoverflow.com/questions/15837283/graphviz-embedded-url
def make_dag(skconfig,engine="dot",path_from_root="",subject=""):
    """ Make a graphviz DAG from the workflow """
    skdot = Digraph('skmap',engine=engine)
    cgraphs = {}
    for exe in skconfig.exes:
        node = skconfig.get_info(exe,"out_base")
        dname = os.path.dirname(exe) + '/'
        # Adjust links to start from out_md/
        # i.e. path_from_root is path from sk.dot to out_md
        link_path = os.path.join(path_from_root,node) 
        # Define subgraph
        if dname not in cgraphs.keys():
            cgraphs[dname] = Digraph(name="cluster_" + dname)
            cgraphs[dname].attr(style='rounded',
                    bgcolor='lightgrey',fontsize='10',
                                label=dname,fontname="arial",fontcolor="black")
        # Highlight current node
        fcolor= '#ff967b' if node == subject else 'white'
        cgraphs[dname].node(node, label = clean_name(os.path.basename(node)),
                URL=f'{link_path}.html',fontsize='10',margin='0.05,0.05',
                href=f'{link_path}.html',width='0.1',height='0.1',
                   shape="box",style="filled",fillcolor=fcolor,fontname="arial")
        if skconfig.analysis[exe] is not None:
            for edge_dep in skconfig.analysis[exe]:
                if edge_dep in skconfig.exes:
                    edge = skconfig.get_info(edge_dep,"out_base")
                    cgraphs[dname].edge(edge,node)
                else:
                    edge = edge_dep
                    cgraphs[dname].node(edge, label =
                            os.path.basename(edge),fontsize='10',width='0.1',height='0.1',

                   shape="note",fillcolor="lightgrey",fontname="arial",style="filled",dir="none")
                    cgraphs[dname].edge(edge,node,dir="none")
    for key in cgraphs.keys():
        skdot.subgraph(cgraphs[key])
    skdot.attr(rankdir="LR")
    skdot.attr(nodesep="0.1")
    skdot.attr(ranksep="0.3")
    skdot.attr(weight="10")
    return skdot

# As graph
#import networkx as nx
#G = nx.Graph(sk)
#G
