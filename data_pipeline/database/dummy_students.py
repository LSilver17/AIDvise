"""
Utility module to populate the Students and Advisors tables with realistic dummy data.
Includes associated entries for StudentProgramsOfStudy and CoursesTaken tables.
"""

import os, sys

# Add root directory to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data_pipeline.database.database_dev_tools import __connect
from lg_agent.database_utils import get_courseID_by_code

def add_dummy_advisors():
    """Add dummy advisor entries to the Advisors table (without User accounts)."""
    advisors = [
        ("Dr. Sarah Mitchell", "Computer Science & Mathematics"),
        ("Prof. James Rodriguez", "Business & Accounting"),
        ("Dr. Emily Chen", "Engineering & Technology"),
    ]
    
    with __connect() as conn:
        cursor = conn.cursor()
        
        advisor_ids = []
        for name, specialty in advisors:
            cursor.execute(
                '''INSERT INTO Advisors (Name, ParentID)
                   VALUES (?, NULL)''',
                (name,)
            )
            advisor_ids.append(cursor.lastrowid)
        
        conn.commit()
        print(f"Added {len(advisors)} dummy advisors.")
        return advisor_ids


def add_dummy_students():
    """Add dummy student entries with realistic GPAs, credits earned, and intended graduation terms."""
    
    with __connect() as conn:
        cursor = conn.cursor()
        
        # Get advisor IDs
        advisors = cursor.execute("SELECT ID FROM Advisors LIMIT 3").fetchall()
        advisor_ids = [a['ID'] for a in advisors] if advisors else [None, None, None]
        
        # Pad if not enough advisors
        while len(advisor_ids) < 3:
            advisor_ids.append(None)
        
        students = [
            {
                "id": 100001,
                "name": "Alex Johnson",
                "gpa": 3.7,
                "credits_earned": 0,
                "intended_graduation": "Spring 2027",
                "advisor_id": advisor_ids[0],
            },
            {
                "id": 100002,
                "name": "Jordan Martinez",
                "gpa": 3.4,
                "credits_earned": 0,
                "intended_graduation": "Fall 2026",
                "advisor_id": advisor_ids[1],
            },
            {
                "id": 100003,
                "name": "Casey Thompson",
                "gpa": 3.9,
                "credits_earned": 0,
                "intended_graduation": "Spring 2026",
                "advisor_id": advisor_ids[2],
            },
            {
                "id": 100004,
                "name": "Morgan Lee",
                "gpa": 3.2,
                "credits_earned": 0,
                "intended_graduation": "Fall 2027",
                "advisor_id": advisor_ids[0],
            },
            {
                "id": 100005,
                "name": "Taylor Chen",
                "gpa": 3.6,
                "credits_earned": 0,
                "intended_graduation": "Summer 2026",
                "advisor_id": advisor_ids[1],
            },
            {
                "id": 100006,
                "name": "Riley Parker",
                "gpa": 3.3,
                "credits_earned": 0,
                "intended_graduation": "Spring 2027",
                "advisor_id": advisor_ids[2],
            },
        ]
        
        for student in students:
            cursor.execute(
                '''INSERT INTO Students (ID, Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID, ParentID)
                   VALUES (?, ?, ?, ?, ?, ?, NULL)''',
                (
                    student["id"],
                    student["name"],
                    student["gpa"],
                    student["credits_earned"],
                    student["intended_graduation"],
                    student["advisor_id"],
                )
            )
        
        conn.commit()
        print(f"Added {len(students)} dummy students.")
        return students


def add_student_programs():
    """Link students to their programs of study."""
    
    with __connect() as conn:
        cursor = conn.cursor()
        
        # Define student-to-program mappings
        student_programs = {
            100001: ["Accounting Certificate"],
            100002: ["Accounting Certificate"],
            100003: ["Business Administration Career"],
            100004: ["Computer Science Transfer"],
            100005: ["Computer Science Transfer"],
            100006: ["Electronics Engineering Technology - Biomedical Instrumentation Option"],
        }
        
        added = 0
        for student_id, program_names in student_programs.items():
            for program_name in program_names:
                # Get program ID by name
                program = cursor.execute(
                    "SELECT ID FROM ProgramsOfStudy WHERE Title = ?",
                    (program_name,)
                ).fetchone()
                
                if program:
                    cursor.execute(
                        '''INSERT INTO StudentProgramsOfStudy (ProgramID, ParentID)
                           VALUES (?, ?)''',
                        (program['ID'], student_id)
                    )
                    added += 1
                else:
                    print(f"Warning: Program '{program_name}' not found in database.")
        
        conn.commit()
        print(f"Added {added} student-to-program associations.")


def add_courses_taken():
    """Link students to courses they have taken, making realistic combinations."""
    
    with __connect() as conn:
        cursor = conn.cursor()
        
        # Define realistic course progressions for different majors using codes present in course_catalog.json
        student_courses = {
            100001: ["ACC 101", "CIS 111", "ENG 101", "MAT 051", "MGT 101"],
            100002: ["ACC 101", "ACC 102", "CIS 111", "ENG 101", "ECO 215", "MGT 101", "MGT 211"],
            100003: ["ACC 101", "ACC 102", "CIS 111", "ENG 101", "ECO 215", "ECO 216", "MGT 101", "MGT 211", "MGT 215", "MGT 216"],
            100004: ["CSC 101", "CSC 105", "CIS 111", "ENG 101", "MAT 051", "MAT 052"],
            100005: ["CSC 101", "CSC 105", "CSC 108", "CSC 140", "CSC 141", "CSC 201", "CIS 105", "CIS 111", "ENG 101", "MAT 051", "MAT 052", "PHY 101"],
            100006: ["ELT 103", "ELT 104", "ELT 121", "ELT 130", "ELM 251", "ELM 257", "ELM 258", "ELM 260", "CPS 298", "ENG 101", "MAT 051", "PHY 101"],
        }
        
        added = 0
        for student_id, courses in student_courses.items():
            for course_code in courses:
                course_id = get_courseID_by_code(cursor, course_code)
                
                if course_id:
                    cursor.execute(
                        '''INSERT INTO CoursesTaken (CourseID, ParentID)
                           VALUES (?, ?)''',
                        (course_id, student_id)
                    )
                    added += 1
                else:
                    print(f"Warning: Course '{course_code}' not found in database for student {student_id}.")

        # Keep Students.CreditsEarned consistent with inserted CoursesTaken rows.
        for student_id in student_courses.keys():
            total_credits = cursor.execute(
                '''
                SELECT COALESCE(SUM(COALESCE(c.Credits, 0)), 0) AS TotalCredits
                FROM CoursesTaken ct
                JOIN Courses c ON c.ID = ct.CourseID
                WHERE ct.ParentID = ?
                ''',
                (student_id,)
            ).fetchone()['TotalCredits']

            cursor.execute(
                '''UPDATE Students
                   SET CreditsEarned = ?
                   WHERE ID = ?''',
                (int(total_credits), student_id)
            )
        
        conn.commit()
        print(f"Added {added} course-to-student associations.")


def populate_dummy_data():
    """Main function to populate all dummy student and advisor data."""
    try:
        print("\n--- Populating Dummy Student and Advisor Data ---")
        add_dummy_advisors()
        add_dummy_students()
        add_student_programs()
        add_courses_taken()
        print("--- Dummy data population complete! ---\n")
    except Exception as e:
        print(f"Error populating dummy data: {e}")
        raise


if __name__ == '__main__':
    populate_dummy_data()
