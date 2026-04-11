import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import DatabaseHelperState, DatabaseHelperOutput
from utilities.nodes import db_node
from utilities.tools import db_tools

tool_node = ToolNode(db_tools)

def format_db_output(state: DatabaseHelperState) -> DatabaseHelperOutput:
    return {"info": {"query": state["info_needed"], "result": state["messages"][-1].content}}

def should_continue(state: DatabaseHelperState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool_node"
    return "format_db_output"

graph_builder = StateGraph(DatabaseHelperState, output_schema=DatabaseHelperOutput)

graph_builder.add_node("db", db_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("format_db_output", format_db_output)

graph_builder.add_edge(START, "db")
graph_builder.add_conditional_edges("db", should_continue, ["tool_node", "format_db_output"])
graph_builder.add_edge("tool_node", "db")
graph_builder.add_edge("format_db_output", END)

db_graph = graph_builder.compile()
