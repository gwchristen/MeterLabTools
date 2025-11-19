import sqlite3
from sqlite3 import Error

class DatabaseManager:
    def __init__(self, db_file):
        """Initialize the DatabaseManager with a SQLite database file."""
        self.connection = None
        self.db_file = db_file

    def create_connection(self):
        """Create a database connection to the SQLite database specified by db_file."""
        try:
            self.connection = sqlite3.connect(self.db_file)
            print(f"Connected to the database: {self.db_file}")
        except Error as e:
            print(f"Error connecting to database: {e}")

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=()):
        """Execute a single query and commit changes."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_query(self, query, params=()):
        """Fetch results from a query."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
        except Error as e:
            print(f"Error fetching data: {e}")
