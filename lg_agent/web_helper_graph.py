"""
Copyright 2026 Luca Silver

Web search helper subgraph that executes web searches for the planning agents.

Functions:
- `format_web_output`: Normalizes web search helper response into standardized helper output schema.
- `tool_route`: Conditionally routes web helper loop based on tool calls and loop count.

Graph Structure:
- START -> web_node
- web_node -> [tool_node | format_web_output] (conditional routing based on tool_route)
- tool_node -> web_node (feedback loop)
- format_web_output -> END

Exports:
- `web_graph`: Compiled LangGraph web search helper subgraph.

Loop limits are defined in config.json.
"""

import sys, os

# adds lg_agent directory to system path if not already there
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import WebSearchHelperState, WebSearchHelperOutput
from utilities.nodes import web_node
from utilities.tools import web_tools
import json

CONFIG_PATH = os.path.join(PARENT_DIR, "config.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)
    LOOP_CONFIG = CONFIG["loop_limits"]

tool_node = ToolNode(web_tools)

def format_web_output(state: WebSearchHelperState) -> WebSearchHelperOutput:
    """
    Normalizes the web helper response into the helper output schema.

    If the last message is a tool message (meaning the web search helper passed its 
    loop limit without providing a final answer), the full message history is serialized 
    into a single string so the planner can inspect the tool trail. Otherwise, the final 
    AI message content is returned directly as the web result.

    Args:
        state (WebSearchHelperState): Helper state containing the search request
            context and the message history produced by the web helper loop.

    Returns:
        WebSearchHelperOutput: Output object containing the original query and the
            formatted web result string.
    """
    if isinstance(state["messages"][-1], ToolMessage):
        message_dump = ""
        for message in state["messages"]:
            message_str = f"{message.role}: {message.content}\n\n"
            message_dump += message_str
        return {"info": {"query": state["info_needed"], "result": message_dump}}
    else:
        return {"info": {"query": state["info_needed"], "result": state["messages"][-1].content}}

def tool_route(state: WebSearchHelperState):
    """
    Routes the web helper loop based on tool usage and loop count.

    The web helper is allowed a limited number of iterations. If the latest AI
    message includes tool calls, the graph routes to the tool node. Otherwise it
    formats the output. If the loop limit is reached, the function enforces a final
    response path and includes a fallback message when necessary.

    Args:
        state (WebSearchHelperState): Current helper state including messages,
            loop counter, and requested web information.

    Returns:
        str: The next node name to execute.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if state["loop_count"] < LOOP_CONFIG["web"]:
        if getattr(last_message, "tool_calls", None):
            return "tool_node"
        return "format_web_output"
    elif state["loop_count"] == LOOP_CONFIG["web"]:
        if getattr(last_message, "tool_calls", None):
            messages.append("Loop limit reached. Please provide the final answer without using any more tools.")
            return "web"
        else:
            return "format_web_output"
    else:
        tool_dump = []
        for message in messages:
            if isinstance(message, ToolMessage):
                tool_dump.append(message)
            elif isinstance(message, AIMessage):
                messages.append(AIMessage(content="Tool record only", tool_calls=message.tool_calls))
        messages.append("Failsafe: web search agent broke the rules. Returning tool ressults instead.")
        messages.extend(tool_dump)
        return "format_web_output"

graph_builder = StateGraph(WebSearchHelperState, output_schema=WebSearchHelperOutput)

graph_builder.add_node("web", web_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("format_web_output", format_web_output)

graph_builder.add_edge(START, "web")
graph_builder.add_conditional_edges("web", tool_route, ["tool_node", "format_web_output"])
graph_builder.add_edge("tool_node", "web")
graph_builder.add_edge("format_web_output", END)

web_graph = graph_builder.compile()
