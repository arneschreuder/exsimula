from typing import Callable, Dict, Optional, Tuple
from exsimula.graph import ConditionalNode, Edge, Graph, GraphConfig, LoopNode, Node


class Source(GraphConfig):
    pass


class Memory(Dict):
    pass


class Source(GraphConfig):
    id: str
    START: str = "start"
    END: str = "end"

    def __init__(self, id: Optional[str] = None):
        super().__init__(id)
        self.add_function(Source.START)
        self.add_function(Source.END)
        self.set_source_node(Source.START)
        self.set_target_node(Source.END)

    def add_function(self, id: str, fn: Optional[Callable[[Dict], Dict]] = None):
        self.add_node(id, Node(id, fn))

    def add_condition(
        self,
        id: str,
        fn: Callable[[Dict], Tuple[Dict, str]],
        output_mapping: Dict[str, str],
    ):
        self.add_node(id, ConditionalNode(id, fn, output_mapping))

    def add_loop(
        self,
        id: str,
        fn: Callable[[Dict], Tuple[Dict, str]],
        range: int,
    ):
        self.add_node(id, LoopNode(id, fn, range))

    def add_step(
        self, from_node: str, to_node: str, fn: Optional[Callable[[Dict], Dict]] = None
    ):
        edge_id = f"{from_node}:{to_node}"
        edge = Edge(edge_id, fn)
        self.add_edge(edge_id, edge)
        self.add_branch(from_node, to_node, edge.id)


class Program(Graph):
    def compile(self, source: Source):
        self.load_config(source)
