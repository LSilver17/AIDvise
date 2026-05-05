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
    if isinstance(state["messages"][-1], ToolMessage):
        message_dump = ""
        for message in state["messages"]:
            message_str = f"{message.role}: {message.content}\n\n"
            message_dump += message_str
        return {"result": message_dump}
    else:
        return {"result": state["messages"][-1].content}

def tool_route(state: InsertionHelperState):
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