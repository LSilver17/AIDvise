import sqlite3

def create_database():
    conn = sqlite3.connect("courses.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_name TEXT,
        subject TEXT,
        course_code TEXT,
        title TEXT,
        semester_offered TEXT,
        credits TEXT,
        prerequisites TEXT,
        source_url TEXT,
        last_updated TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("courses.db created successfully")

if __name__ == "__main__":
    create_database()
