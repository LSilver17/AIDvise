import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import InsertionHelperState
from utilities.nodes import insertion_node
from utilities.tools import insertion_tools

tool_node = ToolNode(insertion_tools)

def should_continue(state: InsertionHelperState):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None) and state["loop_count"] < 3:
        return "tool_node"
    return END

graph_builder = StateGraph(InsertionHelperState)

graph_builder.add_node("insertion", insertion_node)
graph_builder.add_node("tool_node", tool_node)

graph_builder.add_edge(START, "insertion")
graph_builder.add_conditional_edges("insertion", should_continue, ["tool_node", END])
graph_builder.add_edge("tool_node", "insertion")

insertion_graph = graph_builder.compile()