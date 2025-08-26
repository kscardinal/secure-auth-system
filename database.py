import sqlite3

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

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
        role TEXT DEFAULT 'user'
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")
    
if __name__ == "__main__":
    init_db()
