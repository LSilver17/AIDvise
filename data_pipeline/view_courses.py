import sqlite3

conn = sqlite3.connect("courses.db")
cur = conn.cursor()

rows = cur.execute("SELECT program_name, subject, course_code, title, semester_offered, credits FROM courses LIMIT 20").fetchall()

for row in rows:
    print(row)

conn.close()
