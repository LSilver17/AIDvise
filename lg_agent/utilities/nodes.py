from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
try:
    from .state import AdvisorState
    from .tools import database_query, llm
except ImportError:
    from state import AdvisorState
    from tools import database_query, llm

load_dotenv()

anthr_model = llm.bind_tools([database_query], tool_choice="none")

def advisor_node(state: AdvisorState):
    """Takes the role of an academic advisor, augmented with search tools to deliver information about colleges"""
    new_response = anthr_model.invoke(
                [
                    SystemMessage(
                        """Listen to any questions they have about course requirements, 
                        transfer guidelines, and academic strategies, utilizing the search 
                        tool to take information off of official college websites when necessary. 
                        Responses should be objective and concise. Alert the user when they have 
                        run out of search uses You have access to a database containing 
                        information about courses offered in each term.
                        """)
                ]
                + state["messages"]
            )
    return {
        "messages": new_response,
        "num_calls": state["num_calls"] + 1
    }
