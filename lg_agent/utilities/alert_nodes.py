import sys, os
    
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits import create_sql_agent
from utilities.schemas import RelevantEventsSchema
from utilities.state import AlertsAgentInput, AlertsAgentState, AlertsAgentOutput
from datetime import datetime
import sqlite3

load_dotenv()

DATABASE = "AdvisorDB.db"

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2
)

# Updates the agent's state with new events from the database since the last check.
def get_new_events(state: AlertsAgentState) -> AlertsAgentState:
    with sqlite3.connect(DATABASE) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Get last event check time from database
        cursor.execute(
            '''
            SELECT LastEventCheck
            FROM Students
            WHERE ID = ?
            ''',
            (state["student_id"],)
        )
        last_event_check = cursor.fetchone()[0]

        # Update last event check time in database to now
        now = datetime.now().isoformat()
        cursor.execute(
            '''
            UPDATE Students
            SET LastEventCheck = ?
            WHERE ID = ?
            ''',
            (now, state["student_id"])
        )
        conn.commit()

        # Query for new event dates since last check
        cursor.execute(
            '''
            SELECT e.ID, e.Name, e.Description, ed.Date, ed.StartTime, ed.EndTime, ed.Location, ed.TimeAdded
            FROM Events e
            JOIN EventDates ed ON e.ID = ed.ParentID
            WHERE TimeAdded > ? AND (ed.Date > date('now') OR (ed.Date = date('now') AND ed.EndTime > time('now')))
            ''',
            (last_event_check,)
        )
        event_dates = cursor.fetchall()

        if not event_dates:
            print("No new events found in database since last check.")
            return {"upcoming_events": []}

        # Reorganize the results into a list where each event is a dictionary containing its name, description, and a list of its event dates where each date is a dictionary of its own info
        events = []
        for row in event_dates:
            event = next((e for e in events if e["ID"] == row[0]), None)
            if not event:
                event = dict(ID=row[0], Name=row[1], Description=row[2], Dates=[])
                events.append(event)
            event["Dates"].append(dict(Date=row[3], StartTime=row[4], EndTime=row[5], Location=row[6], TimeAdded=row[7]))

    print("Fetched new events from database:", events)
    return {"upcoming_events": events}

# Updates the agent's state with the student's interests
def get_interests(state: AlertsAgentState) -> AlertsAgentState:
    with sqlite3.connect(DATABASE) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for the student's interests
        cursor.execute(
            '''
            SELECT Interest
            FROM Interests
            WHERE ParentID = ?
            ''',
            (state["student_id"],)
        )

        # Fetch all results
        interests = [row[0] for row in cursor.fetchall()]
    
    print("Fetched interests from database:", interests)
    return {"student_interests": interests}

# Desides what upcoming events are relivent to user based on intrests.
def filter_relivent_events(state: AlertsAgentState) -> AlertsAgentState:
    structured_llm = llm.with_structured_output(RelevantEventsSchema)

    system_prompt = ("""You are an assistent made to indentify what upcoming events at a student's college are relivent to their intrests. You will be given a list of events, with pertenent information as well as a list of the student's interests. Decide which events are relevent to the user as well as an urgency level for each event based on how much time/effort it may require and how much time is left before the event occurs. """)

    events_str = ""
    interests_str = ""
    
    for event in state["upcoming_events"]:
        events_str += f"- ID: {event['ID']}, Name: {event['Name']}, Description: {event['Description']}\n"
        for date in event["Dates"]:
            events_str += f"  - Date: {date['Date']}, Start Time: {date['StartTime']}, End Time: {date['EndTime']}, Location: {date['Location']}\n"

    for interest in state["student_interests"]:
        interests_str += f"- {interest}\n"

    input = f"{system_prompt}\n\nUpcoming Events:\n{events_str}\n\nStudent Interests:\n{interests_str}"
    response = structured_llm.invoke(input)

    print("LLM response:", response.model_dump() if response else "No response")
    return {"relevant_events": response.model_dump()["relivent_events"] if response else []}

# Inserts relevant events for a student into the database
def insert_relevant_events(state: AlertsAgentState) -> AlertsAgentOutput:
    with sqlite3.connect(DATABASE) as conn:
        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Insert relevant events into database
        for event in state["relevant_events"]:
            cursor.execute(
                '''
                INSERT INTO RelevantEvents (ParentID, EventID, Urgency)
                VALUES (?, ?, ?)
                ''',
                (state["student_id"], event["ID"], event["Urgency"])
            )
        conn.commit()

    return {"relevant_events": state["relevant_events"]}
