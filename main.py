from typing import Dict, Optional
import uuid
from exsimula.graph import Edge, Graph, Node


class ConditionalNode(Node):
    output_mapping: Dict[str, str]

    def __init__(
        self,
        id: Optional[str] = None,
        output_mapping: Optional[Dict[str, str]] = None,
    ):
        super().__init__(id)
        self.output_mapping = output_mapping

    def __call__(self) -> Optional[Edge]:
        print(f"Calling conditional node id:{self.id}")
        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        result = "goto"
        if result in self.output_mapping:
            edge_id = self.output_mapping[result]
            for edge in self.edges:
                if edge.id == edge_id:
                    return edge
        return None


class LoopNode(Node):
    range: int

    def __init__(
        self,
        id: Optional[str] = None,
        range: Optional[int] = None,
    ):
        super().__init__(id)
        self.range = range or 1

    def __call__(self) -> Optional[Edge]:
        for i in range(self.range):
            # Can only loop contents of the node, so this type of node
            # does not quite make sense entirely
            print(f"Calling loop node id:{self.id} - loop {i+1}/{self.range}")

        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        # Get all edges, where source node is this node
        if self.edges:
            # something like [edge for self.edges.values() if edge.source_node == self]
            target_edges = [edge for edge in self.edges if edge.source_node == self]
            if target_edges:
                return next(iter(self.edges))
        return None


source = Node("source")
n1 = Node("n1")
n2 = ConditionalNode("n2", {"goto": "e3"})
n3 = LoopNode("n3", 10)
n4 = Node("n4")
target = Node("target")

e1 = Edge("e1")
e2 = Edge("e2")
e3 = Edge("e3")
e4 = Edge("e4")
e5 = Edge("e5")
e6 = Edge("e6")

graph = Graph()

graph.add_node(source)
graph.add_node(n1)
graph.add_node(n2)
graph.add_node(n3)
graph.add_node(n4)
graph.add_node(target)

graph.add_edge(e1)
graph.add_edge(e2)
graph.add_edge(e3)
graph.add_edge(e4)
graph.add_edge(e5)
graph.add_edge(e6)

graph

graph.connect(source, n1, e1)
graph.connect(n1, n2, e2)
graph.connect(n2, n3, e3)
graph.connect(n2, n4, e4)
graph.connect(n3, target, e5)
graph.connect(n4, target, e6)

graph.set_source_node(source)
graph.set_target_node(target)

graph()
