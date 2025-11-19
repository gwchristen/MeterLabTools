# Database Initialization Script

"""
This script initializes the database schema for the MeterLabTools project.
"""

import sqlite3


def init_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('meter_lab_tools.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        value REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()