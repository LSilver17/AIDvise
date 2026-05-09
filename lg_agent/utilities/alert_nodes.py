import sys, os
    
# adds root directory to system path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# adds utilities directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from utilities.schemas import RelevantEventsSchema
from utilities.state import AlertsAgentState, AlertsAgentOutput
from utilities.model_inits import alerts_llm
from data_pipeline.database.database_dev_tools import __connect
from datetime import datetime

load_dotenv()

def get_new_events(state: AlertsAgentState) -> AlertsAgentState:
    """
    Retrieves new events from the database since the last check and updates agent state.
    
    This function queries the database for events that were added since the student's last
    event check, filtering for events that are upcoming (future dates or today with future times).
    It also updates the LastEventCheck timestamp in the database to the current time.
    
    Args:
        state (AlertsAgentState): The current state of the alerts agent containing the student_id.
            Expected to have the key 'student_id' with an integer student ID.
    
    Returns:
        AlertsAgentState: Updated state dictionary with 'upcoming_events' key containing a list
            of event dictionaries. Each event dict has:
            - 'ID': Event identifier
            - 'Name': Event name
            - 'Description': Event description
            - 'Dates': List of date dictionaries with Date, StartTime, EndTime, Location, TimeAdded
    
    Raises:
        sqlite3.DatabaseError: If there's an issue connecting to or querying the database.
    
    Side Effects:
        - Updates the 'LastEventCheck' timestamp for the student in the database.
    """
    with __connect() as conn:
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

def get_interests(state: AlertsAgentState) -> AlertsAgentState:
    """
    Retrieves the student's interests from the database and updates agent state.
    
    Queries the database to fetch all interests associated with a specific student,
    enabling the agent to personalize event filtering based on what the student cares about.
    
    Args:
        state (AlertsAgentState): The current state of the alerts agent containing the student_id.
            Expected to have the key 'student_id' with an integer student ID.
    
    Returns:
        AlertsAgentState: Dictionary with 'student_interests' key containing a list of interest
            strings (e.g., ['sports', 'music', 'technology']). Empty list if no interests found.
    
    Raises:
        sqlite3.DatabaseError: If there's an issue connecting to or querying the database.
    """
    with __connect() as conn:
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

def filter_relivent_events(state: AlertsAgentState) -> AlertsAgentState:
    """
    Uses LLM to filter events relevant to the student's interests and assess urgency.
    
    Leverages an LLM model to intelligently match upcoming events against
    the student's interests. For each matching event, assigns an urgency level based on the
    time/effort required and time remaining until the event.
    
    Args:
        state (AlertsAgentState): The current state containing:
            - 'upcoming_events': List of event dictionaries with ID, Name, Description, and Dates
            - 'student_interests': List of interest strings
    
    Returns:
        AlertsAgentState: Dictionary with 'relevant_events' key containing a list of event
            dictionaries marked as relevant. Each dict includes:
            - 'ID': Event identifier
            - 'Urgency': Urgency level (int from 1 to 5, with 5 being most urgent)
    
    Raises:
        ValueError: If LLM response cannot be parsed into RelevantEventsSchema.
    
    Note:
        - Returns empty list if no relevant events found or if LLM response is None
        - Uses system prompt to guide LLM decision-making
        - Response is parsed via structured output into RelevantEventsSchema
    """
    structured_llm = alerts_llm.with_structured_output(RelevantEventsSchema)

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

def insert_relevant_events(state: AlertsAgentState) -> AlertsAgentOutput:
    """
    Persists relevant events to the database and returns the formatted output.
    
    Inserts all events identified as relevant (from the filtering step) into the
    RelevantEvents table in the database, associating them with the student and
    their assigned urgency levels.
    
    Args:
        state (AlertsAgentState): The current state containing:
            - 'student_id': Integer ID of the student
            - 'relevant_events': List of event dicts with 'ID' and 'Urgency' keys
    
    Returns:
        AlertsAgentOutput: Dictionary with 'relevant_events' key containing the list of
            events that were inserted into the database.
    
    Raises:
        sqlite3.DatabaseError: If database insertion fails.
    
    Side Effects:
        - Inserts rows into the RelevantEvents table in the database
        - Commits transaction to persist changes
    """
    with __connect() as conn:
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
