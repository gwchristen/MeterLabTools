import sqlite3
from sqlite3 import Error

def init_db(db_file='meter_lab_tools.db'):
    """Initialize the database with required schema"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create measurements table
        cursor.execute('''CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            value REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Create recently_used table
        cursor.execute('''CREATE TABLE IF NOT EXISTS recently_used (
            id INTEGER PRIMARY KEY,
            module_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create user_preferences table
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            theme TEXT DEFAULT 'Light',
            font_size INTEGER DEFAULT 10,
            window_state TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        conn.commit()
        print(f"Database initialized successfully: {db_file}")
        
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()