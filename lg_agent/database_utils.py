import sqlite3

# Utility function to recursively get all data related to a target entry in a table based on the hierarchy of the database schema, starting from the target entry and including all entries that reference it as a foreign key, along with their relevant linked data based on the hierarchy, and returning this information in a structured format that indicates the relationships between the data
def get_data_with_hierarchy(cursor: sqlite3.Cursor, table: str, targetID: str) -> dict:
    results = {}
    entry = {}

    results["entry"] = table + ": " + targetID

    # Get the entry from the target table that corresponds to the target and add its fields and values to the results
    for row in cursor.execute(f"SELECT * FROM {table} WHERE ID = ?", (targetID,)):
        for idx, col in enumerate(cursor.description) if col[0] != "ID" and col[0] != "ParentID" and row[idx] is not None else []:
            entry[col[0]] = row[idx]

    # Find all tables that reference target as a foreign key
    cursor.execute(
        '''
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND sql LIKE ?
        ''', 
        (f'%REFERENCES {table}(ID)%',)
    )
    related_tables = [row[0] for row in cursor.fetchall()]

    # Loop through each related table and get all entries that reference the target entry, along with their relevant linked data based on the hierarchy, and add this information to the results in a structured format that indicates the relationships between the data
    if related_tables:
        for table in related_tables:
            entry[f"{table}"] = get_data_with_hierarchy(cursor, table, targetID)
    
    results["content"] = entry
    return results


def _format_hierarchy_node(node: dict, depth: int = 0) -> str:
    indent = "  " * depth
    inner_indent = "  " * (depth + 1)
    lines = [f"{indent}{{"]
    lines.append(f"{inner_indent}\"entry\": \"{node['entry']}\",")

    content = node.get("content", {})
    field_items = []
    child_items = []

    for key, value in content.items():
        if isinstance(value, dict) and "entry" in value and "content" in value:
            child_items.append((key, value))
        else:
            field_items.append((key, value))

    lines.append(f"{inner_indent}\"fields\": {{")
    for idx, (key, value) in enumerate(field_items):
        comma = "," if idx < len(field_items) - 1 else ""
        value_str = str(value).replace('"', '\\"')
        lines.append(f"{inner_indent}  \"{key}\": \"{value_str}\"{comma}")
    lines.append(f"{inner_indent}}},")

    lines.append(f"{inner_indent}\"children\": {{")
    for idx, (key, child) in enumerate(child_items):
        child_block = _format_hierarchy_node(child, depth + 2)
        child_lines = child_block.split("\n")
        comma = "," if idx < len(child_items) - 1 else ""

        if child_lines:
            lines.append(f"{inner_indent}  \"{key}\": {child_lines[0].lstrip()}")
            for child_line in child_lines[1:-1]:
                lines.append(child_line)
            lines.append(f"{child_lines[-1]}{comma}")
    lines.append(f"{inner_indent}}}")

    lines.append(f"{indent}}}")
    return "\n".join(lines)


# Utility function convert output of get_data_with_hierarchy into a readable string format
def hierarchy_data_to_string(hierarchy_data: dict) -> str:
    return _format_hierarchy_node(hierarchy_data)

# Utility function to get data with hierarchy as a string
def get_data_with_hierarchy_string(cursor: sqlite3.Cursor, table: str, targetID: str) -> str:
    hierarchy_data = get_data_with_hierarchy(cursor, table, targetID)
    return hierarchy_data_to_string(hierarchy_data)

# Utility function to get IDs of entries in a table based on a field value
def get_ids_by_field_value(cursor: sqlite3.Cursor, table: str, field: str, value: str) -> list:
    cursor.execute(f"SELECT ID FROM {table} WHERE {field} = ?", (value,))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get all entries in a table that match a filter condition on a field, and return their IDs as a list
def get_ids_by_field_filter(cursor: sqlite3.Cursor, table: str, field: str, filter_value: str) -> list:
    cursor.execute(f"SELECT ID FROM {table} WHERE {field} LIKE ?", (f"%{filter_value}%",))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get IDs of all entries in a table that reference a target entry as a foreign key, and return these IDs as a list
def get_ids_by_parent(cursor: sqlite3.Cursor, table: str, targetID: str) -> list:
    cursor.execute(f"SELECT ID FROM {table} WHERE ParentID = ?", (targetID,))
    results = cursor.fetchall()
    return [row[0] for row in results]

# Utility function to get IDs of all students that are advised by a target advisor, and return these IDs as a list
def get_students_by_advisor(cursor: sqlite3.Cursor, advisorID: str) -> list:
    cursor.execute("SELECT ID FROM Students WHERE AdvisorID = ?", (advisorID,))
    results = cursor.fetchall()
    return [row[0] for row in results]