QCC Course Data Pipeline

Files:
- create_courses_db.py: creates the SQLite database
- scrape_qcc_courses.py: scrapes QCC public course/program page data
- update_courses_db.py: inserts scraped course data into the database
- view_courses.py: prints saved course records for testing

Database fields:
- program_name
- subject
- course_code
- title
- semester_offered
- credits
- prerequisites
- source_url
- last_updated

How to run:
1. python create_courses_db.py
2. python scrape_qcc_courses.py
3. python update_courses_db.py
4. python view_courses.py
