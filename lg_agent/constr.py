from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from lg_agent.utilities.state import AdvisorState
from lg_agent.utilities.nodes import advisor_node
import sqlite3

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

conn = sqlite3.connect("Test.db")
cursor = conn.cursor()

graph_builder = StateGraph(AdvisorState)

graph_builder.add_node("advisor_cb", advisor_node)

graph_builder.add_edge(START, "advisor_cb")
graph_builder.add_edge("advisor_cb", END)

graph = graph_builder.compile()
