import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import WebSearchHelperState, WebSearchHelperOutput
from utilities.nodes import web_node
from utilities.tools import web_tools

tool_node = ToolNode(web_tools)

def format_web_output(state: WebSearchHelperState) -> WebSearchHelperOutput:
    if isinstance(state["messages"][-1], ToolMessage):
        message_dump = ""
        for message in state["messages"]:
            message_str = f"{message.role}: {message.content}\n\n"
            message_dump += message_str
        return {"info": {"query": state["info_needed"], "result": message_dump}}
    else:
        return {"info": {"query": state["info_needed"], "result": state["messages"][-1].content}}

def tool_route(state: WebSearchHelperState):
    messages = state["messages"]
    last_message = messages[-1]
    if state["loop_count"] < 3:
        if getattr(last_message, "tool_calls", None):
            return "tool_node"
        return "format_web_output"
    elif state["loop_count"] == 3:
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
