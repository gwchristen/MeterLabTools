import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime


class InventoryDatabase:
    """Database manager for Created Histories system"""
    
    def __init__(self, db_path: str = 'created_histories.db'):
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opco TEXT NOT NULL,
                    device_type TEXT NOT NULL,
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
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_opco_type ON inventory(opco, device_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_code ON inventory(dev_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_po_number ON inventory(po_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_recv_date ON inventory(recv_date)')
            
            # Create user preferences table for UI state persistence
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"Database initialized: {self.db_path}")
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
    
    def get_items_by_sheet(self, opco: str, device_type: str) -> List[tuple]:
        """Get items filtered by OpCo and device type"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, opco, device_type, status, mfr, dev_code, beg_ser, end_ser,
                       qty, po_date, po_number, recv_date, unit_cost, cid,
                       me_number, pur_code, est, use, notes1, notes2
                FROM inventory
                WHERE opco = ? AND device_type = ?
                ORDER BY id DESC
            ''', (opco, device_type))
            
            items = cursor.fetchall()
            conn.close()
            return items
            
        except sqlite3.Error as e:
            print(f"Error fetching items: {e}")
            return []
    
    def search_items(self, opco: str, device_type: str, search_type: str, search_value: str) -> List[tuple]:
        """Search items by device code, PO number, or recv date"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if search_type == "dev_code":
                cursor.execute('''
                    SELECT id, opco, device_type, status, mfr, dev_code, beg_ser, end_ser,
                           qty, po_date, po_number, recv_date, unit_cost, cid,
                           me_number, pur_code, est, use, notes1, notes2
                    FROM inventory
                    WHERE opco = ? AND device_type = ? AND dev_code LIKE ?
                    ORDER BY id DESC
                ''', (opco, device_type, f"%{search_value}%"))
            
            elif search_type == "po_number":
                cursor.execute('''
                    SELECT id, opco, device_type, status, mfr, dev_code, beg_ser, end_ser,
                           qty, po_date, po_number, recv_date, unit_cost, cid,
                           me_number, pur_code, est, use, notes1, notes2
                    FROM inventory
                    WHERE opco = ? AND device_type = ? AND po_number LIKE ?
                    ORDER BY id DESC
                ''', (opco, device_type, f"%{search_value}%"))
            
            elif search_type == "recv_date":
                cursor.execute('''
                    SELECT id, opco, device_type, status, mfr, dev_code, beg_ser, end_ser,
                           qty, po_date, po_number, recv_date, unit_cost, cid,
                           me_number, pur_code, est, use, notes1, notes2
                    FROM inventory
                    WHERE opco = ? AND device_type = ? AND recv_date = ?
                    ORDER BY id DESC
                ''', (opco, device_type, search_value))
            
            items = cursor.fetchall()
            conn.close()
            return items
            
        except sqlite3.Error as e:
            print(f"Error searching items: {e}")
            return []
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get a single item by ID"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM inventory WHERE id = ?', (item_id,))
            item = cursor.fetchone()
            conn.close()
            
            return dict(item) if item else None
            
        except sqlite3.Error as e:
            print(f"Error fetching item: {e}")
            return None
    
    def insert_item(self, item: Dict[str, Any]) -> int:
        """Insert inventory item and return ID"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO inventory (
                    opco, device_type, status, mfr, dev_code, beg_ser, end_ser, qty,
                    po_date, po_number, recv_date, unit_cost, cid, me_number,
                    pur_code, est, use, notes1, notes2, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('opco'),
                item.get('device_type'),
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
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            item_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return item_id
            
        except sqlite3.Error as e:
            print(f"Error inserting item: {e}")
            return -1
    
    def update_item(self, item_id: int, item: Dict[str, Any]) -> bool:
        """Update inventory item"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE inventory SET
                    opco = ?, device_type = ?, status = ?, mfr = ?, dev_code = ?,
                    beg_ser = ?, end_ser = ?, qty = ?, po_date = ?, po_number = ?,
                    recv_date = ?, unit_cost = ?, cid = ?, me_number = ?,
                    pur_code = ?, est = ?, use = ?, notes1 = ?, notes2 = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                item.get('opco'),
                item.get('device_type'),
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
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                item_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating item: {e}")
            return False
    
    def delete_item(self, item_id: int) -> bool:
        """Delete inventory item"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            return False
    
    def get_statistics(self, opco: str, device_type: str) -> Dict[str, Any]:
        """Get statistics for a specific sheet"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM inventory 
                WHERE opco = ? AND device_type = ?
            ''', (opco, device_type))
            total_items = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT SUM(qty) FROM inventory
                WHERE opco = ? AND device_type = ?
            ''', (opco, device_type))
            result = cursor.fetchone()
            total_qty = result[0] if result and result[0] else 0
            
            cursor.execute('''
                SELECT SUM(qty * unit_cost) FROM inventory
                WHERE opco = ? AND device_type = ?
            ''', (opco, device_type))
            result = cursor.fetchone()
            total_value = result[0] if result and result[0] else 0.0
            
            cursor.execute('''
                SELECT AVG(unit_cost) FROM inventory 
                WHERE opco = ? AND device_type = ? AND unit_cost > 0
            ''', (opco, device_type))
            result = cursor.fetchone()
            avg_cost = result[0] if result and result[0] else 0.0
            
            conn.close()
            
            return {
                'total_items': int(total_items),
                'total_qty': int(total_qty),
                'total_value': float(total_value),
                'avg_cost': float(avg_cost),
            }
            
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def clear_sheet(self, opco: str, device_type: str) -> bool:
        """Clear all items from a specific sheet"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM inventory WHERE opco = ? AND device_type = ?', (opco, device_type))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing sheet: {e}")
            return False
    
    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference value"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT preference_value FROM user_preferences WHERE preference_key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else default
        except sqlite3.Error as e:
            print(f"Error getting preference: {e}")
            return default
    
    def set_preference(self, key: str, value: str) -> bool:
        """Set a user preference value"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_preferences (preference_key, preference_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(preference_key) DO UPDATE SET
                    preference_value = excluded.preference_value,
                    updated_at = excluded.updated_at
            ''', (key, value, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error setting preference: {e}")
            return False