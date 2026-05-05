import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import DatabaseHelperState, DatabaseHelperOutput
from utilities.nodes import db_node
from utilities.tools import db_tools, alt_db_tools

tool_node = ToolNode(db_tools)
alt_tool_node = ToolNode(alt_db_tools)

def format_db_output(state: DatabaseHelperState) -> DatabaseHelperOutput:
    if isinstance(state["messages"][-1], ToolMessage):
        message_dump = ""
        for message in state["messages"]:
            message_str = f"{message.role}: {message.content}\n\n"
            message_dump += message_str
        return {"info": {"query": state["info_needed"], "result": message_dump}}
    else:
        return {"info": {"query": state["info_needed"], "result": state["messages"][-1].content}}

def tool_route(state: DatabaseHelperState):
    messages = state["messages"]
    last_message = messages[-1]
    if state["loop_count"] < 3:
        if getattr(last_message, "tool_calls", None):
            if state["account_type"] == "Student":
                return "tool_node"
            else:
                return "alt_tool_node"
        return "format_db_output"
    elif state["loop_count"] == 3:
        if getattr(last_message, "tool_calls", None):
            messages.append("Loop limit reached. Please provide the final answer without using any more tools.")
            return "db"
        else:
            return "format_db_output"
    else:
        tool_dump = []
        for message in messages:
            if isinstance(message, ToolMessage):
                tool_dump.append(message)
            elif isinstance(message, AIMessage):
                messages.append(AIMessage(content="Tool record only", tool_calls=message.tool_calls))
        messages.append("Failsafe: database agent broke the rules. Returning tool ressults instead.")
        messages.extend(tool_dump)
        return "format_db_output"

graph_builder = StateGraph(DatabaseHelperState, output_schema=DatabaseHelperOutput)

graph_builder.add_node("db", db_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("alt_tool_node", alt_tool_node)
graph_builder.add_node("format_db_output", format_db_output)

graph_builder.add_edge(START, "db")
graph_builder.add_conditional_edges("db", tool_route, ["tool_node", "alt_tool_node", "format_db_output"])
graph_builder.add_edge("tool_node", "db")
graph_builder.add_edge("alt_tool_node", "db")
graph_builder.add_edge("format_db_output", END)

db_graph = graph_builder.compile()
