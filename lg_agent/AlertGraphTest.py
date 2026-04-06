import os, sys

path_to_database_tools = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_pipeline', 'database'))
if path_to_database_tools not in sys.path:
    sys.path.append(path_to_database_tools)

path_to_lg_agent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if path_to_lg_agent not in sys.path:
    sys.path.append(path_to_lg_agent)

from data_pipeline.database.InterestDummies import reset
from lg_agent import alert_constr

# Remember to switch alert_nodes DATABASE to AlertTestDB.db before running this test, and switch it back to AdvisorDB.db after testing.
if __name__ == "__main__":
    reset()
    alert_constr.graph.invoke({"student_id": 1,})
    print("Check db for relevant events")
