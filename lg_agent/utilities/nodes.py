from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from .state import AdvisorState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage

load_dotenv()

anthr_model = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature= .2,
    tools= [{
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 3
    }]
)

def advisor_node(state: AdvisorState):
    """Takes the role of an academic advisor, augmented with search tools to deliver information about colleges"""
    new_response = anthr_model.invoke(
                [
                    SystemMessage("""You are taking the role of an academic advisor. Listen to any 
                              questions they have about course requirements, transfer guidelines, 
                              and academic strategies, utilizing the search tool to take information 
                              off of official college websites when necessary. Responses should be
                              objective and concise. Alert the user when they have run out of search
                              uses.""")
                ]
                + state["messages"]
            )
    return {
        "messages": new_response,
        "num_calls": state["num_calls"] + 1
    }