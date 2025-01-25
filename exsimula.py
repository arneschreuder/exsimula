import asyncio
from typing import (
    AsyncIterator,
    Callable,
    Dict,
    List,
    Tuple,
    TypedDict,
    Union,
)


class Memory(TypedDict):
    pass


class Function(
    Callable[
        [Memory],
        Union[
            Memory,
            Tuple[Memory, str],
            AsyncIterator[Memory],
            AsyncIterator[Tuple[Memory, str]],
        ],
    ]
):
    pass


class Program:
    ip: str  # instruction pointer
    functions: Dict[str, Callable]
    steps: Dict[str, str]
    conditions: Dict[str, Dict[str, str]]
    subscribers: List[Callable[[Memory], None]]
    INIT = "init"
    RETURN = "return"
    CONTINUE = "continue"

    def __init__(self):
        self.ip = Program.INIT
        self.functions = {}
        self.steps = {}
        self.conditions = {}
        self.subscribers = []
        self.add_function(Program.INIT, lambda memory: memory)
        self.add_function(Program.RETURN, lambda memory: memory)

    async def __call__(self, memory: Memory, run_async: bool = False) -> Memory:
        if not run_async:
            return await self.run(memory)

        return self.run_async(memory)

    async def run(self, memory: Memory) -> Memory:
        self.ip = Program.INIT

        while self.ip is not Program.RETURN:
            result = self.functions[self.ip](memory)

            if asyncio.iscoroutine(result):
                result = await result

            if isinstance(result, AsyncIterator):
                async for delta in result:
                    # Step
                    if isinstance(delta, dict):
                        memory = delta
                        await self.emit(memory)
                    # Condition
                    elif isinstance(delta, Tuple):
                        memory, condition = delta
                        await self.emit(memory)
                        # Break on continue
                        if condition == Program.CONTINUE:
                            self.ip = self.steps[self.ip]
                            break
                        # Invalid condition
                        if condition not in self.conditions[self.ip]:
                            raise ValueError("Invalid function return value")
                        # Break on condition
                        self.ip = self.conditions[self.ip][condition]
                        break
                    # Invalid
                    else:
                        raise ValueError("Invalid function return value")
            # Step
            elif isinstance(result, dict):
                memory = result
                self.ip = self.steps[self.ip]
                await self.emit(memory)
            # Condition
            elif isinstance(result, Tuple):
                memory, condition = result
                if condition not in self.conditions[self.ip]:
                    raise ValueError("Invalid function return value")
                self.ip = self.conditions[self.ip][condition]
                await self.emit(memory)
            # Invalid
            else:
                raise ValueError("Invalid function return value")
        return memory

    async def run_async(self, memory: Memory) -> AsyncIterator[Memory]:
        self.ip = Program.INIT

        while self.ip is not Program.RETURN:
            result = self.functions[self.ip](memory)

            if asyncio.iscoroutine(result):
                result = await result

            if isinstance(result, AsyncIterator):
                async for delta in result:
                    # Step
                    if isinstance(delta, dict):
                        memory = delta
                        await self.emit(memory)
                        yield memory
                    # Condition
                    elif isinstance(delta, Tuple):
                        memory, condition = delta
                        await self.emit(memory)
                        # Break on continue
                        if condition == Program.CONTINUE:
                            self.ip = self.steps[self.ip]
                            yield memory
                            break
                        # Invalid condition
                        if condition not in self.conditions[self.ip]:
                            raise ValueError("Invalid function return value")
                        # Break on condition
                        self.ip = self.conditions[self.ip][condition]
                        # Debtable whether this is needed of not
                        yield memory
                        break
                    # Invalid
                    else:
                        raise ValueError("Invalid function return value")
            # Step
            elif isinstance(result, dict):
                memory = result
                self.ip = self.steps[self.ip]
                await self.emit(memory)
                yield memory
            # Condition
            elif isinstance(result, Tuple):
                memory, condition = result
                if condition not in self.conditions[self.ip]:
                    raise ValueError("Invalid function return value")
                self.ip = self.conditions[self.ip][condition]
                await self.emit(memory)
                yield memory
            # Invalid
            else:
                raise ValueError("Invalid function return value")
        await self.emit(memory)
        yield memory

    def add_function(self, address: str, fn: Callable):
        assert address not in self.functions
        self.functions[address] = fn

    def add_step(self, address: str, next_address: str):
        assert address in self.functions, f"Function {address} not found"
        assert next_address in self.functions, f"Function {next_address} not found"
        assert (
            address not in self.steps
        ), f"Step {address}->{next_address} already exists"
        assert address not in self.conditions, f"Condition {address} already exists"
        self.steps[address] = next_address

    def add_condition(self, address: str, condition: Dict[str, str]):
        assert address in self.functions, f"Function {address} already exists"
        assert address not in self.steps, f"Step {address} already exists"
        assert address not in self.conditions, f"Condition {address} already exists"
        for _, next_address in condition.items():
            assert next_address in self.functions, f"Function {next_address} not found"
        self.conditions[address] = condition

    def subscribe(self, callback: Callable[[Memory], None]):
        """
        Register a callback to receive memory updates during execution.

        Args:
            callback (Callable[[Memory], None]): The callback function to register.
        """
        self.subscribers.append(callback)

    async def emit(self, memory: Memory):
        for subscriber in self.subscribers:
            subscriber(memory)
