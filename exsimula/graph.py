from __future__ import annotations
from abc import ABC
from typing import Callable, Dict, Optional, Tuple
import uuid


class Node(ABC):
    id: str
    edges: Dict[str, Edge]
    fn: Callable[[Dict], Dict]

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Optional[Callable[[Dict], Tuple[Dict, str]]] = None,
        edges: Optional[Dict[str, Edge]] = None,
    ):
        self.id = id or uuid.uuid1()
        self.fn = fn or (lambda x: (x, None))
        self.edges = edges or {}

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        # Get all edges, where source node is this node
        if self.fn:
            state, _ = self.fn(state)

        if self.edges and len(self.edges) > 0:
            return (state, next(iter(self.edges.values())))
        return (state, None)

    def add_edge(self, edge: Edge):
        assert edge not in self.edges.values(), "edge is already in edges"
        self.edges[edge.id] = edge


class ConditionalNode(Node):
    output_mapping: Dict[str, str]

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Optional[Callable[[Dict], Tuple[Dict, str]]] = None,
        output_mapping: Optional[Dict[str, str]] = None,
    ):
        super().__init__(id, fn)
        self.output_mapping = output_mapping or {}

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        if self.fn:
            state, route = self.fn(state)

        if route in self.output_mapping:
            edge_id = self.output_mapping[route]
            if edge_id in self.edges:
                return (state, self.edges[edge_id])
        return (state, None)


class LoopNode(Node):
    range: int

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Optional[Callable[[Dict], Tuple[Dict, str]]] = None,
        range: Optional[int] = None,
    ):
        super().__init__(id, fn)
        self.range = range or 1

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        for i in range(self.range):
            # Can only loop contents of the node, so this type of node
            # does not quite make sense entirely
            if self.fn:
                state, _ = self.fn(state)

        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        # Get all edges, where source node is this node
        if self.edges and len(self.edges) > 0:
            return (state, next(iter(self.edges.values())))
        return (state, None)


class Edge:
    id: str
    source_node: Optional[Node]
    target_node: Optional[Node]
    fn: Optional[Callable[[Dict], Tuple[Dict, str]]]

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Optional[Callable[[Dict], Tuple[Dict, str]]] = None,
        source_node: Optional[Node] = None,
        target_node: Optional[Node] = None,
    ):
        self.id = id or uuid.uuid1()
        self.fn = fn or (lambda x: (x, None))
        self.source_node = source_node
        self.target_node = target_node

    def __call__(self, state: Dict) -> Tuple[Dict, Node]:
        assert self.target_node is not None, "target_node is not set"
        if self.fn:
            state, _ = self.fn(state)
        return (state, self.target_node)

    def set_source_node(self, source_node: Node):
        self.source_node = source_node

    def set_target_node(self, target_node: Node):
        self.target_node = target_node


class GraphConfig:
    id: str
    nodes: Dict[str, Node]
    edges: Dict[str, Edge]
    branches: Dict[str, Dict[str, str]]
    source_node: str
    target_node: str

    def __init__(
        self,
        id: Optional[str] = None,
        nodes: Optional[Dict[str, Node]] = None,
        edges: Optional[Dict[str, str, Edge]] = None,
        branches: Optional[Dict[str, str]] = None,
    ):
        self.id = id or uuid.uuid1()
        self.nodes = nodes or {}
        self.edges = edges or {}
        self.branches = branches or {}

    def set_id(self, id: str):
        self.id = id

    def add_node(self, id: str, node: Node):
        assert id not in self.nodes, "node id already exists"
        self.nodes[id] = node

    def add_edge(self, id: str, edge: Edge):
        assert id not in self.edges, "edge id already exists"
        self.edges[id] = edge

    def add_branch(self, source_id: str, target_id: str, edge_id: str):
        assert source_id in self.nodes, "source_id is not in nodes"
        assert target_id in self.nodes, "target_id is not in nodes"
        assert edge_id in self.edges, "edge_id is not in edges"

        if source_id not in self.branches:
            self.branches[source_id] = {}
        if target_id in self.branches[source_id]:
            raise ValueError("target_id is already in branches")
        self.branches[source_id][target_id] = edge_id

    def set_source_node(self, id: str):
        assert id in self.nodes, "source_id is not in nodes"
        self.source_node = id

    def set_target_node(self, id: str):
        assert id in self.nodes, "target_id is not in nodes"
        self.target_node = id


class Graph:
    id: str
    nodes: Dict[str, Node]
    edges: Dict[str, Edge]
    source_node: Node
    target_node: Node

    def __init__(self, id: Optional[str] = None, config: Optional[GraphConfig] = None):
        self.id = id or uuid.uuid1()
        self.nodes = {}
        self.edges = {}

        if config:
            self.load_config(config)

    def load_config(self, config: GraphConfig):
        self.id = config.id

        for id, node in config.nodes.items():
            # Override id if none
            node.id = id
            self.add_node(node)

        for id, edge in config.edges.items():
            # Override id if none
            edge.id = id
            self.add_edge(edge)

        for source_id in config.branches:
            assert source_id in self.nodes, "source_id is not in nodes"
            for target_id, edge_id in config.branches[source_id].items():
                assert target_id in self.nodes, "target_id is not in nodes"
                assert edge_id in self.edges, "edge_id is not in edges"
                source_node = self.nodes[source_id]
                target_node = self.nodes[target_id]
                edge = self.edges[edge_id]
                self.connect(source_node, target_node, edge)

        source_node = self.nodes[config.source_node]
        target_node = self.nodes[config.target_node]

        self.set_source_node(source_node)
        self.set_target_node(target_node)

    def step(self, state: Dict, current_node: Node) -> Tuple[Dict, Optional[Node]]:
        if current_node == None:
            return self.target_node
        next_node = None
        state, next_edge = current_node(state)

        if next_edge:
            state, next_node = next_edge(state)
            return (state, next_node)

        return (state, next_node)

    def __call__(self, state: Dict) -> Dict:
        print(f"Calling graph id:{self.id}")
        assert self.source_node is not None, "source_node is not set"
        assert self.target_node is not None, "target_node is not set"

        current_node = self.source_node

        while current_node != self.target_node:
            state, next_node = self.step(state, current_node)
            current_node = next_node

        # Finalise by executing target node
        state, _ = current_node(state)
        return state

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge

    def set_source_node(self, node: Node):
        self.source_node = node

    def set_target_node(self, node: Node):
        self.target_node = node

    def connect(self, source_node: Node, target_node: Node, edge: Edge):
        assert source_node in self.nodes.values(), "source_node is not in nodes"
        assert target_node in self.nodes.values(), "target_node is not in nodes"
        assert source_node != target_node, "source_node is the same as target_node"
        assert edge in self.edges.values(), "edge is not in edges"
        edge.set_source_node(source_node)
        edge.set_target_node(target_node)
        source_node.add_edge(edge)
