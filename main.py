import json
import pickle
from typing import Callable, Dict, Optional, Tuple
from exsimula.graph import Edge, Graph, GraphConfig, Node


def hello_world(state: Dict) -> Dict:
    print("Hello World")
    state["messages"] = state["messages"] + ["Hello World"]
    return state


class ConditionalNode(Node):
    output_mapping: Dict[str, str]

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Callable = None,
        output_mapping: Optional[Dict[str, str]] = None,
    ):
        super().__init__(id, fn)
        self.output_mapping = output_mapping

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        print(f"Calling conditional node id:{self.id}")
        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        if self.fn:
            state = self.fn(state)

        result = "goto"
        if result in self.output_mapping:
            edge_id = self.output_mapping[result]
            if edge_id in self.edges:
                return (state, self.edges[edge_id])
        return (state, None)


class LoopNode(Node):
    range: int

    def __init__(
        self,
        id: Optional[str] = None,
        fn: Callable = None,
        range: Optional[int] = None,
    ):
        super().__init__(id, fn)
        self.range = range or 1

    def __call__(self, state: Dict) -> Tuple[Dict, Optional[Edge]]:
        if self.fn:
            state = self.fn(state)

        for i in range(self.range):
            # Can only loop contents of the node, so this type of node
            # does not quite make sense entirely
            print(f"Calling loop node id:{self.id} - loop {i+1}/{self.range}")

        # This is the default implementation for the graph that does not have parallel traversal
        # It's kinda like depth first traversal
        # Get all edges, where source node is this node
        if self.edges and len(self.edges) > 0:
            return (state, next(iter(self.edges.values())))
        return (state, None)


source = Node("source", hello_world)
n1 = Node("n1", hello_world)
n2 = ConditionalNode("n2", hello_world, {"goto": "e3"})
n3 = LoopNode("n3", hello_world, 10)
n4 = Node("n4", hello_world)
target = Node("target", hello_world)

e1 = Edge("e1", hello_world)
e2 = Edge("e2", hello_world)
e3 = Edge("e3", hello_world)
e4 = Edge("e4", hello_world)
e5 = Edge("e5", hello_world)
e6 = Edge("e6", hello_world)

graph_config = GraphConfig()
graph_config.add_node("source", source)
graph_config.add_node("n1", n1)
graph_config.add_node("n2", n2)
graph_config.add_node("n3", n3)
graph_config.add_node("n4", n4)
graph_config.add_node("target", target)

graph_config.add_edge("e1", e1)
graph_config.add_edge("e2", e2)
graph_config.add_edge("e3", e3)
graph_config.add_edge("e4", e4)
graph_config.add_edge("e5", e5)
graph_config.add_edge("e6", e6)

graph_config.add_branch("source", "n1", "e1")
graph_config.add_branch("n1", "n2", "e2")
graph_config.add_branch("n2", "n3", "e3")
graph_config.add_branch("n2", "n4", "e4")
graph_config.add_branch("n3", "target", "e5")
graph_config.add_branch("n4", "target", "e6")

graph_config.set_source_node("source")
graph_config.set_target_node("target")

graph = Graph(config=graph_config)

# graph.add_node(source)
# graph.add_node(n1)
# graph.add_node(n2)
# graph.add_node(n3)
# graph.add_node(n4)
# graph.add_node(target)

# graph.add_edge(e1)
# graph.add_edge(e2)
# graph.add_edge(e3)
# graph.add_edge(e4)
# graph.add_edge(e5)
# graph.add_edge(e6)


# graph.connect(source, n1, e1)
# graph.connect(n1, n2, e2)
# graph.connect(n2, n3, e3)
# graph.connect(n2, n4, e4)
# graph.connect(n3, target, e5)
# graph.connect(n4, target, e6)

# graph.set_source_node(source)
# graph.set_target_node(target)

# Measure execution time of graph
state = {"messages": []}
state = graph(state)
print(state)
