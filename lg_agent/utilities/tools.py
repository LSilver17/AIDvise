from langchain_core.tools import tool
import sqlite3

# Database query tools
@tool("search_for_courses", return_direct=True)
def search_for_courses(cursor: sqlite3.Cursor, filter: str) -> str:
    """Retrieve all relevant info on courses matching a filter"""

    