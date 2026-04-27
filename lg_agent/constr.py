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

# cd my-agent && .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
load_dotenv()

def state_init(state: RouteState, config) -> RouteState:
    """Initializes the state for the routing graph."""
    state["user_id"] = config.get("configurable", {}).get("userId")
    state["account_type"] = config.get("configurable", {}).get("accountType")
    return state

def route_node(state: RouteState) -> RouteState:
    """Routes the user to the appropriate chatbot based on their account type."""
    match state["account_type"]:
        case "Student":
            with __connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT ID FROM students WHERE parent_id = ?", (state["user_id"],))
                student_id = cur.fetchone()
                if student_id is None:
                    raise ValueError(f"No student found for parent_id {state['user_id']}")
                result = s_chat_graph.invoke({"messages": state["messages"], "loop_count": 0, "student_id": student_id[0]})
        case "Advisor":
            result = a_chat_graph.invoke({"messages": state["messages"], "loop_count": 0, "user_id": state["user_id"]})
        case _:
            raise ValueError(f"Account type {state['account_type']} not supported.")
        
    return {"messages": result["messages"]}

graph_builder = StateGraph(RouteState)
graph_builder.add_node("state_init", state_init)
graph_builder.add_node("route_node", route_node)

graph_builder.add_edge(START, "state_init")
graph_builder.add_edge("state_init", "route_node")
graph_builder.add_edge("route_node", END)