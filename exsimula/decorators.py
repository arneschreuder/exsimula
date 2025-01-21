# Factory function to create decorators for a given source instance
from typing import Callable, Dict
from exsimula.program import Source


def create_decorators(source: Source):
    def function():
        def decorator(func: Callable):
            source.add_function(func.__name__.replace("_func", ""), func)
            return func

        return decorator

    def condition(transitions: Dict[bool, str]):
        def decorator(func: Callable):
            source.add_condition(func.__name__.replace("_func", ""), func, transitions)
            return func

        return decorator

    def loop(max_iterations: int):
        def decorator(func: Callable):
            source.add_loop(func.__name__.replace("_func", ""), func, max_iterations)
            return func

        return decorator

    def step(from_step: str, to_step: str):
        def decorator(func: Callable):
            # Steps don't directly use the function but register transitions
            source.add_step(from_step, to_step)
            return func

        return decorator

    return function, condition, loop, step
