# type: ignore
from graphviz import Digraph
from node.base_node import BaseNode
from typing import Set


def draw_graph(root: BaseNode):
    dot = Digraph()
    visited: Set['BaseNode'] = set()

    def add_edges(node: BaseNode):
        if node not in visited:
            dot.node(node.name)
            for dependency in node.dependencies:
                dot.edge(node.name, dependency.name)
                add_edges(dependency)
            visited.add(node)
    add_edges(root)
    dot.render('dag.gv', view=True)


    