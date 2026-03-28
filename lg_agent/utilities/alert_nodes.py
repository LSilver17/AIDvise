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
from utilities.state import AlertsAgentState
import sqlite3
from datetime import datetime

load_dotenv()

database = "AdvisorDB.db"

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=.2
)

# Updates the agent's state with new events from the database since the last check.
def get_new_events(state: AlertsAgentState) -> AlertsAgentState:
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

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

        # Query for new events since last check, sorted by start date
        cursor.execute(
            '''
            SELECT ID, Name, Description, StartDate, EndDate, StartTime, EndTime, Location
            FROM Events
            WHERE StartDate >= DATE('now') AND AddedTimeStamp > ?
            ORDER BY StartDate ASC
            ''',
            (last_event_check,)
        )

        # Fetch all results
        events = [dict(ID=row[0], Name=row[1], Description=row[2], StartDate=row[3], EndDate=row[4], StartTime=row[5], EndTime=row[6], Location=row[7]) for row in cursor.fetchall()]

        state["upcoming_events"] = events
        return state

    except Exception as exc:
        raise RuntimeError("Failed to fetch upcoming events.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Updates the agent's state with the student's interests
def get_interests(state: AlertsAgentState) -> AlertsAgentState:
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Query for the student's interests
        cursor.execute(
            '''
            SELECT Interest
            FROM Interests
            WHERE StudentID = ?
            ''',
            (state["student_id"],)
        )

        # Fetch all results
        interests = [row[0] for row in cursor.fetchall()]

        state["student_interests"] = interests
        return state

    except Exception as exc:
        raise RuntimeError("Failed to fetch student interests.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

# Desides what upcoming events are relivent to user based on intrests.
def filter_relivent_events(state: AlertsAgentState) -> AlertsAgentState:
    structured_llm = llm.with_structured_output(RelevantEventsSchema)

    system_prompt = ("""You are an assistent made to indentify what upcoming events at a student's college are relivent to their intrests. You will be given a list of events, with pertenent information as well as a list of the student's interests. Decide which events are relevent to the user as well as an urgency level for each event based on how much time/effort it may require and how much time is left before the event occurs. """)

    events_str = ""
    interests_str = ""
    
    for event in state["upcoming_events"]:
        events_str += f"- {event['Name']} (Description: {event['Description']}, "
        events_str += f"Start: {event['StartDate']} {event['StartTime']}, "
        events_str += f"End: {event['EndDate']} {event['EndTime']}, "
        events_str += f"Location: {event['Location']})\n"

    for interest in state["student_interests"]:
        interests_str += f"- {interest}\n"

    input = f"{system_prompt}\n\nUpcoming Events:\n{events_str}\n\nStudent Interests:\n{interests_str}"
    response = structured_llm.invoke(input)

    state["relevant_events"] = response
    return state

# Inserts relevant events for a student into the database
def insert_relevant_events(state: AlertsAgentState):
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect(database)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Insert relevant events into database
        for event in state["relevant_events"]:
            # Get event ID from event name and start date
            cursor.execute(
                '''
                SELECT ID
                FROM Events
                WHERE Name = ? AND StartDate = ?
                ''',
                (event['Name'], event['StartDate'])
            )
            eventID = cursor.fetchone()

            if eventID:
                cursor.execute(
                    '''
                    INSERT INTO RelevantEvents (StudentID, EventID, Urgency)
                    VALUES (?, ?, ?)
                    ''',
                    (state["student_id"], eventID[0], event['Urgency'])
                )

        # Commit changes to the database
        conn.commit()

    except Exception as exc:
        raise RuntimeError("Failed to insert relevant events.") from exc
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
