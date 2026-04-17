import sys, os

# adds database directory to system path if not already there
database_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if database_dir not in sys.path:
    sys.path.append(database_dir)

import sqlite3
from datetime import datetime, timedelta
from database.database_dev_tools import __connect, setup_database

def _clear_existing_data(cursor: sqlite3.Cursor) -> None:
    """Clear all existing data in child-to-parent delete order to satisfy foreign keys."""
    delete_order = [
        "TrackedSections",
        "StudentSectionStatusChanges",
        "RelevantEvents",
        "ChatLogs",
        "CoursesTaken",
        "StudentProgramsOfStudy",
        "Interests",
        "Students",
        "Advisors",
        "MeetTimes",
        "Sections",
        "CoursesOffered",
        "ProgramRequiredCourseOptions",
        "ProgramRequiredCourses",
        "EventDates",
        "Events",
        "Terms",
        "ProgramsOfStudy",
        "Courses",
    ]
    for table in delete_order:
        cursor.execute(f"DELETE FROM {table}")

def seed_comprehensive_data(reset_existing: bool = True) -> None:
    """Seed database with comprehensive, diverse dummy data."""
    with __connect() as conn:
        cursor = conn.cursor()
        
        # Ensure database is set up
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Courses'")
        if not cursor.fetchone():
            setup_database()
        
        if reset_existing:
            _clear_existing_data(cursor)

        # ==================== 1) COMPREHENSIVE COURSE CATALOG ====================
        courses = [
            # Computer Science
            ("CSC", 101, "Intro to Programming", "Fundamentals of programming with Python.", 3, "None"),
            ("CSC", 110, "Web Development Basics", "HTML, CSS, and JavaScript fundamentals.", 3, "None"),
            ("CSC", 150, "Intro to Cybersecurity", "Overview of cybersecurity principles and threats.", 3, "None"),
            ("CSC", 200, "Data Structures", "Arrays, linked lists, stacks, queues, and trees.", 3, "CSC 101"),
            ("CSC", 212, "Data Structures and Algorithms", "Advanced algorithms and complexity analysis.", 3, "CSC 200"),
            ("CSC", 220, "Object-Oriented Programming", "Design patterns and OOP principles in Java.", 3, "CSC 101"),
            ("CSC", 251, "Computer Organization", "Assembly language and machine architecture.", 3, "CSC 101"),
            ("CSC", 310, "Database Systems", "Relational models, SQL, and schema design.", 3, "CSC 212"),
            ("CSC", 340, "Artificial Intelligence", "Foundational AI topics and search techniques.", 3, "CSC 212"),
            ("CSC", 350, "Operating Systems", "Process management, memory, and file systems.", 3, "CSC 251"),
            ("CSC", 380, "Web Applications", "Full-stack web development with frameworks.", 3, "CSC 110; CSC 220"),
            ("CSC", 420, "Machine Learning", "Supervised and unsupervised learning algorithms.", 3, "CSC 340"),
            
            # Mathematics
            ("MTH", 101, "College Algebra", "Equations, functions, and polynomial algebra.", 4, "None"),
            ("MTH", 102, "Trigonometry", "Trigonometric functions and identities.", 3, "MTH 101"),
            ("MTH", 125, "Calculus I", "Limits, derivatives, and basic integration.", 4, "MTH 102"),
            ("MTH", 126, "Calculus II", "Integration techniques and applications.", 4, "MTH 125"),
            ("MTH", 201, "Linear Algebra", "Matrices, vectors, and eigenvalues.", 3, "MTH 101"),
            ("MTH", 231, "Discrete Mathematics", "Logic, proofs, sets, relations, and combinatorics.", 3, "MTH 101"),
            ("MTH", 301, "Differential Equations", "Solving and applications of differential equations.", 4, "MTH 126"),
            ("MTH", 310, "Probability and Statistics", "Distributions, hypothesis testing, and inference.", 3, "MTH 125"),
            ("MTH", 250, "Abstract Algebra", "Groups, rings, and fields.", 3, "MTH 201"),
            
            # English
            ("ENG", 101, "English Composition I", "Academic writing and essay structure.", 3, "None"),
            ("ENG", 102, "English Composition II", "Advanced writing and research papers.", 3, "ENG 101"),
            ("ENG", 201, "Literature and Analysis", "Fiction, poetry, and literary criticism.", 3, "ENG 101"),
            ("ENG", 250, "Technical Writing", "Documentation and technical communication.", 3, "ENG 101"),
            
            # Natural Sciences
            ("BIO", 101, "General Biology I", "Cell structure, genetics, and evolution.", 4, "None"),
            ("BIO", 102, "General Biology II", "Ecology and organism biology.", 4, "BIO 101"),
            ("BIO", 201, "Human Anatomy", "Structure of human body systems.", 4, "BIO 101"),
            ("CHM", 101, "General Chemistry I", "Atoms, bonding, and reactions.", 4, "None"),
            ("CHM", 102, "General Chemistry II", "Thermodynamics and equilibrium.", 4, "CHM 101"),
            ("PHY", 101, "Physics I", "Mechanics and waves.", 4, "MTH 125"),
            ("PHY", 102, "Physics II", "Electricity, magnetism, and optics.", 4, "PHY 101; MTH 125"),
            
            # Business
            ("BUS", 101, "Introduction to Business", "Business fundamentals and organization.", 3, "None"),
            ("BUS", 201, "Business Ethics", "Ethical issues in organizational context.", 3, "None"),
            ("BUS", 210, "Accounting I", "Financial accounting principles.", 3, "None"),
            ("BUS", 220, "Management", "Planning, organizing, and leadership.", 3, "BUS 101"),
            ("BUS", 250, "Marketing Fundamentals", "Market segmentation and strategy.", 3, "BUS 101"),
        ]
        cursor.executemany(
            """
            INSERT INTO Courses (Department, Code, Name, Description, Credits, Requirements)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            courses,
        )

        course_id_by_name = {
            row[0]: row[1]
            for row in cursor.execute("SELECT Name, ID FROM Courses").fetchall()
        }

        # ==================== 2) COMPREHENSIVE PROGRAMS ====================
        program_rows = [
            ("Computer Science", "Study in software development, systems, and theory.", 60, "Associate in Science"),
            ("Software Engineering", "Focus on industrial-strength software practices.", 60, "Associate in Science"),
            ("Cybersecurity", "Specialized study in information security.", 54, "Associate in Science"),
            ("Data Science", "Analytics, machine learning, and data engineering.", 54, "Associate in Science"),
            ("Mathematics", "Pure and applied mathematics with proof writing.", 54, "Associate in Science"),
            ("Information Technology", "IT infrastructure and network management.", 51, "Associate in Applied Science"),
            ("Business Administration", "General business management and operations.", 60, "Associate in Science"),
            ("Biology", "Life sciences and organismal biology.", 60, "Associate in Science"),
            ("Chemistry", "Inorganic and organic chemistry.", 60, "Associate in Science"),
            ("Physics", "Classical and modern physics.", 60, "Associate in Science"),
        ]
        cursor.executemany(
            """
            INSERT INTO ProgramsOfStudy (Title, Description, CreditsRequired, Type)
            VALUES (?, ?, ?, ?)
            """,
            program_rows,
        )

        program_id_by_title = {
            row[0]: row[1]
            for row in cursor.execute("SELECT Title, ID FROM ProgramsOfStudy").fetchall()
        }

        # ==================== 3) PROGRAM REQUIRED COURSES ====================
        requirement_groups = {
            "Computer Science": [
                ["Intro to Programming"],
                ["Data Structures and Algorithms"],
                ["Computer Organization"],
                ["Discrete Mathematics"],
                ["Calculus I"],
                ["Database Systems", "Artificial Intelligence"],
                ["Object-Oriented Programming"],
                ["Object-Oriented Programming", "Web Applications"],
            ],
            "Software Engineering": [
                ["Intro to Programming"],
                ["Object-Oriented Programming"],
                ["Data Structures and Algorithms"],
                ["Web Applications"],
                ["Database Systems"],
                ["Calculus I"],
                ["Operating Systems"],
            ],
            "Cybersecurity": [
                ["Intro to Cybersecurity"],
                ["Intro to Programming"],
                ["Computer Organization"],
                ["Database Systems"],
                ["Operating Systems"],
                ["Discrete Mathematics"],
            ],
            "Data Science": [
                ["Intro to Programming"],
                ["Data Structures and Algorithms"],
                ["Probability and Statistics"],
                ["Linear Algebra"],
                ["Calculus I"],
                ["Machine Learning"],
                ["Database Systems"],
            ],
            "Mathematics": [
                ["College Algebra"],
                ["Calculus I"],
                ["Calculus II"],
                ["Linear Algebra"],
                ["Discrete Mathematics"],
                ["Differential Equations", "Abstract Algebra"],
                ["Probability and Statistics"],
            ],
            "Information Technology": [
                ["Intro to Programming"],
                ["Computer Organization"],
                ["Operating Systems"],
                ["Web Development Basics"],
                ["Database Systems"],
            ],
            "Business Administration": [
                ["Introduction to Business"],
                ["Management"],
                ["Accounting I"],
                ["Marketing Fundamentals"],
                ["Business Ethics"],
            ],
            "Biology": [
                ["General Biology I"],
                ["General Biology II"],
                ["Human Anatomy"],
                ["Chemistry I"],
                ["Chemistry II"],
            ],
            "Chemistry": [
                ["General Chemistry I"],
                ["General Chemistry II"],
                ["Calculus I"],
                ["Physics I"],
            ],
            "Physics": [
                ["Physics I"],
                ["Physics II"],
                ["Calculus I"],
                ["Calculus II"],
                ["Linear Algebra"],
            ],
        }

        for title, options_per_group in requirement_groups.items():
            program_id = program_id_by_title[title]
            for option_group in options_per_group:
                cursor.execute(
                    "INSERT INTO ProgramRequiredCourses (ParentID) VALUES (?)",
                    (program_id,),
                )
                required_group_id = cursor.lastrowid
                for course_name in option_group:
                    if course_name in course_id_by_name:
                        cursor.execute(
                            """
                            INSERT INTO ProgramRequiredCourseOptions (CourseID, ParentID)
                            VALUES (?, ?)
                            """,
                            (course_id_by_name[course_name], required_group_id),
                        )

        # ==================== 4) TERMS AND COURSE OFFERINGS ====================
        terms = [
            (2026, "Spring", None),
            (2026, "Summer", 1),
            (2026, "Fall", None),
            (2027, "Spring", None),
            (2027, "Summer", 1),
            (2027, "Fall", None),
        ]
        cursor.executemany(
            "INSERT INTO Terms (Year, Season, Number) VALUES (?, ?, ?)",
            terms,
        )

        term_ids = {
            (year, season): row[0]
            for year, season, _ in terms
            for row in cursor.execute(
                "SELECT ID FROM Terms WHERE Year = ? AND Season = ?",
                (year, season),
            ).fetchall()
        }

        # Diverse course offerings across terms
        offerings_data = [
            # Spring 2026
            ("Intro to Programming", (2026, "Spring")),
            ("Web Development Basics", (2026, "Spring")),
            ("College Algebra", (2026, "Spring")),
            ("English Composition I", (2026, "Spring")),
            ("General Biology I", (2026, "Spring")),
            ("General Chemistry I", (2026, "Spring")),
            ("Introduction to Business", (2026, "Spring")),
            ("Discrete Mathematics", (2026, "Spring")),
            
            # Summer 2026
            ("Data Structures", (2026, "Summer")),
            ("Calculus I", (2026, "Summer")),
            ("Object-Oriented Programming", (2026, "Summer")),
            ("Trigonometry", (2026, "Summer")),
            
            # Fall 2026
            ("Data Structures and Algorithms", (2026, "Fall")),
            ("Computer Organization", (2026, "Fall")),
            ("Artificial Intelligence", (2026, "Fall")),
            ("Calculus II", (2026, "Fall")),
            ("English Composition II", (2026, "Fall")),
            ("General Chemistry II", (2026, "Fall")),
            ("Physics I", (2026, "Fall")),
            ("Linear Algebra", (2026, "Fall")),
            
            # Spring 2027
            ("Database Systems", (2027, "Spring")),
            ("Web Applications", (2027, "Spring")),
            ("Machine Learning", (2027, "Spring")),
            ("Differential Equations", (2027, "Spring")),
            ("Operating Systems", (2027, "Spring")),
            ("Literature and Analysis", (2027, "Spring")),
            ("Physics II", (2027, "Spring")),
            ("Probability and Statistics", (2027, "Spring")),
            
            # Summer 2027
            ("Intro to Cybersecurity", (2027, "Summer")),
            ("Technical Writing", (2027, "Summer")),
            ("Human Anatomy", (2027, "Summer")),
            
            # Fall 2027
            ("Abstract Algebra", (2027, "Fall")),
            ("Management", (2027, "Fall")),
            ("Business Ethics", (2027, "Fall")),
            ("Accounting I", (2027, "Fall")),
        ]

        for course_name, (year, season) in offerings_data:
            if course_name in course_id_by_name:
                term_id = term_ids.get((year, season))
                if term_id:
                    cursor.execute(
                        "INSERT INTO CoursesOffered (CourseID, ParentID) VALUES (?, ?)",
                        (course_id_by_name[course_name], term_id),
                    )

        offered_course_ids = [
            row[0] for row in cursor.execute("SELECT ID FROM CoursesOffered ORDER BY ID").fetchall()
        ]

        # ==================== 5) SECTIONS WITH DIVERSE INSTRUCTORS AND DETAILS ====================
        instructors = [
            "Dr. Allen", "Prof. Nguyen", "Dr. Patel", "Dr. Rivera", "Dr. Carter", "Dr. Lopez",
            "Prof. Martinez", "Dr. Thompson", "Dr. Jackson", "Prof. White", "Dr. Harris",
            "Prof. Clark", "Dr. Lewis", "Prof. Walker", "Dr. Hall", "Prof. Young",
        ]
        
        methods = ["In Person", "Online", "Hybrid"]
        locations = [
            "Science Hall 201", "Tech Building 115", "Math Center 302",
            "Engineering 101", "Engineering 202", "Online",
            "Student Union 350", "Lab 405", "Classroom A", "Classroom B",
        ]
        
        sections = []
        for idx, course_id in enumerate(offered_course_ids):
            # Create 1-3 sections per course offering
            num_sections = (idx % 3) + 1
            for section_num in range(1, num_sections + 1):
                instructor = instructors[(idx + section_num) % len(instructors)]
                method = methods[idx % len(methods)]
                location = locations[idx % len(locations)] if method != "Online" else "Online"
                max_seats = 20 + (idx * 3) % 30
                seats_left = max_seats - ((idx + section_num) % (max_seats - 5))
                status = ["Open", "Closed", "Reopened"][(idx + section_num) % 3]
                
                # Determine start and end dates based on course term
                course_info = cursor.execute(
                    "SELECT ParentID FROM CoursesOffered WHERE ID = ?",
                    (course_id,),
                ).fetchone()
                term_id = course_info[0]
                term_info = cursor.execute(
                    "SELECT Year, Season FROM Terms WHERE ID = ?",
                    (term_id,),
                ).fetchone()
                year, season = term_info
                
                if season == "Spring":
                    start_date = f"{year}-01-12"
                    end_date = f"{year}-05-01"
                elif season == "Summer":
                    start_date = f"{year}-05-18"
                    end_date = f"{year}-07-10"
                else:  # Fall
                    start_date = f"{year}-08-24"
                    end_date = f"{year}-12-11"
                
                sections.append((
                    section_num, instructor, start_date, end_date, status,
                    max_seats, seats_left, method, location, course_id
                ))

        cursor.executemany(
            """
            INSERT INTO Sections (
                SectionNum, Instructor, StartDate, EndDate, Status,
                MaxSeats, SeatsLeft, Method, Location, ParentID
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sections,
        )

        section_ids = [row[0] for row in cursor.execute("SELECT ID FROM Sections ORDER BY ID").fetchall()]

        # ==================== 6) DIVERSE MEET TIMES ====================
        day_times = [
            ("Monday", "09:00", "10:15"),
            ("Tuesday", "10:30", "11:45"),
            ("Wednesday", "13:00", "14:15"),
            ("Thursday", "14:30", "15:45"),
            ("Friday", "16:00", "17:15"),
            ("Monday", "18:00", "19:15"),
            ("Wednesday", "11:00", "12:15"),
            ("Tuesday", "15:00", "16:15"),
        ]

        meet_times = []
        for idx, section_id in enumerate(section_ids):
            # Most sections have 2 days per week
            num_meet_times = 2 if idx % 5 != 4 else 3
            for i in range(num_meet_times):
                day, start, end = day_times[(idx + i) % len(day_times)]
                meet_times.append((day, start, end, section_id))

        cursor.executemany(
            "INSERT INTO MeetTimes (Day, StartTime, EndTime, ParentID) VALUES (?, ?, ?, ?)",
            meet_times,
        )

        # ==================== 7) ADVISORS ====================
        advisors_data = [
            "Dr. Jordan Kim",
            "Dr. Maria Diaz",
            "Prof. Robert Chen",
            "Dr. Sarah Mitchell",
            "Prof. James Turner",
            "Dr. Lisa Anderson",
            "Prof. Michael Johnson",
        ]
        
        for advisor_name in advisors_data:
            cursor.execute(
                "INSERT INTO Advisors (Name) VALUES (?)",
                (advisor_name,),
            )

        advisor_ids = [row[0] for row in cursor.execute("SELECT ID FROM Advisors ORDER BY ID").fetchall()]

        # ==================== 8) DIVERSE STUDENTS ====================
        first_names = ["Alice", "Bob", "Carla", "David", "Emma", "Frank", "Grace", "Henry", "Iris", "Jack",
                      "Karen", "Liam", "Maya", "Nathan", "Olga", "Peter", "Quinn", "Rachel", "Samuel", "Tina"]
        last_names = ["Johnson", "Smith", "Reyes", "Williams", "Brown", "Jones", "Miller", "Davis", "Rodriguez",
                     "Martinez", "Garcia", "Chen", "Kim", "Patel", "Anderson", "Taylor", "Thompson", "Lee", "White", "Harris"]
        
        students_data = []
        for i in range(20):
            name = f"{first_names[i]} {last_names[i]}"
            gpa = 2.5 + (i * 0.15) % 1.5  # GPA between 2.5 and 4.0
            credits_earned = (i * 12) % 90
            graduation_terms = ["Spring 2027", "Fall 2027", "Spring 2028", "Fall 2028", "Spring 2029"]
            graduation_term = graduation_terms[i % len(graduation_terms)]
            advisor_id = advisor_ids[i % len(advisor_ids)]
            
            students_data.append((name, round(gpa, 2), credits_earned, graduation_term, advisor_id))

        cursor.executemany(
            """
            INSERT INTO Students (
                Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            students_data,
        )

        student_ids = [row[0] for row in cursor.execute("SELECT ID FROM Students ORDER BY ID").fetchall()]

        # ==================== 9) STUDENT PROGRAMS OF STUDY ====================
        programs = list(program_id_by_title.values())
        student_programs = []
        for idx, student_id in enumerate(student_ids):
            # Each student has 1-2 programs
            num_programs = (idx % 2) + 1
            for i in range(num_programs):
                program_id = programs[(idx + i) % len(programs)]
                student_programs.append((program_id, student_id))

        cursor.executemany(
            "INSERT INTO StudentProgramsOfStudy (ProgramID, ParentID) VALUES (?, ?)",
            student_programs,
        )

        # ==================== 10) COURSES TAKEN ====================
        courses_taken = []
        for idx, student_id in enumerate(student_ids):
            # Each student has taken 3-8 courses
            num_courses = (idx % 6) + 3
            course_ids = list(course_id_by_name.values())
            for i in range(num_courses):
                course_id = course_ids[(idx + i) % len(course_ids)]
                courses_taken.append((course_id, student_id))

        cursor.executemany(
            "INSERT INTO CoursesTaken (CourseID, ParentID) VALUES (?, ?)",
            courses_taken,
        )

        # ==================== 11) INTERESTS ====================
        interests_list = [
            "Artificial Intelligence", "Software Engineering", "Cybersecurity", "Data Science",
            "Web Development", "Mobile Development", "Game Development", "Cloud Computing",
            "Machine Learning", "DevOps", "Frontend Development", "Backend Development",
            "Database Design", "Blockchain", "Quantum Computing", "Natural Language Processing",
            "Computer Vision", "Robotics", "Biology Research", "Chemistry Lab Work",
        ]
        
        interests = []
        for idx, student_id in enumerate(student_ids):
            # Each student has 2-4 interests
            num_interests = (idx % 3) + 2
            for i in range(num_interests):
                interest = interests_list[(idx + i) % len(interests_list)]
                interests.append((interest, student_id))

        cursor.executemany(
            "INSERT INTO Interests (Interest, ParentID) VALUES (?, ?)",
            interests,
        )

        # ==================== 12) CHAT LOGS ====================
        chat_messages = [
            "Can you help me plan next semester courses?",
            "I need one more 300-level CSC course.",
            "What internships are relevant to my interests?",
            "How can I prepare for the Machine Learning course?",
            "When are office hours for the advisor?",
            "What are the prerequisites for Advanced Algorithms?",
            "Can I take two courses simultaneously?",
            "How do I register for courses online?",
            "What scholarships are available for my program?",
            "When are the next career fairs?",
            "How can I improve my GPA?",
            "What opportunities are there for research?",
            "Can I switch majors at this point?",
            "Are there any tutor recommendations?",
            "What internships align with cybersecurity?",
        ]

        chat_logs = []
        now = datetime.now()
        for idx, student_id in enumerate(student_ids):
            # Each student has 2-5 chat logs
            num_logs = (idx % 4) + 2
            for i in range(num_logs):
                message = chat_messages[(idx + i) % len(chat_messages)]
                timestamp = (now - timedelta(days=(idx + i) * 3)).isoformat(timespec="seconds")
                chat_logs.append((message, timestamp, student_id))

        cursor.executemany(
            "INSERT INTO ChatLogs (Log, Timestamp, ParentID) VALUES (?, ?, ?)",
            chat_logs,
        )

        # ==================== 13) EVENTS AND EVENT DATES ====================
        events_data = [
            ("AI Career Panel", "Faculty and alumni discuss careers in AI and ML."),
            ("Secure Coding Workshop", "Hands-on workshop covering secure coding practices."),
            ("Software Design Interview Prep", "Interview prep focused on system design."),
            ("Internship Fair", "Networking with regional employers."),
            ("Resume Workshop", "Career center session for resume feedback."),
            ("Intro to Web Development", "Beginner workshop on modern web development."),
            ("Data Science Meetup", "Local data scientists share insights and experiences."),
            ("Study Abroad Information Session", "Learn about international study opportunities."),
            ("Graduate School Prep", "Information on graduate programs and applications."),
            ("Women in STEM Panel", "Successful women in STEM share their journeys."),
            ("Leadership Summit", "Building leadership skills workshop."),
            ("Community Service Event", "Volunteer opportunity in the community."),
            ("Math Olympiad Training", "Intense training for mathematics competitions."),
            ("Science Fair Showcase", "Student research presentations."),
            ("Career Networking Lunch", "Informal networking with alumni and professionals."),
        ]

        cursor.executemany(
            """
            INSERT INTO Events (Name, Description)
            VALUES (?, ?)
            """,
            events_data,
        )

        event_ids = [row[0] for row in cursor.execute("SELECT ID FROM Events ORDER BY ID").fetchall()]

        # ==================== 14) EVENT DATES ====================
        event_dates = []
        base_date = datetime(2026, 3, 1)
        for idx, event_id in enumerate(event_ids):
            # Each event has 1-2 dates
            num_dates = (idx % 2) + 1
            for i in range(num_dates):
                event_date = (base_date + timedelta(days=(idx * 7 + i * 14))).strftime("%Y-%m-%d")
                start_time = f"{9 + (idx % 8):02d}:00"
                end_time = f"{10 + (idx % 8):02d}:30"
                location = locations[idx % len(locations)]
                event_dates.append((event_date, start_time, end_time, location, event_id))

        cursor.executemany(
            """
            INSERT INTO EventDates (Date, StartTime, EndTime, Location, ParentID)
            VALUES (?, ?, ?, ?, ?)
            """,
            event_dates,
        )

        # ==================== 16) TRACKED SECTIONS ====================
        tracked_sections = []
        for idx, student_id in enumerate(student_ids):
            # Each student is tracking 1-3 sections
            num_tracked = (idx % 3) + 1
            for i in range(num_tracked):
                section_id = section_ids[(idx + i) % len(section_ids)]
                tracked_sections.append((section_id, student_id))

        cursor.executemany(
            "INSERT INTO TrackedSections (SectionID, ParentID) VALUES (?, ?)",
            tracked_sections,
        )

        conn.commit()
        print("✓ Comprehensive dummy data inserted successfully!")
        print(f"  - {len(courses)} courses")
        print(f"  - {len(program_rows)} programs")
        print(f"  - {len(term_ids)} terms")
        print(f"  - {len(offered_course_ids)} course offerings")
        print(f"  - {len(sections)} sections")
        print(f"  - {len(advisors_data)} advisors")
        print(f"  - {len(students_data)} students")
        print(f"  - {len(interests)} interest entries")
        print(f"  - {len(events_data)} events")
        print(f"  - {len(chat_logs)} chat logs")

if __name__ == "__main__":
    seed_comprehensive_data(reset_existing=False)
