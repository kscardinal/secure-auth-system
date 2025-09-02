import sqlite3

# Define the database file
DB_FILE = "users.db"

# Initialize the DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the table in the DB
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        date_created TEXT NOT NULL,
        last_accessed TEXT,
        is_active INTEGER DEFAULT 1,
        role TEXT DEFAULT 'user',
        backup_code TEXT,
        login_attempts INTEGER DEFAULT 0,
        latest_reset TEXT,
        password_resets INTEGER DEFAULT 0,
        verification_attempts INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")
    

# Run the main program
if __name__ == "__main__":
    init_db()
