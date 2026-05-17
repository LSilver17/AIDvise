"""
Copyright 2026 Luca Silver

Basic script to add a test student to the database.
"""

import sys, os

# Add the path to the root directory to the path if not already there
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from data_pipeline.database.database_dev_tools import add_advisors_from_json, add_students_from_json

if __name__ == "__main__":
    add_advisors_from_json("test_advisors.json")
    add_students_from_json("test_students.json")