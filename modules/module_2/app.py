import sys
import csv
from datetime import datetime
from pathlib import Path
import sqlite3

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QFileDialog, QMessageBox, QSplitter,
                             QHeaderView)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from inventory_db import InventoryDatabase


class InventorySystemApp(QMainWindow):
    """Inventory System Module - Manages equipment and device inventory"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Inventory System")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize database
        self.db = InventoryDatabase('inventory.db')
        self.db.init_db()
        
        # Setup UI
        self.setup_ui()
        
        # Load existing data
        self.load_inventory_data()
    
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Equipment Inventory Management")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import CSV")
        import_btn.setMinimumWidth(150)
        import_btn.clicked.connect(self.import_csv)
        button_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export CSV")
        export_btn.setMinimumWidth(150)
        export_btn.clicked.connect(self.export_csv)
        button_layout.addWidget(export_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumWidth(150)
        refresh_btn.clicked.connect(self.load_inventory_data)
        button_layout.addWidget(refresh_btn)
        
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setMinimumWidth(150)
        stats_btn.clicked.connect(self.show_statistics)
        button_layout.addWidget(stats_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Data table
        self.table = QTableWidget()
        self.table.setColumnCount(19)
        self.table.setHorizontalHeaderLabels([
            "ID", "OpCo", "Status", "MFR", "Dev Code", "Beg Ser", "End Ser",
            "Qty", "PO Date", "PO Number", "Recv Date", "Unit Cost", "CID",
            "M.E. #", "Pur. Code", "Est.", "Use", "Notes 1", "Notes 2"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)
        
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Import', self.import_csv)
        file_menu.addAction('Export', self.export_csv)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Refresh', self.load_inventory_data)
        view_menu.addAction('Statistics', self.show_statistics)
        
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def load_inventory_data(self):
        """Load inventory data from database into table"""
        try:
            self.table.setRowCount(0)
            
            items = self.db.get_all_items()
            self.table.setRowCount(len(items))
            
            for row_idx, item in enumerate(items):
                for col_idx, value in enumerate(item):
                    cell = QTableWidgetItem(str(value) if value else "")
                    self.table.setItem(row_idx, col_idx, cell)
            
            self.status_label.setText(f"Loaded {len(items)} items")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {e}")
            self.status_label.setText("Error loading data")
    
    def import_csv(self):
        """Import CSV file into database"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CSV File", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                header = next(csv_reader)  # Skip header
                
                for row in csv_reader:
                    if not any(row):  # Skip empty rows
                        continue
                    
                    if len(row) >= 17:
                        item = {
                            'id': row[0] if row[0] else None,
                            'opco': row[1],
                            'status': row[2],
                            'mfr': row[3],
                            'dev_code': row[4],
                            'beg_ser': row[5],
                            'end_ser': row[6],
                            'qty': int(row[7]) if row[7] else 0,
                            'po_date': row[8],
                            'po_number': row[9],
                            'recv_date': row[10],
                            'unit_cost': float(row[11]) if row[11] else 0.0,
                            'cid': row[12],
                            'me_number': row[13],
                            'pur_code': row[14],
                            'est': row[15],
                            'use': row[16],
                            'notes1': row[17] if len(row) > 17 else '',
                            'notes2': row[18] if len(row) > 18 else '',
                        }
                        
                        self.db.insert_item(item)
                        imported_count += 1
            
            self.load_inventory_data()
            QMessageBox.information(self, "Success", f"Imported {imported_count} items")
            self.status_label.setText(f"Imported {imported_count} items")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error importing CSV: {e}")
    
    def export_csv(self):
        """Export database to CSV file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            "inventory_export.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            items = self.db.get_all_items()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'OpCo', 'Status', 'MFR', 'Dev Code', 'Beg Ser', 'End Ser',
                    'Qty', 'PO Date', 'PO Number', 'Recv Date', 'Unit Cost', 'CID',
                    'M.E. #', 'Pur. Code', 'Est.', 'Use', 'Notes 1', 'Notes 2'
                ])
                
                for item in items:
                    writer.writerow(item)
            
            QMessageBox.information(self, "Success", f"Exported {len(items)} items to {file_path}")
            self.status_label.setText(f"Exported {len(items)} items")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting CSV: {e}")
    
    def show_statistics(self):
        """Show inventory statistics"""
        try:
            stats = self.db.get_statistics()
            
            msg = (
                f"Inventory Statistics\n"
                f"{'='*40}\n\n"
                f"Total Items: {stats['total_items']}\n"
                f"Total Quantity: {stats['total_qty']}\n"
                f"Total Value: ${stats['total_value']:,.2f}\n"
                f"Average Cost: ${stats['avg_cost']:,.2f}\n"
                f"Unique OpCos: {stats['unique_opcos']}\n"
                f"Unique Manufacturers: {stats['unique_mfrs']}\n"
                f"Unique Device Codes: {stats['unique_dev_codes']}\n"
            )
            
            QMessageBox.information(self, "Statistics", msg)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting statistics: {e}")
    
    def show_about(self):
        """Show about dialog"""
        msg = (
            "Inventory System v1.0.0\n\n"
            "Equipment and device inventory management system.\n\n"
            "Features:\n"
            "• Import CSV data\n"
            "• View and manage inventory\n"
            "• Export to CSV\n"
            "• View statistics\n\n"
            "Created with PyQt6"
        )
        QMessageBox.information(self, "About", msg)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = InventorySystemApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
