"""
Created Histories Module - Modern Professional UI
Enhanced with dashboard, advanced filtering, and professional design
"""

import sys
import csv
import hashlib
import openpyxl
from datetime import datetime
from typing import Dict, List, Any

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog,
                            QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit,
                            QStackedWidget, QSplitter, QFrame, QScrollArea,
                            QGridLayout)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QAction

from inventory_db import InventoryDatabase
from ui_components.theme import ThemeManager, ColorScheme
from ui_components.dashboard_cards import MetricCard, StatisticsCard, InfoCard
from ui_components.enhanced_grid import EnhancedDataGrid, DataGridToolbar
from ui_components.filter_sidebar import FilterSidebar
from ui_components.form_builder import FormBuilder
from ui_components.validation_feedback import ValidationFeedback, Validator
from ui_components.status_indicators import StatusIndicator, ProgressIndicator


class PasswordDialog(QDialog):
    """Dialog for entering edit mode password"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Mode")
        self.setModal(True)
        self.setFixedSize(350, 150)
        
        layout = QFormLayout()
        layout.setSpacing(12)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.accept)
        
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


class ModernAddEditDialog(QDialog):
    """Modern dialog for adding/editing records with validation"""
    
    def __init__(self, parent=None, item=None, opco=None, device_type=None):
        super().__init__(parent)
        self.item = item
        self.opco = opco
        self.device_type = device_type
        
        self.setWindowTitle("Edit Record" if item else "Add New Record")
        self.setMinimumSize(700, 750)
        
        self.setup_ui()
        
        if item:
            self.populate_form()
    
    def setup_ui(self):
        """Setup dialog UI with modern form builder"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Edit Record" if self.item else "New Record")
        title_label.setProperty("class", "heading")
        layout.addWidget(title_label)
        
        # Form builder
        self.form = FormBuilder(self)
        
        # Device Information Group
        device_group = self.form.add_group("Device Information")
        
        # Read-only fields
        opco_field = QLineEdit()
        opco_field.setText(self.opco or "")
        opco_field.setReadOnly(True)
        device_group.add_field("OpCo", opco_field)
        
        device_type_field = QLineEdit()
        device_type_field.setText(self.device_type or "")
        device_type_field.setReadOnly(True)
        device_group.add_field("Device Type", device_type_field)
        
        self.form.add_field_to_group("Device Information", "Status", "text",
                                     placeholder="Active, Inactive, etc.")
        self.form.add_field_to_group("Device Information", "Manufacturer", "text",
                                     placeholder="Device manufacturer")
        self.form.add_field_to_group("Device Information", "Device Code", "text",
                                     required=True, placeholder="Unique device code")
        
        # Serial Numbers Group
        self.form.add_field_to_group("Serial Numbers", "Beginning Serial", "text",
                                     placeholder="Starting serial number")
        self.form.add_field_to_group("Serial Numbers", "Ending Serial", "text",
                                     placeholder="Ending serial number")
        self.form.add_field_to_group("Serial Numbers", "Quantity", "number",
                                     min=0, max=100000)
        
        # Purchase Information Group
        self.form.add_field_to_group("Purchase Information", "PO Date", "text",
                                     placeholder="YYYY-MM-DD")
        self.form.add_field_to_group("Purchase Information", "PO Number", "text",
                                     placeholder="Purchase order number")
        self.form.add_field_to_group("Purchase Information", "Received Date", "text",
                                     placeholder="YYYY-MM-DD")
        self.form.add_field_to_group("Purchase Information", "Unit Cost", "decimal",
                                     min=0.0, max=999999.99, decimals=2)
        
        # Additional Information Group
        self.form.add_field_to_group("Additional Information", "CID", "text",
                                     placeholder="Customer ID")
        self.form.add_field_to_group("Additional Information", "M.E. #", "text",
                                     placeholder="M.E. Number")
        self.form.add_field_to_group("Additional Information", "Purchase Code", "text",
                                     placeholder="Purchase code")
        self.form.add_field_to_group("Additional Information", "Est.", "text",
                                     placeholder="Estimate")
        self.form.add_field_to_group("Additional Information", "Use", "text",
                                     placeholder="Usage type")
        
        # Notes Group
        self.form.add_field_to_group("Notes", "Notes 1", "multiline",
                                     height=60, placeholder="Additional notes...")
        self.form.add_field_to_group("Notes", "Notes 2", "multiline",
                                     height=60, placeholder="Additional notes...")
        
        layout.addWidget(self.form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save Record")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def populate_form(self):
        """Populate form with existing item data"""
        if not self.item:
            return
        
        # Map field labels to item keys
        field_mapping = {
            ("Device Information", "Status"): 'status',
            ("Device Information", "Manufacturer"): 'mfr',
            ("Device Information", "Device Code"): 'dev_code',
            ("Serial Numbers", "Beginning Serial"): 'beg_ser',
            ("Serial Numbers", "Ending Serial"): 'end_ser',
            ("Serial Numbers", "Quantity"): 'qty',
            ("Purchase Information", "PO Date"): 'po_date',
            ("Purchase Information", "PO Number"): 'po_number',
            ("Purchase Information", "Received Date"): 'recv_date',
            ("Purchase Information", "Unit Cost"): 'unit_cost',
            ("Additional Information", "CID"): 'cid',
            ("Additional Information", "M.E. #"): 'me_number',
            ("Additional Information", "Purchase Code"): 'pur_code',
            ("Additional Information", "Est."): 'est',
            ("Additional Information", "Use"): 'use',
            ("Notes", "Notes 1"): 'notes1',
            ("Notes", "Notes 2"): 'notes2',
        }
        
        for (group, field), key in field_mapping.items():
            value = self.item.get(key, '')
            if value is not None:
                group_widget = self.form.groups.get(group)
                if group_widget:
                    group_widget.set_value(field, value)
    
    def get_data(self):
        """Get form data"""
        values = self.form.get_all_values()
        
        return {
            'opco': self.opco,
            'device_type': self.device_type,
            'status': values.get('Device Information', {}).get('Status', ''),
            'mfr': values.get('Device Information', {}).get('Manufacturer', ''),
            'dev_code': values.get('Device Information', {}).get('Device Code', ''),
            'beg_ser': values.get('Serial Numbers', {}).get('Beginning Serial', ''),
            'end_ser': values.get('Serial Numbers', {}).get('Ending Serial', ''),
            'qty': values.get('Serial Numbers', {}).get('Quantity', 0),
            'po_date': values.get('Purchase Information', {}).get('PO Date', ''),
            'po_number': values.get('Purchase Information', {}).get('PO Number', ''),
            'recv_date': values.get('Purchase Information', {}).get('Received Date', ''),
            'unit_cost': values.get('Purchase Information', {}).get('Unit Cost', 0.0),
            'cid': values.get('Additional Information', {}).get('CID', ''),
            'me_number': values.get('Additional Information', {}).get('M.E. #', ''),
            'pur_code': values.get('Additional Information', {}).get('Purchase Code', ''),
            'est': values.get('Additional Information', {}).get('Est.', ''),
            'use': values.get('Additional Information', {}).get('Use', ''),
            'notes1': values.get('Notes', {}).get('Notes 1', ''),
            'notes2': values.get('Notes', {}).get('Notes 2', ''),
        }


class CreatedHistoriesApp(QMainWindow):
    """Modern Created Histories Application"""
    
    # Master password hash (default: "admin123")
    MASTER_PASSWORD_HASH = "0192023a7bbd73250516f069df18b500"
    
    SHEETS = [
        ("Ohio", "Meters"),
        ("I&M", "Meters"),
        ("Ohio", "Transformers"),
        ("I&M", "Transformers"),
    ]
    
    COLUMNS = [
        "ID", "OpCo", "Device Type", "Status", "MFR", "Dev Code", "Beg Ser", "End Ser",
        "Qty", "PO Date", "PO Number", "Recv Date", "Unit Cost", "CID",
        "M.E. #", "Pur. Code", "Est.", "Use", "Notes 1", "Notes 2"
    ]
    
    # Sheet name mapping for import
    SHEET_MAP = {
        'OH - Meters': ('Ohio', 'Meters'),
        'I&M - Meters': ('I&M', 'Meters'),
        'OH - Transformers': ('Ohio', 'Transformers'),
        'I&M - Transformers': ('I&M', 'Transformers'),
    }
    
    # Sidebar configuration constants
    SIDEBAR_EXPANDED_WIDTH = 260
    SIDEBAR_COLLAPSED_WIDTH = 50
    SIDEBAR_ANIMATION_DURATION = 200  # milliseconds
    RESPONSIVE_BREAKPOINT_WIDTH = 1200  # pixels
    SIDEBAR_STATE_AUTO = "auto"
    SIDEBAR_STATE_MANUAL = "manual"
    
    def __init__(self, parent_theme="Light"):
        super().__init__()
        
        self.setWindowTitle("Created Histories - Device History Management")
        self.setGeometry(50, 50, 1600, 900)
        self.edit_mode = False
        self.current_theme = parent_theme
        self.current_sheet = None
        
        # Initialize database
        self.db = InventoryDatabase('created_histories.db')
        self.db.init_db()
        
        # Sidebar state
        self.sidebar_collapsed = False
        self.sidebar_manual_state_cache = None  # Cache for performance
        self.sidebar_animation = None  # Reusable animation object
        self.sidebar_max_animation = None  # Reusable animation object
        self.last_responsive_width_state = None  # Track last responsive state to prevent duplicate triggers
        
        # Setup UI
        self.setup_ui()
        
        # Setup keyboard shortcut for sidebar toggle
        self.sidebar_shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.sidebar_shortcut.activated.connect(self.toggle_sidebar)
        
        # Apply theme
        self.apply_theme(self.current_theme)
        
        # Load sidebar state from database
        self.load_sidebar_state()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def setup_ui(self):
        """Setup modern UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar for sheet selection
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header/toolbar
        self.header = self.create_header()
        content_layout.addWidget(self.header)
        
        # Stacked widget for different views
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # Create views
        self.dashboard_view = self.create_dashboard_view()
        self.stack.addWidget(self.dashboard_view)
        
        # Create sheet views
        self.sheet_views = {}
        for opco, device_type in self.SHEETS:
            sheet_name = f"{opco} - {device_type}"
            view = self.create_sheet_view(opco, device_type)
            self.sheet_views[sheet_name] = view
            self.stack.addWidget(view)
        
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_header(self) -> QWidget:
        """Create header with breadcrumb and actions"""
        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        header.setMinimumHeight(70)
        header.setMaximumHeight(70)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 12, 24, 12)
        
        # Sidebar toggle button
        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setProperty("class", "secondary")
        self.sidebar_toggle_btn.setMinimumSize(44, 44)
        self.sidebar_toggle_btn.setMaximumSize(44, 44)
        self.sidebar_toggle_btn.setToolTip("Toggle Sidebar (Alt+S)")
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.sidebar_toggle_btn.setAccessibleName("Toggle Sidebar")
        self.sidebar_toggle_btn.setAccessibleDescription("Collapse or expand the sidebar navigation")
        layout.addWidget(self.sidebar_toggle_btn)
        
        # Breadcrumb navigation
        breadcrumb_layout = QVBoxLayout()
        
        self.breadcrumb_label = QLabel("Dashboard")
        self.breadcrumb_label.setProperty("class", "heading")
        breadcrumb_layout.addWidget(self.breadcrumb_label)
        
        self.subtitle_label = QLabel("Overview of all device histories")
        self.subtitle_label.setProperty("class", "caption")
        breadcrumb_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(breadcrumb_layout)
        
        layout.addStretch()
        
        # Status indicator
        self.mode_indicator = StatusIndicator('inactive', 'Read-Only')
        layout.addWidget(self.mode_indicator)
        
        # Edit mode toggle
        self.toggle_mode_btn = QPushButton("🔓 Enable Edit Mode")
        self.toggle_mode_btn.setMinimumWidth(160)
        self.toggle_mode_btn.clicked.connect(self.toggle_edit_mode)
        layout.addWidget(self.toggle_mode_btn)
        
        header.setLayout(layout)
        return header
    
    def create_sidebar(self) -> QFrame:
        """Create modern sidebar with collapsible support"""
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setMinimumWidth(self.SIDEBAR_EXPANDED_WIDTH)
        sidebar.setMaximumWidth(self.SIDEBAR_EXPANDED_WIDTH)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)
        
        # Logo/Title
        self.sidebar_title = QLabel("📊 Created Histories")
        self.sidebar_title.setProperty("class", "subheading")
        self.sidebar_title.setStyleSheet("padding: 8px; margin-bottom: 16px;")
        layout.addWidget(self.sidebar_title)
        
        # Dashboard button
        dashboard_btn = QPushButton("🏠 Dashboard")
        dashboard_btn.setProperty("class", "secondary")
        dashboard_btn.setMinimumHeight(44)
        dashboard_btn.setToolTip("Dashboard")
        dashboard_btn.clicked.connect(self.show_dashboard)
        dashboard_btn.setAccessibleName("Dashboard")
        layout.addWidget(dashboard_btn)
        self.dashboard_btn = dashboard_btn
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("margin: 12px 0;")
        layout.addWidget(separator)
        
        # Sheets section
        self.sheets_label = QLabel("SHEETS")
        self.sheets_label.setProperty("class", "caption")
        self.sheets_label.setStyleSheet("font-weight: 600; padding: 8px; text-transform: uppercase; letter-spacing: 0.5px;")
        layout.addWidget(self.sheets_label)
        
        # Sheet buttons
        self.sheet_buttons = {}
        for opco, device_type in self.SHEETS:
            sheet_name = f"{opco} - {device_type}"
            btn = QPushButton(f"📋 {sheet_name}")
            btn.setProperty("class", "secondary")
            btn.setMinimumHeight(44)
            btn.setToolTip(sheet_name)
            btn.clicked.connect(lambda checked, name=sheet_name: self.show_sheet(name))
            btn.setAccessibleName(sheet_name)
            layout.addWidget(btn)
            self.sheet_buttons[sheet_name] = btn
        
        layout.addStretch()
        
        # Version info
        self.version_label = QLabel("v2.0.0")
        self.version_label.setProperty("class", "caption")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.version_label)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_dashboard_view(self) -> QWidget:
        """Create dashboard with metrics"""
        dashboard = QScrollArea()
        dashboard.setWidgetResizable(True)
        dashboard.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Metrics cards
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(16)
        
        self.total_records_card = MetricCard("Total Records", "0", "📊")
        metrics_layout.addWidget(self.total_records_card, 0, 0)
        
        self.total_devices_card = MetricCard("Total Devices", "0", "🔧")
        metrics_layout.addWidget(self.total_devices_card, 0, 1)
        
        self.total_value_card = MetricCard("Total Value", "$0", "💰")
        metrics_layout.addWidget(self.total_value_card, 0, 2)
        
        self.avg_cost_card = MetricCard("Avg. Unit Cost", "$0", "📈")
        metrics_layout.addWidget(self.avg_cost_card, 0, 3)
        
        layout.addLayout(metrics_layout)
        
        # Sheet statistics
        sheets_label = QLabel("Sheet Statistics")
        sheets_label.setProperty("class", "subheading")
        layout.addWidget(sheets_label)
        
        sheets_grid = QGridLayout()
        sheets_grid.setSpacing(16)
        
        self.sheet_stats_cards = {}
        for idx, (opco, device_type) in enumerate(self.SHEETS):
            sheet_name = f"{opco} - {device_type}"
            card = StatisticsCard(sheet_name, {})
            sheets_grid.addWidget(card, idx // 2, idx % 2)
            self.sheet_stats_cards[sheet_name] = card
        
        layout.addLayout(sheets_grid)
        
        layout.addStretch()
        
        container.setLayout(layout)
        dashboard.setWidget(container)
        
        return dashboard
    
    def create_sheet_view(self, opco: str, device_type: str) -> QWidget:
        """Create modern sheet view with grid and filters"""
        view = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main content
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(16)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)
        
        add_btn = QPushButton("➕ Add Record")
        add_btn.clicked.connect(lambda: self.add_record(opco, device_type))
        toolbar_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setProperty("class", "secondary")
        edit_btn.clicked.connect(lambda: self.edit_record(opco, device_type))
        toolbar_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setProperty("class", "error")
        delete_btn.clicked.connect(lambda: self.delete_record(opco, device_type))
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        
        import_btn = QPushButton("📥 Import")
        import_btn.setProperty("class", "secondary")
        import_btn.clicked.connect(lambda: self.import_data(opco, device_type))
        toolbar_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.setProperty("class", "secondary")
        export_btn.clicked.connect(lambda: self.export_data(opco, device_type))
        toolbar_layout.addWidget(export_btn)
        
        stats_btn = QPushButton("📊 Statistics")
        stats_btn.setProperty("class", "secondary")
        stats_btn.clicked.connect(lambda: self.show_statistics(opco, device_type))
        toolbar_layout.addWidget(stats_btn)
        
        filter_btn = QPushButton("🔽 Filters")
        filter_btn.setProperty("class", "secondary")
        filter_btn.setCheckable(True)
        filter_btn.clicked.connect(lambda checked: self.toggle_filters(opco, device_type, checked))
        toolbar_layout.addWidget(filter_btn)
        
        content_layout.addLayout(toolbar_layout)
        
        # Enhanced data grid
        grid = EnhancedDataGrid(self.COLUMNS)
        grid.row_double_clicked.connect(lambda row: self.edit_record(opco, device_type))
        content_layout.addWidget(grid)
        
        content_widget.setLayout(content_layout)
        
        # Splitter for filter sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(content_widget)
        
        # Filter sidebar (initially hidden)
        filter_sidebar = FilterSidebar(self.COLUMNS)
        filter_sidebar.apply_filters.connect(lambda filters: self.apply_filters(opco, device_type, filters))
        filter_sidebar.clear_filters.connect(lambda: self.load_sheet_data(opco, device_type))
        filter_sidebar.hide()
        splitter.addWidget(filter_sidebar)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        layout.addWidget(splitter)
        view.setLayout(layout)
        
        # Store references
        view.grid = grid
        view.filter_sidebar = filter_sidebar
        view.filter_btn = filter_btn
        view.opco = opco
        view.device_type = device_type
        
        return view
    
    def toggle_filters(self, opco: str, device_type: str, show: bool):
        """Toggle filter sidebar"""
        sheet_name = f"{opco} - {device_type}"
        view = self.sheet_views.get(sheet_name)
        if view:
            if show:
                view.filter_sidebar.show()
            else:
                view.filter_sidebar.hide()
    
    def apply_filters(self, opco: str, device_type: str, filters: Dict):
        """Apply filters to grid"""
        sheet_name = f"{opco} - {device_type}"
        view = self.sheet_views.get(sheet_name)
        if not view:
            return
        
        try:
            # Get all data for the sheet
            all_items = self.db.get_items_by_sheet(opco, device_type)
            
            # Apply filter conditions
            logic = filters.get('logic', 'AND')
            conditions = filters.get('conditions', [])
            
            if not conditions or not any(c.get('value') for c in conditions):
                # No valid filters, show all data
                view.grid.set_data(all_items)
                return
            
            # Filter the data
            filtered_items = []
            
            for item in all_items:
                # Check each condition
                condition_results = []
                
                for condition in conditions:
                    field = condition.get('field', '')
                    operator = condition.get('operator', '')
                    value = condition.get('value', '')
                    
                    if not value:
                        continue
                    
                    # Map field name to column index
                    try:
                        col_idx = self.COLUMNS.index(field)
                        item_value = str(item[col_idx]) if item[col_idx] is not None else ""
                    except (ValueError, IndexError):
                        continue
                    
                    # Apply operator
                    result = False
                    value_lower = value.lower()
                    item_value_lower = item_value.lower()
                    
                    if operator == "Contains":
                        result = value_lower in item_value_lower
                    elif operator == "Equals":
                        result = item_value_lower == value_lower
                    elif operator == "Starts with":
                        result = item_value_lower.startswith(value_lower)
                    elif operator == "Ends with":
                        result = item_value_lower.endswith(value_lower)
                    elif operator == "Greater than":
                        try:
                            result = float(item_value) > float(value)
                        except (ValueError, TypeError):
                            result = False
                    elif operator == "Less than":
                        try:
                            result = float(item_value) < float(value)
                        except (ValueError, TypeError):
                            result = False
                    elif operator == "Is empty":
                        result = not item_value
                    elif operator == "Is not empty":
                        result = bool(item_value)
                    
                    condition_results.append(result)
                
                # Combine results based on logic
                if condition_results:
                    if logic == 'AND':
                        if all(condition_results):
                            filtered_items.append(item)
                    else:  # OR
                        if any(condition_results):
                            filtered_items.append(item)
            
            # Update grid with filtered data
            view.grid.set_data(filtered_items)
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            # Fallback to showing all data
            self.load_sheet_data(opco, device_type)
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.stack.setCurrentWidget(self.dashboard_view)
        self.breadcrumb_label.setText("Dashboard")
        self.subtitle_label.setText("Overview of all device histories")
        self.current_sheet = None
        self.update_dashboard_metrics()
    
    def show_sheet(self, sheet_name: str):
        """Show specific sheet"""
        view = self.sheet_views.get(sheet_name)
        if view:
            self.stack.setCurrentWidget(view)
            self.breadcrumb_label.setText(sheet_name)
            self.subtitle_label.setText(f"Manage {sheet_name} device records")
            self.current_sheet = sheet_name
            self.load_sheet_data(view.opco, view.device_type)
    
    def load_sheet_data(self, opco: str, device_type: str):
        """Load data for sheet"""
        try:
            sheet_name = f"{opco} - {device_type}"
            view = self.sheet_views.get(sheet_name)
            if not view:
                return
            
            items = self.db.get_items_by_sheet(opco, device_type)
            view.grid.set_data(items)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading data: {e}")
    
    def update_dashboard_metrics(self):
        """Update dashboard metrics"""
        try:
            total_records = 0
            total_qty = 0
            total_value = 0.0
            costs = []
            
            for opco, device_type in self.SHEETS:
                stats = self.db.get_statistics(opco, device_type)
                
                total_records += stats.get('total_items', 0)
                total_qty += stats.get('total_qty', 0)
                total_value += stats.get('total_value', 0.0)
                
                avg_cost = stats.get('avg_cost', 0.0)
                if avg_cost > 0:
                    costs.append(avg_cost)
                
                # Update sheet card
                sheet_name = f"{opco} - {device_type}"
                card = self.sheet_stats_cards.get(sheet_name)
                if card:
                    card.update_stats({
                        'Records': stats.get('total_items', 0),
                        'Devices': stats.get('total_qty', 0),
                        'Value': f"${stats.get('total_value', 0.0):,.2f}"
                    })
            
            # Update metric cards
            self.total_records_card.update_value(f"{total_records:,}")
            self.total_devices_card.update_value(f"{total_qty:,}")
            self.total_value_card.update_value(f"${total_value:,.2f}")
            
            avg_cost = sum(costs) / len(costs) if costs else 0
            self.avg_cost_card.update_value(f"${avg_cost:,.2f}")
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def toggle_edit_mode(self):
        """Toggle edit mode with password"""
        if self.edit_mode:
            self.edit_mode = False
            self.mode_indicator.update_status('inactive', 'Read-Only')
            self.toggle_mode_btn.setText("🔓 Enable Edit Mode")
            QMessageBox.information(self, "Edit Mode", "Edit mode disabled")
        else:
            dialog = PasswordDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.get_password()
                password_hash = hashlib.md5(password.encode()).hexdigest()
                
                if password_hash == self.MASTER_PASSWORD_HASH:
                    self.edit_mode = True
                    self.mode_indicator.update_status('success', 'Edit Mode')
                    self.toggle_mode_btn.setText("🔒 Disable Edit Mode")
                    QMessageBox.information(self, "Edit Mode", "Edit mode enabled!")
                else:
                    QMessageBox.warning(self, "Error", "Incorrect password")
    
    def toggle_sidebar(self):
        """Toggle sidebar collapsed/expanded state with animation"""
        if self.sidebar_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()
    
    def _set_button_texts_collapsed(self):
        """Set button texts to icon-only mode"""
        self.dashboard_btn.setText("🏠")
        for sheet_name, btn in self.sheet_buttons.items():
            btn.setText("◆")
    
    def _set_button_texts_expanded(self):
        """Restore button texts to full mode"""
        self.dashboard_btn.setText("🏠 Dashboard")
        for opco, device_type in self.SHEETS:
            sheet_name = f"{opco} - {device_type}"
            btn = self.sheet_buttons.get(sheet_name)
            if btn:
                btn.setText(f"📋 {sheet_name}")
    
    def _update_sidebar_visual_state(self, collapsed: bool, animate: bool = True):
        """Update sidebar visual state (width, buttons, labels)"""
        if animate:
            # Stop any existing animations to prevent conflicts
            if self.sidebar_animation is not None and self.sidebar_animation.state() == QPropertyAnimation.State.Running:
                self.sidebar_animation.stop()
            if self.sidebar_max_animation is not None and self.sidebar_max_animation.state() == QPropertyAnimation.State.Running:
                self.sidebar_max_animation.stop()
            
            # Create or reuse animation objects
            if self.sidebar_animation is None:
                self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
                self.sidebar_max_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            
            self.sidebar_animation.setDuration(self.SIDEBAR_ANIMATION_DURATION)
            self.sidebar_max_animation.setDuration(self.SIDEBAR_ANIMATION_DURATION)
            
            if collapsed:
                self.sidebar_animation.setStartValue(self.SIDEBAR_EXPANDED_WIDTH)
                self.sidebar_animation.setEndValue(self.SIDEBAR_COLLAPSED_WIDTH)
                self.sidebar_max_animation.setStartValue(self.SIDEBAR_EXPANDED_WIDTH)
                self.sidebar_max_animation.setEndValue(self.SIDEBAR_COLLAPSED_WIDTH)
            else:
                self.sidebar_animation.setStartValue(self.SIDEBAR_COLLAPSED_WIDTH)
                self.sidebar_animation.setEndValue(self.SIDEBAR_EXPANDED_WIDTH)
                self.sidebar_max_animation.setStartValue(self.SIDEBAR_COLLAPSED_WIDTH)
                self.sidebar_max_animation.setEndValue(self.SIDEBAR_EXPANDED_WIDTH)
            
            self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.sidebar_max_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Disconnect any previous connections to avoid duplicates
            try:
                self.sidebar_animation.finished.disconnect()
            except TypeError:
                pass  # No previous connection
            
            # Update UI elements after animation completes
            self.sidebar_animation.finished.connect(lambda: self._update_sidebar_ui_elements(collapsed))
            
            # Start animations
            self.sidebar_animation.start()
            self.sidebar_max_animation.start()
        else:
            # Set width immediately without animation
            width = self.SIDEBAR_COLLAPSED_WIDTH if collapsed else self.SIDEBAR_EXPANDED_WIDTH
            self.sidebar.setMinimumWidth(width)
            self.sidebar.setMaximumWidth(width)
            self._update_sidebar_ui_elements(collapsed)
    
    def _update_sidebar_ui_elements(self, collapsed: bool):
        """Update button texts and labels based on collapsed state"""
        # Update button texts and labels
        if collapsed:
            self._set_button_texts_collapsed()
            self.sidebar_title.hide()
            self.sheets_label.hide()
            self.version_label.hide()
        else:
            self._set_button_texts_expanded()
            self.sidebar_title.show()
            self.sheets_label.show()
            self.version_label.show()
    
    def collapse_sidebar(self):
        """Collapse sidebar with animation"""
        self._update_sidebar_visual_state(collapsed=True, animate=True)
        self.sidebar_collapsed = True
        self.save_sidebar_state()
    
    def expand_sidebar(self):
        """Expand sidebar with animation"""
        self._update_sidebar_visual_state(collapsed=False, animate=True)
        self.sidebar_collapsed = False
        self.save_sidebar_state()
    
    def save_sidebar_state(self):
        """Save sidebar state to database"""
        state = "collapsed" if self.sidebar_collapsed else "expanded"
        # Batch both preferences in a single database transaction for performance
        self.db.set_preferences_batch({
            "sidebar_state": state,
            "sidebar_manual_state": self.SIDEBAR_STATE_MANUAL
        })
        self.sidebar_manual_state_cache = self.SIDEBAR_STATE_MANUAL
    
    def load_sidebar_state(self):
        """Load sidebar state from database"""
        state = self.db.get_preference("sidebar_state", "expanded")
        # Load and cache manual state
        self.sidebar_manual_state_cache = self.db.get_preference("sidebar_manual_state", self.SIDEBAR_STATE_AUTO)
        
        if state == "collapsed":
            # Set initial collapsed state without animation
            self._update_sidebar_visual_state(collapsed=True, animate=False)
            self.sidebar_collapsed = True
    
    def add_record(self, opco: str, device_type: str):
        """Add new record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        dialog = ModernAddEditDialog(self, opco=opco, device_type=device_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item = dialog.get_data()
            item_id = self.db.insert_item(item)
            
            if item_id > 0:
                QMessageBox.information(self, "Success", "Record added successfully")
                self.load_sheet_data(opco, device_type)
                self.update_dashboard_metrics()
            else:
                QMessageBox.warning(self, "Error", "Failed to add record")
    
    def edit_record(self, opco: str, device_type: str):
        """Edit selected record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        sheet_name = f"{opco} - {device_type}"
        view = self.sheet_views.get(sheet_name)
        if not view:
            return
        
        row_data = view.grid.get_selected_data()
        if not row_data:
            QMessageBox.warning(self, "Error", "Please select a record to edit")
            return
        
        item_id = row_data[0]
        item = self.db.get_item_by_id(item_id)
        
        if not item:
            QMessageBox.warning(self, "Error", "Could not load record")
            return
        
        dialog = ModernAddEditDialog(self, item=item, opco=opco, device_type=device_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_item = dialog.get_data()
            
            if self.db.update_item(item_id, updated_item):
                QMessageBox.information(self, "Success", "Record updated successfully")
                self.load_sheet_data(opco, device_type)
                self.update_dashboard_metrics()
            else:
                QMessageBox.warning(self, "Error", "Failed to update record")
    
    def delete_record(self, opco: str, device_type: str):
        """Delete selected record"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        sheet_name = f"{opco} - {device_type}"
        view = self.sheet_views.get(sheet_name)
        if not view:
            return
        
        row_data = view.grid.get_selected_data()
        if not row_data:
            QMessageBox.warning(self, "Error", "Please select a record to delete")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            item_id = row_data[0]
            
            if self.db.delete_item(item_id):
                QMessageBox.information(self, "Success", "Record deleted successfully")
                self.load_sheet_data(opco, device_type)
                self.update_dashboard_metrics()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete record")
    
    def import_data(self, opco: str, device_type: str):
        """Import data from file"""
        if not self.edit_mode:
            QMessageBox.warning(self, "Error", "Edit mode is locked. Enable edit mode first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            
            if file_path.endswith('.xlsx'):
                wb = openpyxl.load_workbook(file_path)
                
                sheet_name = f"{'OH' if opco == 'Ohio' else 'I&M'} - {device_type}"
                
                if sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        if not any(row) or not row[0]:
                            continue
                        
                        if len(row) < 17:
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
            
            self.load_sheet_data(opco, device_type)
            self.update_dashboard_metrics()
            QMessageBox.information(self, "Import Complete", f"Imported {imported_count} records")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error importing file: {e}")
            import traceback
            traceback.print_exc()
    
    def export_data(self, opco: str, device_type: str):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", f"{opco}_{device_type}.csv", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            items = self.db.get_items_by_sheet(opco, device_type)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.COLUMNS)
                writer.writerows(items)
            
            QMessageBox.information(self, "Export Complete", f"Exported {len(items)} records")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error exporting: {e}")
    
    def show_statistics(self, opco: str, device_type: str):
        """Show statistics"""
        try:
            stats = self.db.get_statistics(opco, device_type)
            
            msg = (
                f"Statistics for {opco} - {device_type}\n"
                f"{'='*50}\n\n"
                f"Total Records: {stats['total_items']}\n"
                f"Total Quantity: {stats['total_qty']:,}\n"
                f"Total Value: ${stats['total_value']:,.2f}\n"
                f"Average Cost per Unit: ${stats['avg_cost']:,.2f}\n"
            )
            
            QMessageBox.information(self, "Statistics", msg)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting statistics: {e}")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Exit', self.close)
        
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Toggle Edit Mode', self.toggle_edit_mode)
        
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Dashboard', self.show_dashboard)
        view_menu.addSeparator()
        view_menu.addAction('Light Theme', lambda: self.apply_theme("Light"))
        view_menu.addAction('Dark Theme', lambda: self.apply_theme("Dark"))
        
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def apply_theme(self, theme: str):
        """Apply theme"""
        self.current_theme = theme
        stylesheet = ThemeManager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
    
    def show_about(self):
        """Show about dialog"""
        msg = (
            "Created Histories v2.0.0\n\n"
            "Modern Professional Device History Tracking System\n\n"
            "Features:\n"
            "• Modern dashboard with real-time metrics\n"
            "• Multi-sheet support with advanced filtering\n"
            "• Professional form builder with validation\n"
            "• Enhanced data grid with sorting\n"
            "• Import/Export functionality\n"
            "• Password-protected edit mode\n"
            "• Collapsible sidebar (Alt+S) with state persistence\n"
            "• Responsive auto-collapse on small screens\n"
            "• WCAG 2.1 AA accessibility compliant\n"
            "• Light/Dark theme support\n\n"
            "Created with PyQt6"
        )
        QMessageBox.information(self, "About", msg)
    
    def resizeEvent(self, event):
        """Handle window resize for responsive behavior"""
        super().resizeEvent(event)
        
        # Only handle responsive behavior if in auto mode (not manually set)
        if self.sidebar_manual_state_cache == self.SIDEBAR_STATE_MANUAL:
            return
        
        # Check if we've crossed the responsive breakpoint threshold
        window_width = event.size().width()
        is_below_breakpoint = window_width < self.RESPONSIVE_BREAKPOINT_WIDTH
        
        # Only trigger if crossing the threshold (prevents repeated triggers)
        if self.last_responsive_width_state != is_below_breakpoint:
            self.last_responsive_width_state = is_below_breakpoint
            
            if is_below_breakpoint:
                # Auto-collapse if not already collapsed
                if not self.sidebar_collapsed:
                    self.collapse_sidebar()
            else:
                # Auto-expand if window is wide enough
                if self.sidebar_collapsed:
                    self.expand_sidebar()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = CreatedHistoriesApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
