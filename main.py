from typing import Dict
from exsimula.graph import GraphConfig
from exsimula.llms import OpenAILLM
from exsimula.program import Memory, Program, Source
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()


def user(state: Dict) -> Dict:
    user_input = input("USER: ")
    state["messages"] = state["messages"] + [user_input]
    return state, None


def condition(state: Dict) -> Dict:
    print("condition")
    state["messages"] = state["messages"] + ["condition"]
    return state, True


def f3(state: Dict) -> Dict:
    print("Agent is executing function")
    state["messages"] = state["messages"] + ["f3"]
    return state, None


def loop(state: Dict) -> Dict:
    print("loop")
    state["messages"] = state["messages"] + ["loop"]
    return state, None


llm = OpenAILLM("openai")
source = Source()
source.add_function("user", user)
source.add_condition(
    "condition",
    condition,
    {
        True: "condition:llm",  # This is not great, user only wants to make to next node/function, not edge
        False: "condition:loop",
    },
)
source.add_function("llm", llm)
source.add_loop("loop", loop, 10)
source.add_function("f3", f3)

source.add_step(Source.START, "user")
source.add_step("user", "condition")
source.add_step("condition", "llm")
source.add_step("condition", "loop")
source.add_step("llm", "user")
source.add_step("llm", Source.END)
source.add_step("loop", "f3")
source.add_step("f3", Source.END)

program = Program()
program.compile(source)

memory = Memory({"messages": []})
# memory = program(memory)

pprint(memory)


def graph_config_to_mermaid(graph_config: GraphConfig) -> str:
    mermaid_lines = ["graph TD;"]

    # Add nodes
    for node_id in graph_config.nodes:
        if node_id == Source.START:
            node_id = f"__{Source.START}__"
        if node_id == Source.END:
            node_id = f"__{Source.END}__"
        mermaid_lines.append(f"{node_id}")

    # # Add edges
    # for edge_id, edge in graph_config.edges.items():
    #     source = edge.source_  # Assuming Edge has source and target attributes
    #     target = edge.target
    #     mermaid_lines.append(f"  {source} -->|{edge_id}| {target}")

    # Add branches
    for source_id, targets in graph_config.branches.items():
        if source_id == Source.START:
            source_id = f"__{Source.START}__"
        if source_id == Source.END:
            source_id = f"__{Source.END}__"

        for target_id, edge_id in targets.items():
            if target_id == Source.START:
                target_id = f"__{Source.START}__"
            if target_id == Source.END:
                target_id = f"__{Source.END}__"
            mermaid_lines.append(f"{source_id}-.->|{edge_id}|{target_id}")

    return "\n".join(mermaid_lines)


mm = graph_config_to_mermaid(source)
print(mm)
