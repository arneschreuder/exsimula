from typing import Dict, Callable
from exsimula.decorators import create_decorators
from exsimula.program import Memory, Program, Source
from pprint import pprint

# Create a Source instance
source = Source()

# Generate decorators for this specific Source
function, condition, loop, step = create_decorators(source)


# Define functions and steps using the decorators
@function()
def f1(state: Dict) -> Dict:
    print("f1")
    state["messages"] = state["messages"] + ["f1"]
    return state, None


@condition({True: "condition:f2", False: "condition:loop"})
def condition_func(state: Dict) -> Dict:
    print("condition")
    state["messages"] = state["messages"] + ["condition"]
    return state, False


@function()
def f2(state: Dict) -> Dict:
    print("f2")
    state["messages"] = state["messages"] + ["f2"]
    return state, None


@loop(10)
def loop_func(state: Dict) -> Dict:
    print("loop")
    state["messages"] = state["messages"] + ["loop"]
    return state, None


@function()
def f3(state: Dict) -> Dict:
    print("f3")
    state["messages"] = state["messages"] + ["f3"]
    return state, None


# Add steps between functions
source.add_step(Source.START, "f1")
source.add_step("f1", "condition")
source.add_step("condition", "f2")
source.add_step("condition", "loop")
source.add_step("f2", Source.END)
source.add_step("loop", "f3")
source.add_step("f3", Source.END)


# Compile and execute the program
program = Program()
program.compile(source)

memory = Memory({"messages": []})
memory = program(memory)

pprint(memory)
