import random
from typing import Dict

from exsimula.program import Program


# Function to handle user input and update the memory
def user(memory: Dict):
    """
    This function takes user input, adds it to the memory, and decides
    the next action based on the user input.

    Parameters:
    memory (Dict): The current state of the memory, containing the conversation history.

    Returns:
    tuple: A tuple containing the updated memory and the pointer for the next action.
    """
    # Prompt the user for input
    user_input = input("USER: ")

    # Create a message from the user input
    message = {"role": "user", "content": user_input}

    # Add the user's message to the conversation history
    memory["messages"] = memory["messages"] + [message]

    # Decide the next action based on the input
    ptr = Program.NEXT
    if user_input == ":quit":
        # If the user input is ":quit", end the conversation
        ptr = Program.RETURN

    return memory, ptr


# Function to handle the LLM (Large Language Model) input and update the memory
def llm(memory: Dict):
    """
    This function handles the LLM input, adds it to the memory, and decides
    the next action based on the presence of tool calls in the LLM's message.

    Parameters:
    memory (Dict): The current state of the memory, containing the conversation history.

    Returns:
    tuple: A tuple containing the updated memory and the pointer for the next action.
    """
    # Prompt the LLM for input
    llm_input = input("LLM: ")

    # Create a message from the LLM's input, possibly including tool calls
    message = {
        "role": "llm",
        "content": llm_input,
        "tool_calls": (
            ["tool"] if random.random() > 0.5 else None
        ),  # Randomly include tool calls
    }

    # Add the LLM's message to the conversation history
    memory["messages"] = memory["messages"] + [message]

    # Decide the next action based on the presence of tool calls in the LLM's message
    ptr = "goto_user"
    if "tool_calls" in message:
        if message["tool_calls"] and len(message["tool_calls"]) > 0:
            # If tool calls are present, transition to tool calls processing
            ptr = "goto_tools"

    return memory, ptr


# Function to check and process tool calls from the memory
def tool_calls(memory: Dict):
    """
    This function checks if the last message in the conversation has tool calls,
    evaluates the tool calls, and updates the memory with the results.

    Parameters:
    memory (Dict): The current state of the memory, containing the conversation history.

    Returns:
    tuple: A tuple containing the updated memory and the pointer for the next action.
    """
    print("Checking tool calls")

    # Get the last message from the conversation history
    last_message = memory["messages"][-1]

    # Check if the last message has "tool_calls" key
    if "tool_calls" in last_message:
        for tool_call in last_message["tool_calls"]:
            # Evaluate the function represented by the tool call
            result = eval(tool_call + "()")

            # Log the tool call result
            print("HAS CALLED A TOOL")

            # Create a message with the result of the tool call
            message = {"role": "tool_call", "content": result}
    else:
        # If no tool calls are found, create a system message
        message = {"role": "system", "content": "No valid tools"}

    # Add the tool call result or system message to the conversation history
    memory["messages"] = memory["messages"] + [message]

    return memory, "goto_llm"


# Sample tool function to be called via eval
def tool():
    """
    This function simulates a tool call, returning a sample result.

    Returns:
    dict: A dictionary containing a simulated result from the tool.
    """
    return {"WOHOOOOO Some result"}
