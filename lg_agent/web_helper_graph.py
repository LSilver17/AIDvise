from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from utilities.state import WebSearchHelperState, WebSearchHelperOutput
from utilities.nodes import web_node
from utilities.tools import web_tools

tool_node = ToolNode(web_tools)

def format_web_output(state: WebSearchHelperState) -> WebSearchHelperOutput:
    return {"info": {"query": state["info_needed"], "result": state["messages"][-1]}}

def should_continue(state: WebSearchHelperState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool_node"
    return "format_web_output"

graph_builder = StateGraph(WebSearchHelperState, output_schema=WebSearchHelperOutput)

graph_builder.add_node("web", web_node)
graph_builder.add_node("tool_node", tool_node)
graph_builder.add_node("format_web_output", format_web_output)

graph_builder.add_edge(START, "web")
graph_builder.add_conditional_edges("web", should_continue, ["tool_node", "format_web_output"])
graph_builder.add_edge("tool_node", "web")
graph_builder.add_edge("format_web_output", END)

web_graph = graph_builder.compile()
