from __future__ import annotations
from abc import ABC
from collections import OrderedDict
from typing import Dict, List, Optional
import uuid


class Node(ABC):
    id: str
    edges: List[Edge]

    def __init__(self, id: Optional[str] = None, edges: Optional[List[Edge]] = None):
        self.id = id or uuid.uuid1()
        self.edges = edges or []

    def __call__(self) -> Optional[Edge]:
        print(f"Calling node id:{self.id}")
        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        # Get all edges, where source node is this node
        if self.edges:
            # something like [edge for self.edges.values() if edge.source_node == self]
            target_edges = [edge for edge in self.edges if edge.source_node == self]
            if target_edges:
                return next(iter(self.edges))
        return None

    def add_edge(self, edge: Edge):
        assert edge not in self.edges, "edge is already in edges"
        self.edges.append(edge)


class Edge:
    id: str
    source_node: Node
    target_node: Node

    def __init__(
        self,
        id: Optional[str] = None,
        source_node: Optional[Node] = None,
        target_node: Optional[Node] = None,
    ):
        self.id = id or uuid.uuid1()
        self.source_node = source_node
        self.target_node = target_node

    def __call__(self) -> Node:
        print(f"Calling edge id:{self.id}")
        assert self.target_node is not None, "target_node is not set"
        return self.target_node

    def set_source_node(self, source_node: Node):
        self.source_node = source_node

    def set_target_node(self, target_node: Node):
        self.target_node = target_node


class Graph:
    id: str
    nodes: List[Node]
    edges: List[Edge]
    source_node: Node
    target_node: Node

    def __init__(self, id: Optional[str] = None):
        self.id = id or uuid.uuid1()
        self.nodes = []
        self.edges = []

    def step(self, current_node: Node) -> Node:
        if current_node == None:
            return self.target_node
        next_node = None
        next_edge = current_node()

        if next_edge:
            next_node = next_edge()
            return next_node

        return next_node

    def __call__(self):
        print(f"Calling graph id:{self.id}")
        assert self.source_node is not None, "source_node is not set"
        assert self.target_node is not None, "target_node is not set"

        current_node = self.source_node

        while current_node != self.target_node:
            next_node = self.step(current_node)
            current_node = next_node

        # Finalise by executing target node
        current_node()

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def set_source_node(self, node: Node):
        self.source_node = node

    def set_target_node(self, node: Node):
        self.target_node = node

    def connect(self, source_node: Node, target_node: Node, edge: Edge):
        assert source_node in self.nodes, "source_node is not in nodes"
        assert target_node in self.nodes, "target_node is not in nodes"
        assert source_node != target_node, "source_node is the same as target_node"
        edge.set_source_node(source_node)
        edge.set_target_node(target_node)
        source_node.add_edge(edge)

    # def compile(self):
    #     for edge in self.edges:
    #         source_node = edge.source_node
    #         target_node = edge.target_node
    #         source_node.add_edge(edge)
    #         edge.set_source_node(source_node)
    #         edge.set_target_node(target_node)
    #         target_node.add_edge(edge)
