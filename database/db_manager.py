import sqlite3
from sqlite3 import Error
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self, db_path: str = 'meter_lab_tools.db'):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection"""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
            except Error as e:
                print(f"Connection error: {e}")
        return self.connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query"""
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            print(f"Query error: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except Error as e:
            print(f"Update error: {e}")
            conn.rollback()
            return False
    
    def add_recent_module(self, module_id: str, timestamp: str) -> bool:
        """Add a module to recently used list"""
        query = "INSERT INTO recently_used (module_id, timestamp) VALUES (?, ?)"
        return self.execute_update(query, (module_id, timestamp))
    
    def get_recently_used(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get list of recently used modules"""
        query = """
            SELECT DISTINCT module_id, timestamp
            FROM recently_used
            ORDER BY timestamp DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (limit,))
        return [dict(row) for row in rows]
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None