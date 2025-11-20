import sys
import csv
import hashlib
import openpyxl
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QFileDialog, QMessageBox, QDialog,
                             QHeaderView, QTabWidget, QLineEdit, QComboBox,
                             QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit,
                             QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from inventory_db import InventoryDatabase


class PasswordDialog(QDialog):
    """Dialog for entering edit mode password"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Mode")
        self.setModal(True)
        self.setGeometry(400, 300, 300, 150)
        
        layout = QFormLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("Master Password:", self.password_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_password(self):
        return self.password_input.text()


class AddEditDialog(QDialog):
    """Dialog for adding/editing inventory items"""
    
    def __init__(self, parent=None, item=None, opco=None, device_type=None):
        super().__init__(parent)
        self.item = item
        self.opco = opco
        self.device_type = device_type
        
        if item:
            self.setWindowTitle("Edit Record")
        else:
            self.setWindowTitle("Add New Record")
        
        self.setGeometry(200, 200, 600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QFormLayout()
        
        # Read-only fields
        self.opco_input = QLineEdit()
        self.opco_input.setText(self.opco or "")
        self.opco_input.setReadOnly(True)
        layout.addRow("OpCo:", self.opco_input)
        
        self.device_type_input = QLineEdit()
        self.device_type_input.setText(self.device_type or "")
        self.device_type_input.setReadOnly(True)
        layout.addRow("Device Type:", self.device_type_input)
        
        # Editable fields
        self.status_input = QLineEdit()
        layout.addRow("Status:", self.status_input)
        
        self.mfr_input = QLineEdit()
        layout.addRow("Manufacturer:", self.mfr_input)
        
        self.dev_code_input = QLineEdit()
        layout.addRow("Device Code:", self.dev_code_input)
        
        self.beg_ser_input = QLineEdit()
        layout.addRow("Beginning Serial:", self.beg_ser_input)
        
        self.end_ser_input = QLineEdit()
        layout.addRow("Ending Serial:", self.end_ser_input)
        
        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(100000)
        layout.addRow("Quantity:", self.qty_input)
        
        self.po_date_input = QLineEdit()
        layout.addRow("PO Date:", self.po_date_input)
        
        self.po_number_input = QLineEdit()
        layout.addRow("PO Number:", self.po_number_input)
        
        self.recv_date_input = QLineEdit()
        layout.addRow("Received Date:", self.recv_date_input)
        
        self.unit_cost_input = QDoubleSpinBox()
        self.unit_cost_input.setMaximum(999999.99)
        self.unit_cost_input.setDecimals(2)
        layout.addRow("Unit Cost:", self.unit_cost_input)
        
        self.cid_input = QLineEdit()
        layout.addRow("CID:", self.cid_input)
        
        self.me_number_input = QLineEdit()
        layout.addRow("M.E. #:", self.me_number_input)
        
        self.pur_code_input = QLineEdit()
        layout.addRow("Purchase Code:", self.pur_code_input)
        
        self.est_input = QLineEdit()
        layout.addRow("Est.:", self.est_input)
        
        self.use_input = QLineEdit()
        layout.addRow("Use:", self.use_input)
        
        self.notes1_input = QTextEdit()
        self.notes1_input.setMaximumHeight(60)
        layout.addRow("Notes 1:", self.notes1_input)
        
        self.notes2_input = QTextEdit()
        self.notes2_input.setMaximumHeight(60)
        layout.addRow("Notes 2:", self.notes2_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
        # Populate if editing
        if self.item:
            self.status_input.setText(self.item.get('status', ''))
            self.mfr_input.setText(self.item.get('mfr', ''))
            self.dev_code_input.setText(self.item.get('dev_code', ''))
            self.beg_ser_input.setText(self.item.get('beg_ser', ''))
            self.end_ser_input.setText(self.item.get('end_ser', ''))
            self.qty_input.setValue(self.item.get('qty', 0))
            self.po_date_input.setText(self.item.get('po_date', ''))
            self.po_number_input.setText(self.item.get('po_number', ''))
            self.recv_date_input.setText(self.item.get('recv_date', ''))
            self.unit_cost_input.setValue(self.item.get('unit_cost', 0.0))
            self.cid_input.setText(self.item.get('cid', ''))
            self.me_number_input.setText(self.item.get('me_number', ''))
            self.pur_code_input.setText(self.item.get('pur_code', ''))
            self.est_input.setText(self.item.get('est', ''))
            self.use_input.setText(self.item.get('use', ''))
            self.notes1_input.setText(self.item.get('notes1', ''))
            self.notes2_input.setText(self.item.get('notes2', ''))
    
    def get_data(self):
        """Get data from form"""
        return {
            'opco': self.opco,
            'device_type': self.device_type,
            'status': self.status_input.text(),
            'mfr': self.mfr_input.text(),
            'dev_code': self.dev_code_input.text(),
            'beg_ser': self.beg_ser_input.text(),
            'end_ser': self.end_ser_input.text(),
            'qty': self.qty_input.value(),
            'po_date': self.po_date_input.text(),
            'po_number': self.po_number_input.text(),
            'recv_date': self.recv_date_input.text(),
            'unit_cost': self.unit_cost_input.value(),
            'cid': self.cid_input.text(),
            'me_number': self.me_number_input.text(),
            'pur_code': self.pur_code_input.text(),
            'est': self.est_input.text(),
            'use': self.use_input.text(),
            'notes1': self.notes1_input.toPlainText(),
            'notes2': self.notes2_input.toPlainText(),
        }


class CreatedHistoriesApp(QMainWindow):
    """Created Histories Module - Device history tracking and management"""
    
    # Master password hash (default: "admin123")
    MASTER_PASSWORD_HASH = "0192023a7bbd73250516f069df18b500"
    
    SHEETS = [
        ("Ohio", "Meters"),
        ("I&M", "Meters"),
        ("Ohio", "Transformers"),
        ("I&M", "Transformers"),
    ]
    
    def __init__(self, parent_theme="Light"):
        super().__init__()
        
        self.setWindowTitle("Created Histories - Device History Management")
        self.setGeometry(50, 50, 1600, 900)
        self.edit_mode = False
        self.current_theme = parent_theme
        
        # Initialize database
        self.db = InventoryDatabase('created_histories.db')
        self.db.init_db()
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        if self.current_theme == "Dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def toggle_edit_mode(self):
        """Toggle edit mode with password protection"""
        if self.edit_mode:
            # Disable edit mode
            self.edit_mode = False
            self.mode_label.setText("🔒 Read-Only Mode")
            self.toggle_mode_btn.setText("🔓 Enable Edit Mode")
            self.toggle_mode_btn.setStyleSheet("background-color: #e74c3c; color: white;")
            QMessageBox.information(self, "Edit Mode", "Edit mode disabled")
        else:
            # Request password
            dialog = PasswordDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.get_password()
                password_hash = hashlib.md5(password.encode()).hexdigest()
                
                if password_hash == self.MASTER_PASSWORD_HASH:
                    self.edit_mode = True
                    self.mode_label.setText("🔓 Edit Mode Active")
                    self.toggle_mode_btn.setText("🔒 Disable Edit Mode")
                    self.toggle_mode_btn.setStyleSheet("background-color: #27ae60; color: white;")
                    QMessageBox.information(self, "Edit Mode", "Edit mode enabled!")
                else:
                    QMessageBox.warning(self, "Error", "Incorrect password")
    
    def load_sheet_data(self, widget):
        """Load data for a sheet"""
        try:
            widget.table.setRowCount(0)
            items = self.db.get_items_by_sheet(widget.opco, widget.device_type)
            widget.table.setRowCount(len(items))
            
            for row_idx, item in enumerate(items):
                for col_idx, value in enumerate(item):
                    cell = QTableWidgetItem(str(value) if value else "")
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    widget.table.setItem(row_idx, col_idx, cell)
            
            widget.status_label.setText(f"Loaded {len(items)} records")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {e}")
    
    def search_records(self, widget):
        """Search records in sheet"""
        search_type_map = {
            "Device Code": "dev_code",
            "PO Number": "po_number",
            "Received Date": "recv_date"
        }
        
        search_type = search_type_map[widget.search_type_combo.currentText()]
        search_value = widget.search_input.text().strip()
        
        if not search_value:
            QMessageBox.warning(self, "Warning", "Please enter a search value")
            return
        
        try:
            widget.table.setRowCount(0)
            items = self.db.search_items(widget.opco, widget.device_type, search_type, search_value)
            widget.table.setRowCount(len(items))
            
            for row_idx, item in enumerate(items):
                for col_idx, value in enumerate(item):
                    cell = QTableWidgetItem(str(value) if value else "")
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    widget.table.setItem(row_idx, col_idx, cell)
            
            widget.status_label.setText(f"Found {len(items)} record(s)")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error searching: {e}")
    
    def clear_search(self, widget):
        """Clear search and reload all records"""
        widget.search_input.clear()
        self.load_sheet_data(widget)
    
    def add_record(self, widget):
        """Add new record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        dialog = AddEditDialog(self, opco=widget.opco, device_type=widget.device_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item = dialog.get_data()
            item_id = self.db.insert_item(item)
            
            if item_id > 0:
                QMessageBox.information(self, "Success", "Record added successfully")
                self.load_sheet_data(widget)
            else:
                QMessageBox.warning(self, "Error", "Failed to add record")
    
    def edit_record(self, widget):
        """Edit selected record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        current_row = widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a record to edit")
            return
        
        item_id = int(widget.table.item(current_row, 0).text())
        item = self.db.get_item_by_id(item_id)
        
        if not item:
            QMessageBox.warning(self, "Error", "Could not load record")
            return
        
        dialog = AddEditDialog(self, item=item, opco=widget.opco, device_type=widget.device_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_item = dialog.get_data()
            
            if self.db.update_item(item_id, updated_item):
                QMessageBox.information(self, "Success", "Record updated successfully")
                self.load_sheet_data(widget)
            else:
                QMessageBox.warning(self, "Error", "Failed to update record")
    
    def delete_record(self, widget):
        """Delete selected record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        current_row = widget.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a record to delete")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            item_id = int(widget.table.item(current_row, 0).text())
            
            if self.db.delete_item(item_id):
                QMessageBox.information(self, "Success", "Record deleted successfully")
                self.load_sheet_data(widget)
            else:
                QMessageBox.warning(self, "Error", "Failed to delete record")
    
    def import_csv(self, widget):
        """Import CSV or XLSX file into appropriate sheets"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
    
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
    
        if not file_path:
            return
    
        try:
            print("\n" + "="*60)
            print("IMPORT STARTED")
            print("="*60)
        
            imported_count = 0
            skipped_count = 0
            sheet_counts = {}
        
            if file_path.endswith('.xlsx'):
                print(f"File type: XLSX")
                import openpyxl
                wb = openpyxl.load_workbook(file_path)
            
                print(f"Available sheets in workbook: {wb.sheetnames}")
            
                # Map sheet names to OpCo and Device Type
                sheet_map = {
                    'OH - Meters': ('Ohio', 'Meters'),
                    'I&M - Meters': ('I&M', 'Meters'),
                    'OH - Transformers': ('Ohio', 'Transformers'),
                    'I&M - Transformers': ('I&M', 'Transformers'),
                }
            
                for sheet_name, (opco, device_type) in sheet_map.items():
                    print(f"\nChecking for sheet: '{sheet_name}'")
                    if sheet_name not in wb.sheetnames:
                        print(f"  ✗ NOT FOUND in workbook")
                        continue
                
                    print(f"  ✓ FOUND - importing data...")
                    ws = wb[sheet_name]
                    row_count = 0
                    debug_count = 0
                
                    # Skip header row
                    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                        debug_count += 1
                    
                        # Debug: show first 3 rows of every sheet
                        if debug_count <= 3:
                            print(f"    Row {row_idx}: len={len(row)}, key='{row[0] if row else 'EMPTY'}', data={row[:5] if row else 'NO DATA'}")
                    
                        # Skip empty rows
                        if not any(row):
                            print(f"    Row {row_idx}: Skipped - completely empty")
                            continue
                    
                        try:
                            # Skip if no key (first column)
                            if not row[0]:
                                if debug_count <= 3:
                                    print(f"    Row {row_idx}: Skipped - no key in first column")
                                skipped_count += 1
                                continue
                        
                            if len(row) < 17:
                                if debug_count <= 3:
                                    print(f"    Row {row_idx}: Skipped - not enough columns ({len(row)} < 17)")
                                skipped_count += 1
                                continue
                        
                            # Parse unit cost
                            unit_cost = 0.0
                            if len(row) > 11 and row[11]:
                                try:
                                    cost_val = row[11]
                                    if isinstance(cost_val, str):
                                        cost_str = cost_val.replace('$', '').replace(',', '')
                                        unit_cost = float(cost_str)
                                    else:
                                        unit_cost = float(cost_val)
                                except (ValueError, TypeError):
                                    unit_cost = 0.0
                        
                            # Parse quantity
                            qty = 0
                            if len(row) > 7 and row[7]:
                                try:
                                    qty = int(row[7])
                                except (ValueError, TypeError):
                                    qty = 0
                        
                            item = {
                                'opco': opco,
                                'device_type': device_type,
                                'status': str(row[2]) if len(row) > 2 and row[2] else '',
                                'mfr': str(row[3]) if len(row) > 3 and row[3] else '',
                                'dev_code': str(row[4]) if len(row) > 4 and row[4] else '',
                                'beg_ser': str(row[5]) if len(row) > 5 and row[5] else '',
                                'end_ser': str(row[6]) if len(row) > 6 and row[6] else '',
                                'qty': qty,
                                'po_date': str(row[8]) if len(row) > 8 and row[8] else '',
                                'po_number': str(row[9]) if len(row) > 9 and row[9] else '',
                                'recv_date': str(row[10]) if len(row) > 10 and row[10] else '',
                                'unit_cost': unit_cost,
                                'cid': str(row[12]) if len(row) > 12 and row[12] else '',
                                'me_number': str(row[13]) if len(row) > 13 and row[13] else '',
                                'pur_code': str(row[14]) if len(row) > 14 and row[14] else '',
                                'est': str(row[15]) if len(row) > 15 and row[15] else '',
                                'use': str(row[16]) if len(row) > 16 and row[16] else '',
                                'notes1': str(row[17]) if len(row) > 17 and row[17] else '',
                                'notes2': str(row[18]) if len(row) > 18 and row[18] else '',
                            }
                        
                            result = self.db.insert_item(item)
                            if result > 0:
                                imported_count += 1
                                row_count += 1
                            else:
                                skipped_count += 1
                                if debug_count <= 3:
                                    print(f"    Row {row_idx}: Failed to insert into database")
                        
                            sheet_key = f"{opco} - {device_type}"
                            sheet_counts[sheet_key] = sheet_counts.get(sheet_key, 0) + 1
                        
                        except Exception as e:
                            if debug_count <= 3:
                                print(f"    Row {row_idx}: Exception - {e}")
                            skipped_count += 1
                
                    print(f"  Sheet '{sheet_name}' complete: {row_count} rows imported (processed {debug_count} total rows)")
        
            else:
                print(f"File type: CSV")
                # CSV import code...
        
            print(f"\nTotal Imported: {imported_count}")
            print(f"Total Skipped: {skipped_count}")
            print("="*60 + "\n")
        
            # Reload all sheets
            for sheet_widget in self.sheet_widgets.values():
                self.load_sheet_data(sheet_widget)
        
            msg = f"Import Complete\n{'='*40}\n\n"
            msg += f"Total Imported: {imported_count} records\n"
            if sheet_counts:
                msg += f"\nBreakdown:\n"
                for sheet, count in sorted(sheet_counts.items()):
                    msg += f"  • {sheet}: {count} records\n"
            if skipped_count > 0:
                msg += f"Skipped: {skipped_count} rows\n"
        
            QMessageBox.information(self, "Import Complete", msg)
        
        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            QMessageBox.warning(self, "Error", f"Error importing file: {e}")
            import traceback
            traceback.print_exc()
    
    def show_statistics(self, widget):
        """Show sheet statistics"""
        try:
            stats = self.db.get_statistics(widget.opco, widget.device_type)
            
            msg = (
                f"Statistics for {widget.opco} - {widget.device_type}\n"
                f"{'='*50}\n\n"
                f"Total Records: {stats['total_items']}\n"
                f"Total Quantity: {stats['total_qty']:,}\n"
                f"Total Value: ${stats['total_value']:,.2f}\n"
                f"Average Cost per Unit: ${stats['avg_cost']:,.2f}\n"
            )
            
            QMessageBox.information(self, "Statistics", msg)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting statistics: {e}")
    
    def create_sheet_widget(self, opco: str, device_type: str) -> QWidget:
        """Create widget for a sheet"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search/Filter bar
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search by:")
        search_layout.addWidget(search_label)
        
        # Search type dropdown
        search_type_combo = QComboBox()
        search_type_combo.addItems(["Device Code", "PO Number", "Received Date"])
        search_layout.addWidget(search_type_combo)
        
        # Search input
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter search value...")
        search_layout.addWidget(search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setMinimumWidth(100)
        search_layout.addWidget(search_btn)
        
        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setMinimumWidth(80)
        search_layout.addWidget(clear_search_btn)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Record")
        add_btn.setMinimumWidth(130)
        action_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit Record")
        edit_btn.setMinimumWidth(130)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete Record")
        delete_btn.setMinimumWidth(130)
        action_layout.addWidget(delete_btn)
        
        import_btn = QPushButton("📥 Import CSV")
        import_btn.setMinimumWidth(130)
        action_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export CSV")
        export_btn.setMinimumWidth(130)
        action_layout.addWidget(export_btn)
        
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setMinimumWidth(130)
        action_layout.addWidget(stats_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Data table
        table = QTableWidget()
        table.setColumnCount(20)
        table.setHorizontalHeaderLabels([
            "ID", "OpCo", "Device Type", "Status", "MFR", "Dev Code", "Beg Ser", "End Ser",
            "Qty", "PO Date", "PO Number", "Recv Date", "Unit Cost", "CID",
            "M.E. #", "Pur. Code", "Est.", "Use", "Notes 1", "Notes 2"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(table)
        
        # Status bar
        status_label = QLabel("Ready")
        layout.addWidget(status_label)
        
        widget.setLayout(layout)
        
        # Store references
        widget.table = table
        widget.status_label = status_label
        widget.search_input = search_input
        widget.search_type_combo = search_type_combo
        widget.opco = opco
        widget.device_type = device_type
        
        # Connect buttons
        add_btn.clicked.connect(lambda: self.add_record(widget))
        edit_btn.clicked.connect(lambda: self.edit_record(widget))
        delete_btn.clicked.connect(lambda: self.delete_record(widget))
        import_btn.clicked.connect(lambda: self.import_csv(widget))
        export_btn.clicked.connect(lambda: self.export_csv(widget))
        stats_btn.clicked.connect(lambda: self.show_statistics(widget))
        search_btn.clicked.connect(lambda: self.search_records(widget))
        clear_search_btn.clicked.connect(lambda: self.clear_search(widget))
        
        # Load initial data
        self.load_sheet_data(widget)
        
        return widget
    
    def setup_ui(self):
        """Setup main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Header with title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Created Histories - Device History Management")
        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.mode_label = QLabel("🔒 Read-Only Mode")
        self.mode_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(self.mode_label)
        
        self.toggle_mode_btn = QPushButton("🔓 Enable Edit Mode")
        self.toggle_mode_btn.setMinimumWidth(150)
        self.toggle_mode_btn.clicked.connect(self.toggle_edit_mode)
        header_layout.addWidget(self.toggle_mode_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tabbed interface for sheets
        self.tabs = QTabWidget()
        self.sheet_widgets = {}
        
        for opco, device_type in self.SHEETS:
            sheet_name = f"{opco} - {device_type}"
            widget = self.create_sheet_widget(opco, device_type)
            self.sheet_widgets[sheet_name] = widget
            self.tabs.addTab(widget, sheet_name)
        
        main_layout.addWidget(self.tabs)
        
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Exit', self.close)
        
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Toggle Edit Mode', self.toggle_edit_mode)
        
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Light Theme', self.apply_light_theme)
        view_menu.addAction('Dark Theme', self.apply_dark_theme)
        
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def apply_light_theme(self):
        """Apply light theme"""
        self.current_theme = "Light"
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                border: 1px solid #bdc3c7;
                padding: 6px;
                border-radius: 4px;
                background-color: #ffffff;
                color: #333333;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
                background-color: #ffffff;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 20px;
                border: 1px solid #bdc3c7;
                color: #333333;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QMenuBar {
                background-color: #34495e;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #ffffff;
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLabel {
                color: #333333;
            }
        """)

    def apply_dark_theme(self):
        """Apply dark theme"""
        self.current_theme = "Dark"
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QTableWidget {
                border: 1px solid #555555;
                gridline-color: #444444;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                padding: 8px 20px;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QMenuBar {
                background-color: #1a1a1a;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def show_about(self):
        """Show about dialog"""
        msg = (
            "Created Histories v2.0.0\n\n"
            "Device History Tracking System\n\n"
            "Features:\n"
            "• Multi-sheet support (OpCo and Device Type)\n"
            "• Add/Edit/Delete records\n"
            "• Advanced search and filtering\n"
            "• Import/Export CSV\n"
            "• Password-protected edit mode\n"
            "• Comprehensive statistics\n\n"
            "Created with PyQt6"
        )
        QMessageBox.information(self, "About", msg)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = CreatedHistoriesApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()