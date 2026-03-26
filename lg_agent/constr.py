from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from lg_agent.utilities.state import AdvisorState
from lg_agent.utilities.nodes import planning_node
import sqlite3

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

graph_builder = StateGraph(AdvisorState)

graph_builder.add_node("planning", planning_node)

graph_builder.add_edge(START, "planning")

graph_builder.add_edge("planning", "db_node", condition=lambda state: state["plan"]["requires_database"])
graph_builder.add_edge("planning", "web_node", condition=lambda state: state["plan"]["requires_web_search"])
graph_builder.add_edge("planning", "answer_node", condition=lambda state: not state["plan"]["requires_database"] and not state["plan"]["requires_web_search"])

graph_builder.add_edge("db_node", "answer_node")
graph_builder.add_edge("web_node", "answer_node")

graph_builder.add_edge("answer_node", END)

graph = graph_builder.compile()

# TODO: figure out how to initialize the state with the sqlite cursor and any other necessary information