import sys, os

# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from lg_agent.utilities.state import RouteState
from s_chat_graph import s_chat_graph
from a_chat_graph import a_chat_graph
from data_pipeline.database.database_dev_tools import __connect
from typing import Literal

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

def route(state: RouteState) -> Literal["invoke_s_graph", "invoke_a_graph"]:
    """Routes the user to the appropriate chatbot based on their account type."""
    match state["account_type"]:
        case "Student":
            return "invoke_s_graph"
        case "Advisor":
            return "invoke_a_graph"

def invoke_s_graph(state: RouteState) -> RouteState:
    """Invokes the student chatbot graph."""
    with __connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID FROM students WHERE ParentID = ?", (state["user_id"],))
        student_id = cur.fetchone()
        if student_id is None:
            raise ValueError(f"No student found for parent_id {state['user_id']}")
        result = s_chat_graph.invoke({"messages": state["messages"], "plan": {}, "loop_count": 0, "user_id": student_id[0], "insertion_result": ""})
    return {"messages": result["messages"]}

def invoke_a_graph(state: RouteState) -> RouteState:
    """Invokes the advisor chatbot graph."""
    result = a_chat_graph.invoke({"messages": state["messages"], "plan": {}, "loop_count": 0, "user_id": state["user_id"]})
    return {"messages": result["messages"]}

graph_builder = StateGraph(RouteState, )

graph_builder.add_node("invoke_s_graph", invoke_s_graph)
graph_builder.add_node("invoke_a_graph", invoke_a_graph)

graph_builder.add_conditional_edges(START, route, ["invoke_s_graph", "invoke_a_graph"])
graph_builder.add_edge("invoke_s_graph", END)
graph_builder.add_edge("invoke_a_graph", END)

chat_graph = graph_builder.compile()