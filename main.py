from exsimula.graph import Edge, Graph, Node

source = Node("source")
n1 = Node("n1")
n2 = Node("n2")
n3 = Node("n3")
n4 = Node("n4")
target = Node("target")

e1 = Edge("e1")
e2 = Edge("e2")
e3 = Edge("e3")
e4 = Edge("e4")
e5 = Edge("e5")

graph = Graph()

graph.add_node(n1)
graph.add_node(n2)
graph.add_node(n3)
graph.add_node(n4)
graph.add_edge(e1)
graph.add_edge(e2)
graph.add_edge(e3)
graph.connect(source, n1, e1)
graph.connect(n1, n2, e2)
graph.connect(n2, n3, e3)
graph.connect(n3, n4, e4)
graph.connect(n4, target, e5)

graph.set_source_node(source)
graph.set_target_node(target)

graph()
