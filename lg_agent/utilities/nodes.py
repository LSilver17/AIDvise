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
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolCall
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from utilities.state import AdvisorState, DatabaseHelperState, WebSearchHelperState, InsertionHelperState
from utilities.schemas import PlanSchema
from utilities.tools import db_tools, web_tools, insertion_tools
from utilities.TestModel import GenericFakeChatModel
import json

load_dotenv()

# TODO: add more models and add the respective api keys to .env
with open(os.path.join(root_dir, "model_select.json"), 'r') as f:
    model_select = json.load(f)
    mode = model_select["mode"]
    match model_select[mode]["planning"]:
        case "sonnet-4-6":
            planning_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=.2)
        case "gpt-4o":
            planning_llm = ChatOpenAI(model="gpt-4o", temperature=.2)
        case "testing":
            planning_llm = GenericFakeChatModel(messages=iter([
                AIMessage(content=json.dumps({
                    "requires_database": True,
                    "requires_web_search": True,
                    "answer": "",
                    "info_needed_db": "Look up the seeded CSC 212 course record, the Artificial Intelligence course record, Spring 2026 course offerings, and the CSC 212 Spring 2026 section taught by Prof. Nguyen.",
                    "info_needed_web": "Check current web results for CSC 212 course requirements and academic planning guidance."
                })),
                AIMessage(content=json.dumps({
                    "requires_database": False,
                    "requires_web_search": False,
                    "answer": "Using the gathered database and web information, the advisor can explain the CSC 212 course details, confirm which Spring 2026 courses are offered, identify the CSC 212 section with Prof. Nguyen, and summarize current web guidance.",
                    "info_needed_db": "",
                    "info_needed_web": ""
                })),
                AIMessage(content=json.dumps({
                    "requires_database": False,
                    "requires_web_search": False,
                    "answer": "Testing fallback: the advisor has enough information to answer without more database or web lookups.",
                    "info_needed_db": "",
                    "info_needed_web": ""
                }))
            ]))
        case default:
            raise ValueError(f"Model {model_select[mode]["planning"]} not supported for planning node.")
    match model_select[mode]["db"]:
        case "sonnet-4-6":
            db_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=.2)
        case "gpt-4o":
            db_llm = ChatOpenAI(model="gpt-4o", temperature=.2)
        case "testing":
            db_llm = GenericFakeChatModel(messages=iter([
                AIMessage(content="testing all db tools", tool_calls=[
                    ToolCall(name="course_query_by_code", args={"course_code": "CSC 212"}, id="1"),
                    ToolCall(name="course_query_by_title", args={"course_title": "Artificial Intelligence"}, id="2"),
                    ToolCall(name="course_filter", args={"filters": {"terms": [{"year": 2026, "season": "Spring", "number": None}, {"year": 2026, "season": "Fall", "number": None}], "departments": ["CSC", "MTH"], "credits": {"condition": ">=", "credits": 3}}}, id="3"),
                    ToolCall(name="section_filter", args={"filters": {"terms": [{"year": 2026, "season": "Spring", "number": None}], "course_codes": ["CSC 212"], "instructors": ["Prof. Nguyen"], "locations": ["Tech Building 115"]}}, id="4")
                ]),
                AIMessage(content="Database tools completed. CSC 212, Artificial Intelligence, Spring 2026 offerings, and the CSC 212 section information have all been retrieved successfully."),
                AIMessage(content="Database tools fallback. No additional database work is needed for this test run.")
            ]))
        case default:
            raise ValueError(f"Model {model_select[mode]["db"]} not supported for db node.")
    match model_select[mode]["web"]:
        case "sonnet-4-6":
            web_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=.2)
        case "gpt-4o":
            web_llm = ChatOpenAI(model="gpt-4o", temperature=.2)
        case "testing":
            web_llm = GenericFakeChatModel(messages=iter([
                AIMessage(content="testing web search", tool_calls=[
                    ToolCall(name="web_search", args={"query": "CSC 212 course requirements and academic planning guidance"}, id="1")
                ]),
                AIMessage(content="Web search completed. The returned results can be used to confirm current guidance for CSC 212 and related academic planning questions."),
                AIMessage(content="Web search fallback. No additional web search is needed for this test run.")
            ]))
        case default:
            raise ValueError(f"Model {model_select[mode]["web"]} not supported for web node.")
    match model_select[mode]["insertion"]:
        case "sonnet-4-6":
            insertion_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=.2)
        case "gpt-4o":
            insertion_llm = ChatOpenAI(model="gpt-4o", temperature=.2)
        case "testing":
            insertion_llm = GenericFakeChatModel(messages=iter([
                AIMessage(content="testing insertion tools", tool_calls=[
                    ToolCall(name="insert_student_interest", args={"interest": "Machine Learning"}, id="1"),
                    ToolCall(name="insert_student_tracked_section", args={"course_code": "CSC 212", "section_id": "1"}, id="2")
                ]),
                AIMessage(content="Insertion tools completed. The student's interest in Machine Learning has been added to the database."),
                AIMessage(content="Insertion tools fallback. No additional insertion is needed for this test run.")
            ])),
        case default:
            raise ValueError(f"Model {model_select[mode]["insertion"]} not supported for insertion node.")

def planning_node(state: AdvisorState) -> AdvisorState:
    """Base node for the academic advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = planning_llm.with_structured_output(PlanSchema)

    system_prompt = f"You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Respond according to the specified schema. If you can answer the user's question using informationed previously gathered, leave the appropriate fields blank, even if the answer pertains to the database or web. If loop count is 3 or higher and you still don't have the information needed, provide the best answer you can with the information you have and stop. In addition to answering questions, you should also listen to anything the user says about their interests and goals and use that information to update the database."

    messages = []
    messages.extend(state["messages"])

    if len(messages) == 0:
        messages.append(SystemMessage(content=system_prompt))

    for QueryResult in state["db_info"]:
        messages.append(SystemMessage(content=f"Database Query: {QueryResult['query']}\nDatabase Result: {QueryResult['result']}"))
    for QueryResult in state["web_info"]:
        messages.append(SystemMessage(content=f"Web Search Query: {QueryResult['query']}\nWeb Search Result: {QueryResult['result']}"))

    messages.append(SystemMessage(content="Current loop count: " + str(state["loop_count"])))

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    state["loop_count"] += 1
    return state

def db_node(state: DatabaseHelperState):
    """Node that runs database queries based on the information provided by the planning node."""

    llm_with_db_tools = db_llm.bind_tools(db_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use the tools at your disposal to get the information it needs. Only output this information and nothing else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop."
    
    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(SystemMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_db_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def web_node(state: WebSearchHelperState):
    """Node that performs web searches based on the information provided by the planning node."""
    
    llm_with_web_tools = web_llm.bind_tools(web_tools)

    system_prompt = f"You are the assistant for a student academic advising agent. Your task is to determine how you can use web searches to get the information it needs. Only output this information and nothing else. If loop count is 3 or higher and you still don't have the information needed, output what you have and stop."

    # if state messages is empty add a message with the info needed, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information is needed from the web to answer the user's question: {state['info_needed']}"))

    messages = []
    messages.extend(state["messages"])

    messages.append(SystemMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_web_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}

def insertion_node(state: InsertionHelperState) -> InsertionHelperState:
    """Node that takes any new information the advisor has learned about the student and inserts it into the database."""

    llm_with_insertion_tools = db_llm.bind_tools(insertion_tools)

    system_prompt = f"You are the assistant for an academic advising agent. Your task is to determine how you can use the following tools to update the database with any new information the advisor has learned about the student from their conversations and questions. If the information is already in the database, do not insert it again. Only output the tool calls and nothing else. If loop count is 3 or higher and you still have information that hasn't been inserted, leave it as is and stop."

    # if state messages is empty add a message with the info to be inserted, otherwise pass the messages through
    if len(state["messages"]) == 0:
        state["messages"].append(SystemMessage(content=system_prompt))
        state["messages"].append(HumanMessage(content=f"The planning node has determined that the following information about the student should be added into the database if it is not already present: {state['info_to_insert']}"))
    
    messages = []
    messages.extend(state["messages"])

    messages.append(SystemMessage(content="Current loop count: " + str(state["loop_count"])))

    result = llm_with_insertion_tools.invoke(messages)

    state["loop_count"] += 1
    return {"messages": [result]}
