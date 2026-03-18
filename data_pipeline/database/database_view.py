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
		terms = fetch_all(
			cursor,
			'''
			SELECT TermID, Year, Season, Num
			FROM Terms
			ORDER BY Year, Season, Num, TermID
			''',
		)

		print(f'Database: {db_path}')
		print('Hierarchy: Terms -> CoursesOffered -> (CourseRequirements, Sections -> MeetTimes)\n')

		for term in terms:
			summer_part = f' {term["Num"]}' if term['Season'] == 'Summer' and term['Num'] else ''
			print(f'Term {term["TermID"]}: {term["Season"]}{summer_part} {term["Year"]}')

			courses = fetch_all(
				cursor,
				'''
				SELECT CourseID, Department, Code, Description, Credits
				FROM CoursesOffered
				WHERE TermID = ?
				ORDER BY Department, Code, CourseID
				''',
				(term['TermID'],),
			)

			if not courses:
				print('  └─ (no courses)')
				continue

			for course in courses:
				print(
					f'  ├─ Course {course["CourseID"]}: '
					f'{course["Department"]} {course["Code"]} '
					f'({course["Credits"]} cr) - {course["Description"]}'
				)

				requirements = fetch_all(
					cursor,
					'''
					SELECT RequirementID, Department, Code, Grade
					FROM CourseRequirements
					WHERE CourseID = ?
					ORDER BY RequirementID
					''',
					(course['CourseID'],),
				)

				if requirements:
					for req in requirements:
						req_code = req['Code'] if req['Code'] is not None else 'N/A'
						req_grade = req['Grade'] if req['Grade'] is not None else 'N/A'
						print(
							f'  │  ├─ Requirement {req["RequirementID"]}: '
							f'{req["Department"]} {req_code} min grade {req_grade}'
						)
				else:
					print('  │  ├─ (no requirements)')

				sections = fetch_all(
					cursor,
					'''
					SELECT SectionID, SectionNum, Instructor, MaxSeats, SeatsLeft, Modalim, Location
					FROM Sections
					WHERE CourseID = ?
					ORDER BY SectionNum, SectionID
					''',
					(course['CourseID'],),
				)

				if not sections:
					print('  │  └─ (no sections)')
					continue

				for section in sections:
					location = section['Location'] if section['Location'] else 'TBD'
					print(
						f'  │  └─ Section {section["SectionID"]} '
						f'(#{section["SectionNum"]}): '
						f'{section["Instructor"]}, {section["Modalim"]}, {location}, '
						f'{section["SeatsLeft"]}/{section["MaxSeats"]} seats left'
					)

					meet_times = fetch_all(
						cursor,
						'''
						SELECT MeetTimeID, Day, StartTime, EndTime
						FROM MeetTimes
						WHERE SectionID = ?
						ORDER BY MeetTimeID
						''',
						(section['SectionID'],),
					)

					if meet_times:
						for meet in meet_times:
							print(
								f'  │     └─ MeetTime {meet["MeetTimeID"]}: '
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
