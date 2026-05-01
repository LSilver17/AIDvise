import sys, os

# Add root directory to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data_pipeline.database.database_dev_tools import __connect

def add_dummy_course_alerts():
    # update status of some course sections. if closed then make reopened, if open or reopened then make closed
    with __connect() as conn:
        cursor = conn.cursor()
        
        # Get course section IDs
        course_sections = cursor.execute("SELECT ID, Status FROM Sections").fetchall()

        for section in course_sections:
            new_status = "Closed" if section['Status'] in ["Open", "Reopened"] else "Reopened"
            cursor.execute("UPDATE Sections SET Status = ? WHERE ID = ?", (new_status, section['ID']))
        
        conn.commit()
        print(f"Updated status for {len(course_sections)} course sections.")


if __name__ == "__main__":
    add_dummy_course_alerts()