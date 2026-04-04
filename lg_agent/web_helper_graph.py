from langgraph.graph import StateGraph, START, END
from utilities.state import WebSearchHelperState, WebSearchHelperOutput
from utilities.nodes import web_node

graph_builder = StateGraph(WebSearchHelperState, output_schema=WebSearchHelperOutput)

graph_builder.add_node("web", web_node)

graph_builder.add_edge(START, "web")
graph_builder.add_edge("web", END)

web_graph = graph_builder.compile()
