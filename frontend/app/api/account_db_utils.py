# import dependencies
import sqlite3

def validate_credentials(username, password):
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect('Test.db')
        conn.execute('PRAGMA foreign_keys = ON')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Fetch user credentials from the database if the username exists
        cursor.execute('SELECT username, password FROM Users WHERE username = ?', (username,))
        credential = cursor.fetchone()

        if credential is None:
            raise ValueError("Username not found")
        
        # TODO: Decrypt the stored password
        decrypted_password = credential[1]

        # Compare the provided password with the decrypted stored password
        return password == decrypted_password
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            conn.close()

def create_user(username, hashed_password, account_type):
    conn = None

    try:
        # Connect to sqlite database
        conn = sqlite3.connect('Test.db')
        conn.execute('PRAGMA foreign_keys = ON')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute('SELECT username FROM Users WHERE username = ?', (username,))
        if cursor.fetchone() is not None:
            raise ValueError("Username already exists")
        
        # Insert the new user into the database
        cursor.execute('INSERT INTO Users (username, password, account_type) VALUES (?, ?, ?)', (username, hashed_password, account_type))
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            conn.close()