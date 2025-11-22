"""
Enhanced Data Grid - Professional table widget with advanced features
"""

from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView,
                            QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class EnhancedDataGrid(QWidget):
    """Enhanced data grid with sorting, filtering, and row details"""
    
    row_selected = pyqtSignal(int)
    row_double_clicked = pyqtSignal(int)
    
    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.data = []
        self.filtered_data = []
        self.sort_column = -1
        self.sort_order = Qt.SortOrder.AscendingOrder
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup grid UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        
        # Enable alternating row colors
        self.table.setAlternatingRowColors(True)
        
        # Configure header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.sort_by_column)
        
        # Selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_double_clicked)
        
        # Enable sorting
        self.table.setSortingEnabled(False)  # We'll handle sorting manually
        
        layout.addWidget(self.table)
        
        # Status bar
        self.status_bar = self.create_status_bar()
        layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
    
    def create_status_bar(self) -> QFrame:
        """Create status bar"""
        status_frame = QFrame()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("class", "caption")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.row_count_label = QLabel("0 rows")
        self.row_count_label.setProperty("class", "caption")
        status_layout.addWidget(self.row_count_label)
        
        status_frame.setLayout(status_layout)
        return status_frame
    
    def set_data(self, data: list):
        """Set grid data"""
        self.data = data
        self.filtered_data = data.copy()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the table display"""
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.filtered_data))
        
        for row_idx, row_data in enumerate(self.filtered_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Add data type indicator styling
                if isinstance(value, (int, float)):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                self.table.setItem(row_idx, col_idx, item)
        
        # Update status
        self.update_status()
    
    def update_status(self):
        """Update status bar"""
        total = len(self.data)
        filtered = len(self.filtered_data)
        
        if filtered == total:
            self.row_count_label.setText(f"{total} rows")
            self.status_label.setText("Ready")
        else:
            self.row_count_label.setText(f"{filtered} of {total} rows")
            self.status_label.setText(f"Filtered")
    
    def sort_by_column(self, column: int):
        """Sort by column"""
        if self.sort_column == column:
            # Toggle sort order
            self.sort_order = (Qt.SortOrder.DescendingOrder 
                             if self.sort_order == Qt.SortOrder.AscendingOrder 
                             else Qt.SortOrder.AscendingOrder)
        else:
            self.sort_column = column
            self.sort_order = Qt.SortOrder.AscendingOrder
        
        # Sort data
        reverse = self.sort_order == Qt.SortOrder.DescendingOrder
        self.filtered_data.sort(key=lambda x: x[column] if x[column] is not None else "", 
                               reverse=reverse)
        
        self.refresh_display()
        self.status_label.setText(f"Sorted by {self.columns[column]}")
    
    def filter_data(self, column: int, value: str):
        """Filter data by column value"""
        if not value:
            self.filtered_data = self.data.copy()
        else:
            self.filtered_data = [
                row for row in self.data 
                if value.lower() in str(row[column]).lower()
            ]
        
        self.refresh_display()
    
    def clear_filters(self):
        """Clear all filters"""
        self.filtered_data = self.data.copy()
        self.refresh_display()
    
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.row_selected.emit(current_row)
    
    def on_double_clicked(self, item):
        """Handle double click"""
        if item:
            self.row_double_clicked.emit(item.row())
    
    def get_selected_row(self):
        """Get selected row index"""
        return self.table.currentRow()
    
    def get_selected_data(self):
        """Get selected row data"""
        row_idx = self.table.currentRow()
        if row_idx >= 0 and row_idx < len(self.filtered_data):
            return self.filtered_data[row_idx]
        return None
    
    def highlight_row(self, row: int, color: QColor):
        """Highlight a specific row"""
        if 0 <= row < self.table.rowCount():
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(color)
    
    def clear_highlights(self):
        """Clear all row highlights"""
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor(0, 0, 0, 0))  # Transparent


class DataGridToolbar(QWidget):
    """Toolbar for data grid operations"""
    
    search_requested = pyqtSignal(str)
    filter_requested = pyqtSignal()
    export_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup toolbar UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.search_requested.emit)
        layout.addWidget(self.search_input)
        
        layout.addStretch()
        
        # Filter button
        filter_btn = QPushButton("🔽 Filters")
        filter_btn.setProperty("class", "secondary")
        filter_btn.clicked.connect(self.filter_requested.emit)
        layout.addWidget(filter_btn)
        
        # Export button
        export_btn = QPushButton("📤 Export")
        export_btn.setProperty("class", "secondary")
        export_btn.clicked.connect(self.export_requested.emit)
        layout.addWidget(export_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
