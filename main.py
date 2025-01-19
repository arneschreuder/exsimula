import importlib
import json
import typer
from exsimula.program import Program
from pathlib import Path


def run_program(program_config_path: Path, memory_config_path: Path):
    """
    Initializes and runs the program with the given configuration files.

    Args:
        program_config_path (Path): Path to the program's configuration file.
        memory_config_path (Path): Path to the memory's configuration file.
    """
    # Initialize the program with the loaded program configuration
    program = Program(config=program_config_path)

    # Load the memory configuration from the given path
    with open(memory_config_path, "r") as f:
        memory = json.load(f)

    # Run the program with the initial memory and update memory
    memory = program.run(memory)

    # Print the updated memory after running the program
    print(memory)


def main(
    program: Path = typer.Option(
        ..., "--program", help="Path to the program config file"
    ),
    memory: Path = typer.Option(..., "--memory", help="Path to the memory config file"),
):
    """
    Main entry point for the CLI tool that runs the program.

    Args:
        program (Path): Path to the program configuration file (provided via CLI argument).
        memory (Path): Path to the memory configuration file (provided via CLI argument).
    """
    # Call the run_program function with the provided config paths
    run_program(program, memory)


if __name__ == "__main__":
    # Execute the main function when the script is run
    typer.run(main)
