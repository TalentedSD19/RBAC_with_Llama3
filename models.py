import sqlite3
DATABASE = 'database.db'

def create_table():
# Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create the `users` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role INTEGER NOT NULL DEFAULT 2,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            karma DOUBLE DEFAULT 0
        )
        ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Table created and sample data inserted successfully.")


# Helper function to execute queries
def execute_query(query, args=(), fetch_one=False, fetch_all=False, commit=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = None
    if fetch_one:
        result = cursor.fetchone()
    elif fetch_all:
        result = cursor.fetchall()
    if commit:
        conn.commit()
    conn.close()
    print(result)
    return result
