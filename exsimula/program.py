import importlib
import json
from typing import Callable, Dict, Optional, OrderedDict, Tuple
import time


class Program:
    # Class-level constants
    id: str  # Program's unique identifier
    functions: OrderedDict[
        str, Tuple[Callable, Dict]
    ]  # Ordered dict to store functions with their metadata
    INIT: str = "init"  # Special string representing the initial function
    NEXT: str = "next"  # Special string to indicate the next function
    RETURN: str = "return"  # Special string to indicate the end of the program

    def __init__(self, id: str = None, config: str = None):
        """Initialize the program with an ID and an empty function dictionary."""
        self.id = id  # Set the program's unique ID
        self.functions = (
            OrderedDict()
        )  # Initialize an ordered dictionary to store functions

        if config is not None:
            self.from_config(config)

    # Function to dynamically import a function from a module using its full path
    def load_function(self, module_function: str):
        """
        Loads a function dynamically from a module by splitting the module path and function name.

        Args:
            module_function (str): Full path to the function, e.g., "module.submodule.function".

        Returns:
            function: The function object obtained from the module.
        """
        # Split the full function path into module path and function name
        module_path, function_name = module_function.rsplit(".", 1)

        # Import the module dynamically
        module = importlib.import_module(module_path)

        # Return the function object from the module
        return getattr(module, function_name)

    def from_config(self, config_path: str):
        """
        Initializes the object based on the provided configuration file.

        Args:
            config_path (str): Path to the JSON configuration file.
        """
        # Open and load the JSON configuration file
        with open(config_path, "r") as f:
            config = json.load(f)

        # Set the id from the configuration
        self.id = config["id"]

        # Iterate over the list of functions in the configuration
        for func_config in config["functions"]:
            # Load the function dynamically using the function's module path
            function = self.load_function(
                func_config["fn"]
            )  # 'fn' is the module path to the function

            # Add the function to the class with the provided id and optional metadata
            self.add_function(func_config["id"], function, func_config.get("meta", {}))

    def add_function(self, id: str, fn: Callable, meta: Optional[Dict] = None):
        """
        Adds a new function to the program.

        Args:
            id: The identifier for the function.
            fn: The callable function that represents the function's logic.
            meta: Optional metadata for the function (default is None).
        """
        if id in self.functions:
            raise Exception(
                f"Function {id} already exists in functions"
            )  # Ensure function ID is unique
        self.functions[id] = (
            fn,
            meta,
        )  # Add the function to the dictionary with its metadata

    def get_next_function(self, ptr: str) -> Optional[str]:
        """
        Retrieves the next function ID based on the current function pointer.

        Args:
            ptr: The current function ID to start searching from.

        Returns:
            The next function ID, or "return" if there are no more functions.
        """
        # Create an iterator for the function IDs
        keys = iter(self.functions.keys())

        # Skip to the current function ID if necessary
        if ptr != Program.INIT:
            for key in keys:
                if key == ptr:
                    break  # Stop at the current function ID

        # Return the next function ID or the "return" value if no more functions
        return next(keys, Program.RETURN)

    def step(
        self,
        memory: Dict = None,
        ptr: Optional[str] = None,
    ):
        """
        Executes one step of the program.

        Args:
            memory: A dictionary to hold the program's state (default is None).
            ptr: The current function pointer (default is None, which means starting from "init").

        Returns:
            A tuple containing the updated memory and the next function pointer.
        """
        if ptr is None:
            ptr = Program.INIT  # Start from the INIT function if no pointer is provided
            ptr = self.get_next_function(ptr)  # Move to the next function
        elif ptr == Program.INIT:
            ptr = self.get_next_function(ptr)  # Move to the next function after "init"
        elif ptr == Program.NEXT:
            ptr = self.get_next_function(ptr)  # Move to the next function after "next"
            if ptr == Program.RETURN:
                return memory, ptr  # End of program
        elif ptr == Program.RETURN:
            return memory, ptr  # End of program
        else:
            # Ensure the current function ID exists in the program
            if ptr not in self.functions.keys():
                raise Exception(f"Function {ptr} not found in functions")

        # Execute the current function and get the updated memory and route
        function_fn, meta = self.functions[ptr]
        memory, route = function_fn(memory)

        # Handle routing based on the function's route value
        if route == Program.NEXT:
            ptr = self.get_next_function(ptr)  # Move to the next function
        elif route in [Program.INIT, Program.RETURN]:
            ptr = route  # End or restart based on the route
        elif route in self.functions.keys():
            ptr = route  # Move to a specified function
        elif meta is not None and route in meta:
            ptr = meta[route]  # Use metadata to determine the next function
        else:
            raise Exception(
                f'Cannot route to next function. No meta provided action "{route}".'
            )

        return memory, ptr

    def run(self, memory: Optional[Dict] = None, max_steps: int = None):
        """
        Runs the program to completion (or until the max steps are reached).

        Args:
            memory: A dictionary to hold the program's state (default is None).
            max_steps: The maximum number of steps the program should run before stopping (default is 10).

        Returns:
            The final memory after the program finishes.
        """
        print(f'Running "{self.id}" (max functions={max_steps})')
        start_time = time.time()  # Record the start time
        ptr = Program.INIT  # Start from the INIT function
        step_counter = 0  # Initialize step counter

        while ptr != Program.RETURN:
            memory, ptr = self.step(memory, ptr)  # Perform one step of the program
            step_counter += 1  # Increment the step counter

            if max_steps is not None:
                if step_counter > max_steps:
                    raise Exception(
                        "Max steps exceeded"
                    )  # Ensure the program doesn't run forever

        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(
            f"Done. Execution time: {execution_time:.2f} seconds"
        )  # Print execution time
        return memory  # Return the final memory state
