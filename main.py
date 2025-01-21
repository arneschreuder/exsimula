from typing import Dict
from exsimula.program import Memory, Program, Source
from pprint import pprint


def f1(state: Dict) -> Dict:
    print("f1")
    state["messages"] = state["messages"] + ["f1"]
    return state, None


def condition(state: Dict) -> Dict:
    print("condition")
    state["messages"] = state["messages"] + ["condition"]
    return state, "goto"


def f2(state: Dict) -> Dict:
    print("f2")
    state["messages"] = state["messages"] + ["f2"]
    return state, None


def f3(state: Dict) -> Dict:
    print("f3")
    state["messages"] = state["messages"] + ["f3"]
    return state, None


def loop(state: Dict) -> Dict:
    print("loop")
    state["messages"] = state["messages"] + ["loop"]
    return state, None


source = Source()
source.add_function("f1", f1)
source.add_condition("condition", condition, {"goto": "condition:loop"})
source.add_function("f2", f2)
source.add_loop("loop", loop, 10)
source.add_function("f3", f3)

source.add_step(Source.START, "f1")
source.add_step("f1", "condition")
source.add_step("condition", "f2")
source.add_step("condition", "loop")
source.add_step("f2", Source.END)
source.add_step("loop", "f3")
source.add_step("f3", Source.END)

program = Program("HelloWorld")
program.compile(source)

memory = Memory({"messages": []})
memory = program(memory)

pprint(memory)
