# -*- coding: utf-8 -*-
"""
Various tools for the FSM

Created on 18/11/2011

@author: laur
"""
from itertools import chain

from django_fsm.db.fields.fsmfield import all_states

def write_png_graph(fname):
    """
    Make a graph of all available FSMs and save it in a PNG file

    @param fname: The file name of the image (.png)
    """
    try:
        import pydot
    except:
        return

    graph = pydot.Dot(graph_type='digraph')

    # get all states
    src, dst = zip(*all_states)
    states = filter(lambda s: s and s != '*', list(set(chain(src, dst))))

    # create all nodes
    nodes = {}
    for state in states:
        nodes[state] = pydot.Node(state, shape="rect")
        graph.add_node(nodes[state])

    # create all edges
    edges = []
    for src, dst in all_states:
        if src == '*':
            sources = states
        else:
            sources = [src]
        for src in sources:
            edge = (nodes[src], nodes[dst])
            if edge not in edges:
                edges.append(edge)
                graph.add_edge(pydot.Edge(edge))

    graph.write_png(fname)
