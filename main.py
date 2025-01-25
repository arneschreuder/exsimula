from __future__ import annotations
from copy import deepcopy
import random
import asyncio
from typing import AsyncGenerator, AsyncIterator, List, Tuple, Union

from exsimula import Program, Memory, Function


class MyMemory(Memory):
    """
    Custom memory class to track messages.
    """

    messages: List[str]


class Function1(Function):
    """
    A simple function that appends "f1" to the messages in memory.
    """

    def __call__(self, memory: MyMemory) -> MyMemory:
        new_memory = deepcopy(memory)
        new_memory["messages"].append("f1")
        return new_memory


class Function2(Function):
    """
    A function that appends "f2" to the messages in memory and returns a condition.
    """

    def __call__(self, memory: MyMemory) -> Tuple[MyMemory, str]:
        new_memory = deepcopy(memory)
        new_memory["messages"].append("f2")
        return new_memory, "true"


class Function3(Function):
    """
    A function that appends chunks of "f2" to the messages in memory and returns a condition.
    """

    async def __call__(
        self, memory: MyMemory
    ) -> AsyncIterator[Union[MyMemory, Tuple[MyMemory, str]]]:
        new_memory = deepcopy(memory)

        # Split the message into chunks
        lorem_ipsum = "One two three"
        message_chunks = lorem_ipsum.split(" ")

        for chunk in message_chunks:
            await asyncio.sleep(0.5)  # Simulate delay for typing the message
            new_memory["messages"][
                -1
            ] += f" {chunk}"  # Append the chunk to the last message
            yield new_memory  # Yield the memory so we can stream the intermediate state

        yield new_memory, Program.CONTINUE


def on_memory_update(memory: MyMemory):
    if memory["messages"]:
        print("Memory updated: " + memory["messages"][-1])


async def main():
    """
    Main function to demonstrate both synchronous and asynchronous streaming execution.
    """

    # Define the program
    program = Program()
    program.add_function("f1", Function1())
    program.add_function("f2", Function2())
    program.add_function("f3", Function3())
    program.add_step(Program.INIT, "f1")
    program.add_step("f1", "f2")
    program.add_condition("f2", {"true": "f3", "false": Program.RETURN})
    program.add_step("f3", Program.RETURN)
    program.subscribe(on_memory_update)

    # Synchronous execution
    # memory = MyMemory(messages=[])
    # memory = await program(memory, run_async=False)
    # print(memory)

    # Asynchronous streaming execution
    memory = MyMemory(messages=[])
    async for memory in await program(memory, run_async=True):
        # print(memory)
        pass


if __name__ == "__main__":
    asyncio.run(main())
