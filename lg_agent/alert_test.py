import sys
sys.path.append("/lg_agent/utilities")

from dotenv import load_dotenv
from utilities.alerts_agent import filter_relivent_events
from utilities.alerts_utils import get_events, get_interests

load_dotenv()

events = get_events()
interests = get_interests("2")
filtered_events = filter_relivent_events(events, interests)
print("Filtered Events:\n" + str(filtered_events))
