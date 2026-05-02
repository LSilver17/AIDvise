import sys, os
    
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
from utilities.schemas import APlanSchema, PlanSchema
from utilities.tools import db_tools, web_tools, insertion_tools, alt_db_tools
from utilities.model_inits import db_llm, planning_llm, web_llm, insertion_llm
import json

load_dotenv()

PROMPT_CONFIG_PATH = os.path.join(root_dir, "prompt_config.json")

with open(PROMPT_CONFIG_PATH, "r") as f:
    PROMPT_CONFIG = json.load(f)

def s_planner_node(state: SPlannerState) -> SPlannerState:
    """Base node for the agent when used by a student, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    state["plan"] = None

    structured_llm = planning_llm.with_structured_output(PlanSchema)

    selected_prompt = PROMPT_CONFIG["s-planner"]["prompt-select"]
    system_prompt = PROMPT_CONFIG["s-planner"]["prompt-options"][selected_prompt]

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
            messages.append(HumanMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(HumanMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    if state["insertion_result"] != "":
        messages.append(HumanMessage(content=f"Result of last insertion attempt: {state['insertion_result']}"))

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def a_planner_node(state: APlannerState) -> APlannerState:
    """Base node for the agent when used by an advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = planning_llm.with_structured_output(APlanSchema)

    selected_prompt = PROMPT_CONFIG["a-planner"]["prompt-select"]
    system_prompt = PROMPT_CONFIG["a-planner"]["prompt-options"][selected_prompt]

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    if "db_info" not in state:
        state["db_info"] = []
    else:
        for QueryResult in state["db_info"]:
                messages.append(HumanMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    if "web_info" not in state:
        state["web_info"] = []
    else:
        for QueryResult in state["web_info"]:
            messages.append(HumanMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def db_node(state: DatabaseHelperState):
    """Node that runs database queries based on the information provided by the planning node."""

    if state["account_type"] == "Student":
        llm_with_db_tools = db_llm.bind_tools(db_tools)
        selected_prompt = PROMPT_CONFIG["s-db"]["prompt-select"]
        system_prompt = PROMPT_CONFIG["s-db"]["prompt-options"][selected_prompt]
    else:
        llm_with_db_tools = db_llm.bind_tools(alt_db_tools)
        selected_prompt = PROMPT_CONFIG["a-db"]["prompt-select"]
        system_prompt = PROMPT_CONFIG["a-db"]["prompt-options"][selected_prompt]
    
    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_db_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def web_node(state: WebSearchHelperState):
    """Node that performs web searches based on the information provided by the planning node."""
    
    llm_with_web_tools = web_llm.bind_tools(web_tools)

    selected_prompt = PROMPT_CONFIG["web"]["prompt-select"]
    system_prompt = PROMPT_CONFIG["web"]["prompt-options"][selected_prompt]

    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the web to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_web_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def insertion_node(state: InsertionHelperState) -> InsertionHelperState:
    """Node that takes any new information the advisor has learned about the student and inserts it into the database."""

    llm_with_insertion_tools = insertion_llm.bind_tools(insertion_tools)

    selected_prompt = PROMPT_CONFIG["insertion"]["prompt-select"]
    system_prompt = PROMPT_CONFIG["insertion"]["prompt-options"][selected_prompt]

    # if state messages is empty add a message with the info to be inserted, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information about the student should be added into the database if it is not already present: {state['info_to_insert']}"))
    
    messages = []
    messages.extend(state["messages"])

    messages.append(HumanMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_insertion_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}
