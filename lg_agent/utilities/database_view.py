import sqlite3
from pathlib import Path


def resolve_db_path() -> Path:
	candidates = [
		Path('Test.db'),
		Path(__file__).resolve().parents[2] / 'Test.db',
		Path(__file__).resolve().parent / 'Test.db',
	]

	for candidate in candidates:
		if candidate.exists():
			return candidate

	return candidates[0]


def fetch_all(cursor: sqlite3.Cursor, query: str, params: tuple = ()):
	cursor.execute(query, params)
	return cursor.fetchall()


def print_hierarchy(db_path: Path) -> None:
	conn = sqlite3.connect(str(db_path))
	conn.row_factory = sqlite3.Row
	conn.execute('PRAGMA foreign_keys = ON')
	cursor = conn.cursor()

	try:
		print(f'Database: {db_path}')

		# ── Advisors -> Students -> (MajorsAndMinors, Interests, ChatLogs, RelevantEvents -> Events) ──
		print('\n══ ADVISORS ══')
		print('Hierarchy: Users(Advisor) -> Advisors -> Students -> (MajorsAndMinors, Interests, ChatLogs, RelevantEvents -> Events)\n')

		advisors = fetch_all(
			cursor,
			'''
			SELECT a.ID, a.Name, u.Username
			FROM Advisors a
			JOIN Users u ON a.UserID = u.ID
			ORDER BY a.ID
			''',
		)

		for advisor in advisors:
			print(f'Advisor {advisor["ID"]}: {advisor["Name"]} (user: {advisor["Username"]})')

			students = fetch_all(
				cursor,
				'''
				SELECT s.ID, s.Name, s.GPA, s.CreditsEarned, s.IntendedGraduationTerm, u.Username
				FROM Students s
				JOIN Users u ON s.UserID = u.ID
				WHERE s.AdvisorID = ?
				ORDER BY s.ID
				''',
				(advisor['ID'],),
			)

			if not students:
				print('  └─ (no students)')
				continue

			for student in students:
				gpa = student['GPA'] if student['GPA'] is not None else 'N/A'
				credits_earned = student['CreditsEarned'] if student['CreditsEarned'] is not None else 'N/A'
				grad_term = student['IntendedGraduationTerm'] if student['IntendedGraduationTerm'] else 'N/A'
				print(
					f'  ├─ Student {student["ID"]}: {student["Name"]} '
					f'(user: {student["Username"]}, GPA: {gpa}, '
					f'Credits: {credits_earned}, Grad: {grad_term})'
				)

				majors_minors = fetch_all(
					cursor,
					'''
					SELECT ID, Title, Type
					FROM MajorsAndMinors
					WHERE StudentID = ?
					ORDER BY Type, Title
					''',
					(student['ID'],),
				)

				if majors_minors:
					for mm in majors_minors:
						print(f'  │  ├─ {mm["Type"]}: {mm["Title"]}')
				else:
					print('  │  ├─ (no majors/minors)')

				interests = fetch_all(
					cursor,
					'''
					SELECT ID, Interest
					FROM Interests
					WHERE StudentID = ?
					ORDER BY ID
					''',
					(student['ID'],),
				)

				if interests:
					interest_list = ', '.join(i['Interest'] for i in interests)
					print(f'  │  ├─ Interests: {interest_list}')
				else:
					print('  │  ├─ Interests: (none)')

				chat_logs = fetch_all(
					cursor,
					'''
					SELECT ID, Log, Timestamp
					FROM ChatLogs
					WHERE StudentID = ?
					ORDER BY Timestamp
					''',
					(student['ID'],),
				)

				if chat_logs:
					for log in chat_logs:
						print(f'  │  ├─ ChatLog {log["ID"]} [{log["Timestamp"]}]: {log["Log"]}')
				else:
					print('  │  ├─ (no chat logs)')

				relevant_events = fetch_all(
					cursor,
					'''
					SELECT re.ID, re.UrgencyLevel, e.Name, e.StartDate, e.StartTime, e.Location
					FROM RelevantEvents re
					JOIN Events e ON re.EventID = e.ID
					WHERE re.StudentID = ?
					ORDER BY re.UrgencyLevel, e.StartDate
					''',
					(student['ID'],),
				)

				if relevant_events:
					for re_row in relevant_events:
						loc = re_row['Location'] if re_row['Location'] else 'TBD'
						print(
							f'  │  └─ Event {re_row["ID"]} [{re_row["UrgencyLevel"]}]: '
							f'{re_row["Name"]} on {re_row["StartDate"]} at {re_row["StartTime"]}, {loc}'
						)
				else:
					print('  │  └─ (no relevant events)')

		print()

		# ── Terms -> CoursesOffered -> (CourseRequirements, Sections -> MeetTimes) ──
		print('\n══ COURSE CATALOG ══')
		print('Hierarchy: Terms -> CoursesOffered -> (CourseRequirements, Sections -> MeetTimes)\n')

		terms = fetch_all(
			cursor,
			'''
			SELECT ID, Year, Season, Number
			FROM Terms
			ORDER BY Year, Season, Number, ID
			''',
		)

		for term in terms:
			summer_part = f' {term["Number"]}' if term['Season'] == 'Summer' and term['Number'] else ''
			print(f'Term {term["ID"]}: {term["Season"]}{summer_part} {term["Year"]}')

			courses = fetch_all(
				cursor,
				'''
				SELECT ID, Department, Code, Description, Credits
				FROM CoursesOffered
				WHERE TermID = ?
				ORDER BY Department, Code, ID
				''',
				(term['ID'],),
			)

			if not courses:
				print('  └─ (no courses)')
				continue

			for course in courses:
				print(
					f'  ├─ Course {course["ID"]}: '
					f'{course["Department"]} {course["Code"]} '
					f'({course["Credits"]} cr) - {course["Description"]}'
				)

				requirements = fetch_all(
					cursor,
					'''
					SELECT ID, RequiredCourseID, RequiredGrade
					FROM CourseRequirements
					WHERE CourseID = ?
					ORDER BY ID
					''',
					(course['ID'],),
				)

				if requirements:
					for req in requirements:
						req_grade = req['RequiredGrade'] if req['RequiredGrade'] is not None else 'N/A'
						print(
							f'  │  ├─ Requirement {req["ID"]}: '
							f'CourseID {req["RequiredCourseID"]} min grade {req_grade}'
						)
				else:
					print('  │  ├─ (no requirements)')

				sections = fetch_all(
					cursor,
					'''
					SELECT ID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modality, Location
					FROM Sections
					WHERE CourseID = ?
					ORDER BY SectionNum, ID
					''',
					(course['ID'],),
				)

				if not sections:
					print('  │  └─ (no sections)')
					continue

				for section in sections:
					location = section['Location'] if section['Location'] else 'TBD'
					print(
						f'  │  └─ Section {section["ID"]} '
						f'(#{section["SectionNum"]}): '
						f'{section["Instructor"]}, {section["Modality"]}, {location}, '
						f'{section["SeatsLeft"]}/{section["MaxSeats"]} seats left'
					)

					meet_times = fetch_all(
						cursor,
						'''
						SELECT ID, Day, StartTime, EndTime
						FROM MeetTimes
						WHERE SectionID = ?
						ORDER BY ID
						''',
						(section['ID'],),
					)

					if meet_times:
						for meet in meet_times:
							print(
								f'  │     └─ MeetTime {meet["ID"]}: '
								f'{meet["Day"]} {meet["StartTime"]}-{meet["EndTime"]}'
							)
					else:
						print('  │     └─ (no meet times)')

		print()

	finally:
		conn.close()


if __name__ == '__main__':
	database_path = resolve_db_path()
	if not database_path.exists():
		print(
			f'Could not find database file at {database_path}. '
			'Run the seeding script first to create Test.db.'
		)
	else:
		print_hierarchy(database_path)
