import sys, os

# adds database directory to system path if not already there
database_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
if database_dir not in sys.path:
    sys.path.append(database_dir)
    
# adds lg_agent directory to system path if not already there
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from data_pipeline.database.InterestDummies import reset
import alert_constr

# Remember to switch alert_nodes DATABASE to AlertTestDB.db before running this test, and switch it back to AdvisorDB.db after testing.
if __name__ == "__main__":
    reset()
    alert_constr.graph.invoke({"student_id": 1,})
    print("Check db for relevant events")
