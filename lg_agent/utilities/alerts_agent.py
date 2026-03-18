import sys
sys.path.append("/lg_agent/utilities")

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from utilities.state import AdvisorState
from utilities.schemas import RelevantEventsSchema

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2
)

def filter_relivent_events(events: list, interests: list) -> list:
    """Desides what upcoming events are relivent to user based on intrests."""

    structured_llm = llm.with_structured_output(RelevantEventsSchema)

    system_prompt = ("""You are an assistent made to indentify what upcoming events at a student's college are relivent to their intrests. You will be given a list of events, with pertenent information as well as a list of the student's interests. Decide which events are relevent to the user as well as an urgency level for each event based on how much time/effort it may require and how much time is left before the event occurs. """)

    events_str = ""
    interests_str = ""
    
    for event in events:
        events_str += f"- {event['Name']} (Description: {event['Description']}, "
        events_str += f"Start: {event['StartDate']} {event['StartTime']}, "
        events_str += f"End: {event['EndDate']} {event['EndTime']}, "
        events_str += f"Location: {event['Location']})\n"

    for interest in interests:
        interests_str += f"- {interest}\n"

    input = f"{system_prompt}\n\nUpcoming Events:\n{events_str}\n\nStudent Interests:\n{interests_str}"
    response = structured_llm.invoke(input)

    return response