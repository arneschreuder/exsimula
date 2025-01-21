from __future__ import annotations
from typing import Dict, Optional
import uuid


class Node:
    id: str
    edges: Dict[str, Edge]

    def __init__(
        self, id: Optional[str] = uuid.uuid1(), edges: Optional[Dict[str, Edge]] = None
    ):
        self.id = id
        self.edges = edges or {}

    def __call__(self):
        print(f"Calling node id:{self.id}")

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge


class Edge:
    id: str
    source_node: Node
    target_node: Node

    def __init__(
        self,
        id: Optional[str] = uuid.uuid1(),
        source_node: Optional[Node] = None,
        target_node: Optional[Node] = None,
    ):
        self.id = id
        self.source_node = source_node
        self.target_node = target_node

    def __call__(self):
        print(f"Calling edge id:{self.id}")

    def set_source_node(self, source_node: Node):
        self.source_node = source_node

    def set_target_node(self, target_node: Node):
        self.target_node = target_node


class Graph:
    id: str
    nodes: Dict[str, Node]
    edges: Dict[str, str, Edge]
    source_node: Node
    target_node: Node

    def __init__(self, id: Optional[str] = uuid.uuid1()):
        self.id = id
        self.nodes = {}
        self.edges = {}

    def step(self, current_node: Node) -> Node:
        print(f"Stepping from node id:{current_node.id}")
        next_node = None
        current_node()
        edges = current_node.edges

        # Depth first implementation
        # For normal nodes, not for conditional nodes yet
        for edge in edges.values():
            print(f"Stepping from edge id:{edge.id}")
            edge()
            next_node = edge.target_node
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

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge

    def set_source_node(self, node: Node):
        self.source_node = node

    def set_target_node(self, node: Node):
        self.target_node = node

    def connect(self, source_node: Node, target_node: Node, edge: Edge):
        edge.source_node = source_node
        edge.target_node = target_node
        edge.set_source_node(source_node)
        edge.set_target_node(target_node)
        source_node.add_edge(edge)

    def compile(self):
        for edge in self.edges:
            source_node = edge.source_node
            target_node = edge.target_node
            source_node.add_edge(edge)
            edge.set_source_node(source_node)
            edge.set_target_node(target_node)
            target_node.add_edge(edge)
