import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime


class InventoryDatabase:
    """Database manager for inventory system"""
    
    def __init__(self, db_path: str = 'inventory.db'):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return self.connection
        except sqlite3.Error as e:
            print(f"Connection error: {e}")
            return None
    
    def init_db(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY,
                    opco TEXT,
                    status TEXT,
                    mfr TEXT,
                    dev_code TEXT,
                    beg_ser TEXT,
                    end_ser TEXT,
                    qty INTEGER,
                    po_date TEXT,
                    po_number TEXT,
                    recv_date TEXT,
                    unit_cost REAL,
                    cid TEXT,
                    me_number TEXT,
                    pur_code TEXT,
                    est TEXT,
                    use TEXT,
                    notes1 TEXT,
                    notes2 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_dev_code ON inventory(dev_code)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_opco ON inventory(opco)
            ''')
            
            conn.commit()
            conn.close()
            print(f"Database initialized: {self.db_path}")
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
    
    def insert_item(self, item: Dict[str, Any]) -> bool:
        """Insert inventory item"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO inventory (
                    opco, status, mfr, dev_code, beg_ser, end_ser, qty,
                    po_date, po_number, recv_date, unit_cost, cid, me_number,
                    pur_code, est, use, notes1, notes2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('opco'),
                item.get('status'),
                item.get('mfr'),
                item.get('dev_code'),
                item.get('beg_ser'),
                item.get('end_ser'),
                item.get('qty', 0),
                item.get('po_date'),
                item.get('po_number'),
                item.get('recv_date'),
                item.get('unit_cost', 0.0),
                item.get('cid'),
                item.get('me_number'),
                item.get('pur_code'),
                item.get('est'),
                item.get('use'),
                item.get('notes1'),
                item.get('notes2'),
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error inserting item: {e}")
            return False
    
    def get_all_items(self) -> List[tuple]:
        """Get all inventory items"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, opco, status, mfr, dev_code, beg_ser, end_ser,
                       qty, po_date, po_number, recv_date, unit_cost, cid,
                       me_number, pur_code, est, use, notes1, notes2
                FROM inventory
                ORDER BY id
            ''')
            
            items = cursor.fetchall()
            conn.close()
            return items
            
        except sqlite3.Error as e:
            print(f"Error fetching items: {e}")
            return []
    
    def get_item_by_dev_code(self, dev_code: str) -> Optional[Dict]:
        """Get items by device code"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM inventory WHERE dev_code = ?
            ''', (dev_code,))
            
            items = cursor.fetchall()
            conn.close()
            return [dict(item) for item in items]
            
        except sqlite3.Error as e:
            print(f"Error fetching by device code: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM inventory')
            total_items = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(qty) FROM inventory')
            total_qty = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT SUM(qty * unit_cost) FROM inventory')
            total_value = cursor.fetchone()[0] or 0.0
            
            cursor.execute('SELECT AVG(unit_cost) FROM inventory')
            avg_cost = cursor.fetchone()[0] or 0.0
            
            cursor.execute('SELECT COUNT(DISTINCT opco) FROM inventory')
            unique_opcos = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT mfr) FROM inventory')
            unique_mfrs = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT dev_code) FROM inventory')
            unique_dev_codes = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_items': total_items,
                'total_qty': int(total_qty),
                'total_value': float(total_value),
                'avg_cost': float(avg_cost),
                'unique_opcos': unique_opcos,
                'unique_mfrs': unique_mfrs,
                'unique_dev_codes': unique_dev_codes,
            }
            
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def clear_all(self) -> bool:
        """Clear all inventory data"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM inventory')
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing data: {e}")
            return False
