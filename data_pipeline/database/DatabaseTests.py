from database_dev_tools import __connect as _connect
import database_dev_tools, TestEntries

def test_connection():
    try:
        with _connect() as conn:
            print("Success: Database connected.")
    except Exception as e:
        print(f"Error: Failed to connect to database. {e}")

def test_database_setup():
    with _connect() as conn:
        database_dev_tools.setup_database()
        print("Success: Database setup completed without errors.")

def test_seed_dummy_entries():
    with _connect() as conn:
        TestEntries.seed_dummy_entries()
        print("Success: Dummy entries seeded without errors.")

        # Check if correct entries were added

# TODO: finish making tests