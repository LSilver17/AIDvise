import sys, os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data_pipeline.database.database_dev_tools import __connect
from lg_agent.database_utils import get_courseID_by_code

STUDENT_ID   = 100006
STUDENT_NAME = "Riley Parker"
CUMULATIVE_GPA    = 3.19
TOTAL_CREDITS_EARNED = 31
INTENDED_GRADUATION  = "Spring 2027"

# Completed courses only (Semesters 1 & 2); Semester 3 is Registered/In-Progress
COMPLETED_COURSES = [
    # Semester 1 – Fall 2025
    "CSC 108",  # Computer Science I
    "ENG 101",  # Composition I
    "MAT 233",  # Calculus I
    "BIO 101",  # General Biology I
    "SDV 101",  # Student Success Seminar
    # Semester 2 – Spring 2026
    "CSC 109",  # Computer Science II
    "ENG 102",  # Composition II
    "PHY 201",  # College Physics I
    "SPH 101",  # Speech Communication Skills
]


def insert_riley_parker_transcript() -> None:
    with __connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO Students (ID, Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID, ParentID)
            VALUES (?, ?, ?, ?, ?, NULL, NULL)
            """,
            (STUDENT_ID, STUDENT_NAME, CUMULATIVE_GPA, TOTAL_CREDITS_EARNED, INTENDED_GRADUATION),
        )

        cursor.execute(
            """
            UPDATE Students
            SET GPA = ?, CreditsEarned = ?, IntendedGraduationTerm = ?
            WHERE ID = ?
            """,
            (CUMULATIVE_GPA, TOTAL_CREDITS_EARNED, INTENDED_GRADUATION, STUDENT_ID),
        )

        added = 0
        for course_code in COMPLETED_COURSES:
            course_id = get_courseID_by_code(cursor, course_code)
            if course_id:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO CoursesTaken (CourseID, ParentID)
                    VALUES (?, ?)
                    """,
                    (course_id, STUDENT_ID),
                )
                added += 1
            else:
                print(f"Warning: Course '{course_code}' not found in Courses table — skipping.")

        conn.commit()
        print(f"Transcript inserted for {STUDENT_NAME}: {added} courses added, GPA={CUMULATIVE_GPA}, CreditsEarned={TOTAL_CREDITS_EARNED}.")


if __name__ == "__main__":
    insert_riley_parker_transcript()
