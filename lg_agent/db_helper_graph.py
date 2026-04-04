from langgraph.graph import StateGraph, START, END
from utilities.state import DatabaseHelperState, DatabaseHelperOutput
from utilities.nodes import db_node

graph_builder = StateGraph(DatabaseHelperState, output_schema=DatabaseHelperOutput)

graph_builder.add_node("db", db_node)

graph_builder.add_edge(START, "db")
graph_builder.add_edge("db", END)

db_graph = graph_builder.compile()
