import sys, os

from langchain.messages import AIMessage
    
# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# adds root directory to system path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from utilities.state import APlannerState, SPlannerState, DatabaseHelperState, WebSearchHelperState, InsertionHelperState
from utilities.schemas import APlanSchema, SPlanSchema
from utilities.tools import db_tools, web_tools, insertion_tools, alt_db_tools
from utilities.model_inits import db_llm, planning_llm, web_llm, insertion_llm
import json

load_dotenv()

CONTEXT_CONFIG_PATH = os.path.join(root_dir, "context_config.json")

with open(CONTEXT_CONFIG_PATH, "r") as f:
    CONTEXT_CONFIG = json.load(f)

def s_planner_node(state: SPlannerState) -> SPlannerState:
    """Base node for the agent when used by a student, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    state["loop_count"] += 1
    state["plan"] = None

    structured_llm = planning_llm.with_structured_output(SPlanSchema)

    c_level = CONTEXT_CONFIG["s-planner"]["context-select"]
    system_prompt = CONTEXT_CONFIG["s-planner"]["context-level"][c_level]

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
            messages.append(AIMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(AIMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    if state["insertion_result"] != "":
        messages.append(AIMessage(content=f"Result of last insertion attempt: {state['insertion_result']}"))

    messages.append(AIMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    return state

def a_planner_node(state: APlannerState) -> APlannerState:
    """Base node for the agent when used by an advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    state["loop_count"] += 1

    structured_llm = planning_llm.with_structured_output(APlanSchema)

    c_level = CONTEXT_CONFIG["a-planner"]["context-select"]
    system_prompt = CONTEXT_CONFIG["a-planner"]["context-level"][c_level]

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
                messages.append(AIMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(AIMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    messages.append(AIMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    return state

def db_node(state: DatabaseHelperState):
    """Node that runs database queries based on the information provided by the planning node."""

    state["loop_count"] += 1

    if state["account_type"] == "Student":
        llm_with_db_tools = db_llm.bind_tools(db_tools)
        c_level = CONTEXT_CONFIG["s-db"]["context-select"]
        system_prompt = CONTEXT_CONFIG["s-db"]["context-level"][c_level]
    else:
        llm_with_db_tools = db_llm.bind_tools(alt_db_tools)
        c_level = CONTEXT_CONFIG["a-db"]["context-select"]
        system_prompt = CONTEXT_CONFIG["a-db"]["context-level"][c_level]
    
    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(AIMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_db_tools.invoke(messages)

    return {"messages": [result]}

def web_node(state: WebSearchHelperState):
    """Node that performs web searches based on the information provided by the planning node."""
    
    state["loop_count"] += 1

    llm_with_web_tools = web_llm.bind_tools(web_tools)

    c_level = CONTEXT_CONFIG["web"]["context-select"]
    system_prompt = CONTEXT_CONFIG["web"]["context-level"][c_level]

    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the web to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(AIMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_web_tools.invoke(messages)

    return {"messages": [result]}

def insertion_node(state: InsertionHelperState) -> InsertionHelperState:
    """Node that takes any new information the advisor has learned about the student and inserts it into the database."""

    state["loop_count"] += 1

    llm_with_insertion_tools = insertion_llm.bind_tools(insertion_tools)

    c_level = CONTEXT_CONFIG["insertion"]["context-select"]
    system_prompt = CONTEXT_CONFIG["insertion"]["context-level"][c_level]

    # if state messages is empty add a message with the info to be inserted, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information about the student should be added into the database if it is not already present: {state['info_to_insert']}"))
    
    messages = []
    messages.extend(state["messages"])

    messages.append(AIMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_insertion_tools.invoke(messages)

    return {"messages": [result]}
