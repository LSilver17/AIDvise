from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from utilities.state import AdvisorState, DatabaseHelperState, DatabaseHelperOutput, WebSearchHelperState, WebSearchHelperOutput
from utilities.schemas import PlanSchema
from utilities.tools import db_tools

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

db_llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

web_llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2,
)

def planning_node(state: AdvisorState) -> AdvisorState:
    """Base node for the academic advisor, decides whether it needs to use database queries or web search. If not, it answers the question directly using the knolledge it has."""
    
    structured_llm = llm.with_structured_output(PlanSchema)

    system_prompt = "You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Then respond according to the specified schema."

    db_info = "Database information gathered so far: "
    web_info = "Web information gathered so far: "

    if state["db_info"]:
        for qresult in state["db_info"]:
            db_info += f"\nQuery: {qresult['query']}\nResult: {qresult['result']}\n"

    if state["web_info"]:
        for qresult in state["web_info"]:
            web_info += f"\nQuery: {qresult['query']}\nResult: {qresult['result']}\n"            

    messages = []
     
    messages.append(SystemMessage(content=system_prompt))
    messages.append(SystemMessage(content=f"{db_info}\n\n{web_info}"))

    messages.extend(state["messages"])

    response = structured_llm.invoke(messages).model_dump()
    state["plan"] = response
    return state

def db_node(state: DatabaseHelperState) -> DatabaseHelperOutput:
    """Node that runs database queries based on the information provided by the planning node."""

    llm_with_db_tools = db_llm.bind_tools(db_tools)

    system_prompt = "You are the assistant for a student academic advising agent. Your task is to determine how you can use the tools at your disposal to get the information needed to answer the student's question, based on the information provided by the planning node. You should compile the relevant information from the database queries you perform into a clear and concise format that can be used by the answer node to formulate a final answer to the student's question.\nHere are the tools you have at your disposal:"

    for tool in db_tools:
        system_prompt += f"\n\nTool Name: {tool.name}\nDescription: {tool.description}"
    
    input = f"{system_prompt}\n\nThe planning node has determined that the following information is needed from the database to answer the user's question: {state['info_needed']}"

    result = llm_with_db_tools.invoke(input)

    

    return {"info": {"query": state["info_needed"], "result": result}}

def web_node(state: WebSearchHelperState) -> WebSearchHelperOutput:
    """Node that performs web searches based on the information provided by the planning node."""
    # TODO: implement web search node

    return {"info": {"query": state["info_needed"], "result": "Web search results would be here."}}

def answer_node(state: AdvisorState) -> AdvisorState:
    """Node that formulates a final answer based on the information gathered from the planning node, database node, and web node."""

    # Check if the planning node was able to answer the question directly
    if not state["plan"]["requires_database"] and not state["plan"]["requires_web_search"] and state["plan"]["answer"] != "":
        return {"messages": [AIMessage(content=state["plan"]["answer"])]}
    
    # Otherwise formulate an answer based on the information from the database and web nodes

    system_prompt = "You are an academic advisor assistant. Your task is to listen to any questions the user has about course requirements, transfer guidelines, academic strategies, etc. Then respond according to information gathered from database and web searches."

    db_info = "Database information gathered: "
    web_info = "Web information gathered: "

    if len(state["db_info"]) != 0:
        for qresult in state["db_info"]:
            db_info += f"\nQuery: {qresult['query']}\nResult: {qresult['result']}\n"
    
    if len(state["web_info"]) != 0:
        for qresult in state["web_info"]:
            web_info += f"\nQuery: {qresult['query']}\nResult: {qresult['result']}\n"

    messages = []
     
    messages.append(SystemMessage(content=system_prompt))
    messages.append(SystemMessage(content=f"{db_info}\n\n{web_info}"))

    messages.append(state["messages"][-1]) # add the user's original question

    answer = llm.invoke(messages)
    return {"messages": [answer]}
