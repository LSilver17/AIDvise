import sys, os

"""
Copyright 2026 Luca Silver

Insertion helper subgraph that processes student profile updates (interests and tracked sections).

Functions:
- `format_insertion_output`: Normalizes insertion helper response into standardized helper output schema.
- `tool_route`: Conditionally routes insertion helper loop based on tool calls and loop count (max 3 iterations).

Graph Structure:
- START -> insertion_node
- insertion_node -> [tool_node | format_insertion_output] (conditional routing based on tool_route)
- tool_node -> insertion_node (feedback loop)
- format_insertion_output -> END

Exports:
- `insertion_graph`: Compiled LangGraph insertion helper subgraph.
"""

import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import InsertionHelperState, InsertionHelperOutput
from utilities.nodes import insertion_node
from utilities.tools import insertion_tools

tool_node = ToolNode(insertion_tools)

def format_insertion_output(state: InsertionHelperState) -> InsertionHelperOutput:
    """
    Normalizes the insertion helper response into the helper output schema.

    If the last message is a tool message (meaning the insertion helper passed its 
    loop limit without providing a final answer), the full message history is serialized so
    the planner can inspect the tool trail. Otherwise, the final AI message content
    is returned directly as the insertion result.

    Args:
        state (InsertionHelperState): Helper state containing the insertion request
            context and the message history produced by the insertion loop.

    Returns:
        InsertionHelperOutput: Output object containing the formatted insertion result.
    """
    if isinstance(state["messages"][-1], ToolMessage):
        message_dump = ""
        for message in state["messages"]:
            message_str = f"{message.role}: {message.content}\n\n"
            message_dump += message_str
        return {"result": message_dump}
    else:
        return {"result": state["messages"][-1].content}

def tool_route(state: InsertionHelperState):
    """
    Routes the insertion helper loop based on tool usage and loop count.

    The insertion helper is allowed a limited number of iterations. If the latest
    AI message includes tool calls, the graph routes to the tool node. Otherwise it
    formats the output. If the loop limit is reached, the function enforces a final
    response path and includes a fallback message when necessary.

    Args:
        state (InsertionHelperState): Current helper state including messages,
            loop counter, and requested insertion content.

    Returns:
        str: The next node name to execute.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if state["loop_count"] < 3:
        if getattr(last_message, "tool_calls", None):
            return "tool_node"
        return "format_insertion_output"
    elif state["loop_count"] == 3:
        if getattr(last_message, "tool_calls", None):
            messages.append("Loop limit reached. Please provide the result of your attempts without using any more tools.")
            return "insertion"
        else:
            return "format_insertion_output"
    else:
        tool_dump = []
        for message in messages:
            if isinstance(message, ToolMessage):
                tool_dump.append(message)
            elif isinstance(message, AIMessage):
                messages.append(AIMessage(content="Tool record only", tool_calls=message.tool_calls))
        messages.append("Failsafe: insertion agent broke the rules. Returning tool ressults instead.")
        messages.extend(tool_dump)
        return "format_insertion_output"

graph_builder = StateGraph(InsertionHelperState, output_schema=InsertionHelperOutput)

graph_builder.add_node("insertion", insertion_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("format_insertion_output", format_insertion_output)

graph_builder.add_edge(START, "insertion")
graph_builder.add_conditional_edges("insertion", tool_route, ["tool_node", "format_insertion_output"])
graph_builder.add_edge("tool_node", "insertion")
graph_builder.add_edge("format_insertion_output", END)

insertion_graph = graph_builder.compile()