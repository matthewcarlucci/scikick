from graphviz import Digraph

# Note this has potential to be used to link to 
# pages of the website.
# dot -Tcmapx dag.dot -o dag.cmapx
# dot -Tsvg dag.dot -o dag.svg
# cat template2.html dag.cmapx > index2.html
#https://stackoverflow.com/questions/15837283/graphviz-embedded-url
def make_dag(skconfig):
    """ Make a graphviz DAG from the workflow """
    skdot = Digraph('G')
    for exe in skconfig.analysis.keys():
        node = skconfig.get_info(exe,"out_base")
        skdot.node(node, node, URL=f'{node}.html')
        # TODO - color by external/internal dep (executed or imported)
        if skconfig.analysis[exe] is not None:
            for edge_exe in skconfig.analysis[exe]:
                edge = skconfig.get_info(edge_exe,"out_base") 
                skdot.edge(edge,node)
    return skdot
