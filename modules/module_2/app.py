"""
Created Histories Module - Flet-based Modern UI
Device History Management with dashboard, advanced filtering, and professional design
"""

import flet as ft
import csv
import hashlib
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional: openpyxl for Excel import
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

from inventory_db import InventoryDatabase
from ui_components.theme_flet import ThemeManager, get_status_colors
from ui_components.dashboard_cards_flet import MetricCard, StatisticsCard
from ui_components.enhanced_grid_flet import EnhancedDataGrid
from ui_components.filter_sidebar_flet import FilterSidebar
from ui_components.form_builder_flet import FormBuilder
from ui_components.status_indicators_flet import StatusIndicator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CreatedHistoriesApp:
    """Modern Created Histories Application using Flet"""
    
    # Master password hash (default: "admin123")
    MASTER_PASSWORD_HASH = "0192023a7bbd73250516f069df18b500"
    
    SHEETS = [
        ("Ohio", "Meters"),
        ("I&M", "Meters"),
        ("Ohio", "Transformers"),
        ("I&M", "Transformers"),
    ]
    
    # Full database columns
    FULL_COLUMNS = [
        "ID", "OpCo", "Device Type", "Status", "MFR", "Dev Code", "Beg Ser", "End Ser",
        "OOR Serial", "Qty", "PO Date", "PO Number", "Recv Date", "Unit Cost", "CID",
        "M.E. #", "Pur. Code", "Est.", "Use", "Notes 1", "Notes 2"
    ]
    
    # Streamlined grid columns for display
    GRID_COLUMNS = [
        "ID", "Dev Code", "Beg Ser", "End Ser", "OOR Serial", "Qty", "Recv Date", "CID"
    ]
    
    # Column index mapping from full to grid columns
    COLUMN_INDEX_MAP = {
        "ID": 0,
        "Dev Code": 5,
        "Beg Ser": 6,
        "End Ser": 7,
        "OOR Serial": 8,
        "Qty": 9,
        "Recv Date": 12,
        "CID": 14,
    }
    
    # Sheet name mapping for import
    SHEET_MAP = {
        'OH - Meters': ('Ohio', 'Meters'),
        'I&M - Meters': ('I&M', 'Meters'),
        'OH - Transformers': ('Ohio', 'Transformers'),
        'I&M - Transformers': ('I&M', 'Transformers'),
    }
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.edit_mode = False
        self.current_theme = "Dark"  # Default to dark mode
        self.current_sheet: Optional[str] = None
        self.current_view = "dashboard"
        
        # Initialize database
        self.db = InventoryDatabase('created_histories.db')
        self.db.init_db()
        
        # UI component references
        self.nav_rail: Optional[ft.NavigationRail] = None
        self.content_area: Optional[ft.Container] = None
        self.detail_panel: Optional[ft.Container] = None
        self.breadcrumb_label: Optional[ft.Text] = None
        self.subtitle_label: Optional[ft.Text] = None
        self.mode_indicator: Optional[StatusIndicator] = None
        self.edit_mode_btn: Optional[ft.TextButton] = None
        self.search_field: Optional[ft.TextField] = None
        
        # Dashboard cards
        self.total_records_card: Optional[MetricCard] = None
        self.total_devices_card: Optional[MetricCard] = None
        self.total_value_card: Optional[MetricCard] = None
        self.avg_cost_card: Optional[MetricCard] = None
        self.sheet_stats_cards: Dict[str, StatisticsCard] = {}
        
        # Sheet views
        self.sheet_grids: Dict[str, EnhancedDataGrid] = {}
        self.sheet_filter_sidebars: Dict[str, FilterSidebar] = {}
        self.sheet_filter_visible: Dict[str, bool] = {}
        self.selected_record_data: Optional[tuple] = None
        
        # Setup page
        self.setup_page()
        
        # Build UI
        self.build_ui()
        
        # Load sidebar state
        self.load_sidebar_state()
        
        logger.info("Created Histories App initialized!")
    
    def setup_page(self):
        """Configure page settings"""
        self.page.title = "Created Histories - Device History Management"
        self.page.window.width = 1600
        self.page.window.height = 950
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK  # Default to dark mode
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    
    def build_ui(self):
        """Build the main user interface"""
        # Create AppBar
        app_bar = self.create_app_bar()
        
        # Create NavigationRail
        self.nav_rail = self.create_navigation_rail()
        
        # Create main content area
        self.content_area = ft.Container(
            content=self.create_dashboard_view(),
            expand=True,
            padding=20,
        )
        
        # Main layout with NavigationRail and content
        main_content = ft.Row(
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
        
        # Set page controls
        self.page.appbar = app_bar
        self.page.add(main_content)
    
    def create_app_bar(self) -> ft.AppBar:
        """Create the application bar"""
        # Breadcrumb and subtitle
        self.breadcrumb_label = ft.Text(
            "Dashboard",
            size=18,
            weight=ft.FontWeight.BOLD,
        )
        self.subtitle_label = ft.Text(
            "Overview of all device histories",
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        breadcrumb_column = ft.Column(
            controls=[self.breadcrumb_label, self.subtitle_label],
            spacing=0,
        )
        
        # Search bar
        self.search_field = ft.TextField(
            hint_text="Search across all columns...",
            width=300,
            height=40,
            dense=True,
            border_radius=20,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
        )
        
        # Mode indicator
        self.mode_indicator = StatusIndicator('inactive', 'Read-Only')
        
        # Edit mode button
        self.edit_mode_btn = ft.TextButton(
            text="🔓 Enable Edit Mode",
            on_click=self.toggle_edit_mode,
        )
        
        return ft.AppBar(
            leading=ft.Icon(ft.Icons.HISTORY_EDU),
            leading_width=50,
            title=breadcrumb_column,
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions=[
                self.search_field,
                ft.Container(width=16),
                self.mode_indicator,
                ft.Container(width=16),
                self.edit_mode_btn,
                ft.Container(width=16),
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE,
                    tooltip="Toggle Theme",
                    on_click=self.toggle_theme,
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="About",
                            icon=ft.Icons.INFO_OUTLINE,
                            on_click=self.show_about,
                        ),
                        ft.PopupMenuItem(
                            text="Help",
                            icon=ft.Icons.HELP_OUTLINE,
                            on_click=self.show_help,
                        ),
                    ],
                ),
            ],
        )
    
    def create_navigation_rail(self) -> ft.NavigationRail:
        """Create the navigation rail"""
        destinations = [
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
        ]
        
        # Add sheet destinations with shortened labels
        sheet_labels = [
            "Ohio M",
            "I&M M",
            "Ohio T",
            "I&M T",
        ]
        
        for idx, (opco, device_type) in enumerate(self.SHEETS):
            destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icons.TABLE_CHART_OUTLINED,
                    selected_icon=ft.Icons.TABLE_CHART,
                    label=sheet_labels[idx],
                )
            )
        
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=destinations,
            on_change=self.on_nav_change,
        )
    
    def on_nav_change(self, e):
        """Handle navigation rail selection changes"""
        index = e.control.selected_index
        
        if index == 0:
            self.show_dashboard()
        else:
            # Sheet index (0-based after dashboard)
            sheet_idx = index - 1
            if 0 <= sheet_idx < len(self.SHEETS):
                opco, device_type = self.SHEETS[sheet_idx]
                sheet_name = f"{opco} - {device_type}"
                self.show_sheet(sheet_name)
        
        self.page.update()
    
    def create_dashboard_view(self) -> ft.Control:
        """Create the dashboard view with metrics"""
        # Metric cards row
        self.total_records_card = MetricCard("Total Records", "0", "📊")
        self.total_devices_card = MetricCard("Total Devices", "0", "🔧")
        self.total_value_card = MetricCard("Total Value", "$0", "💰")
        self.avg_cost_card = MetricCard("Avg. Unit Cost", "$0", "📈")
        
        metrics_row = ft.Row(
            controls=[
                self.total_records_card,
                self.total_devices_card,
                self.total_value_card,
                self.avg_cost_card,
            ],
            spacing=16,
            wrap=True,
            run_spacing=16,
        )
        
        # Sheet statistics section
        sheet_stats_label = ft.Text(
            "Sheet Statistics",
            size=18,
            weight=ft.FontWeight.W_600,
        )
        
        # Create stats cards for each sheet
        sheet_stats_row = ft.Row(
            controls=[],
            spacing=16,
            wrap=True,
            run_spacing=16,
        )
        
        for opco, device_type in self.SHEETS:
            sheet_name = f"{opco} - {device_type}"
            card = StatisticsCard(sheet_name, {})
            self.sheet_stats_cards[sheet_name] = card
            sheet_stats_row.controls.append(card)
        
        # Build dashboard layout
        dashboard = ft.Column(
            controls=[
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=16),
                metrics_row,
                ft.Container(height=24),
                sheet_stats_label,
                ft.Container(height=16),
                sheet_stats_row,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Update metrics
        self.update_dashboard_metrics()
        
        return dashboard
    
    def create_sheet_view(self, opco: str, device_type: str) -> ft.Control:
        """Create a sheet view with data grid, toolbar, and detail panel"""
        sheet_name = f"{opco} - {device_type}"
        
        # Create data grid with streamlined columns and row selection callback
        grid = EnhancedDataGrid(
            columns=self.GRID_COLUMNS,
            on_row_select=lambda idx: self.on_row_selected(opco, device_type, idx),
            on_row_double_click=lambda idx: self.edit_record(opco, device_type),
            column_alignments=["center"] * len(self.GRID_COLUMNS),
        )
        self.sheet_grids[sheet_name] = grid
        
        # Create toolbar
        toolbar = ft.Row(
            controls=[
                ft.FilledButton(
                    text="Add Record",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.add_record(opco, device_type),
                ),
                ft.OutlinedButton(
                    text="Edit",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: self.edit_record(opco, device_type),
                ),
                ft.OutlinedButton(
                    text="Delete",
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    on_click=lambda e: self.delete_record(opco, device_type),
                ),
                ft.Container(expand=True),
                ft.OutlinedButton(
                    text="Import",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=lambda e: self.import_data(opco, device_type),
                ),
                ft.OutlinedButton(
                    text="Export",
                    icon=ft.Icons.FILE_DOWNLOAD,
                    on_click=lambda e: self.export_data(opco, device_type),
                ),
                ft.OutlinedButton(
                    text="Statistics",
                    icon=ft.Icons.BAR_CHART,
                    on_click=lambda e: self.show_statistics(opco, device_type),
                ),
                ft.OutlinedButton(
                    text="Filters",
                    icon=ft.Icons.FILTER_LIST,
                    on_click=lambda e: self.toggle_filters(opco, device_type),
                ),
            ],
            spacing=8,
        )
        
        # Create filter sidebar
        filter_sidebar = FilterSidebar(
            fields=self.FULL_COLUMNS,
            on_apply_filters=lambda filters: self.apply_filters(opco, device_type, filters),
            on_clear_filters=lambda: self.load_sheet_data(opco, device_type),
        )
        self.sheet_filter_sidebars[sheet_name] = filter_sidebar
        self.sheet_filter_visible[sheet_name] = False
        
        # Create detail panel (right side, always visible)
        self.detail_panel = self.create_detail_panel()
        
        # Create main content with grid and detail panel
        main_content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            toolbar,
                            ft.Container(height=16),
                            grid,
                        ],
                        expand=True,
                    ),
                    expand=True,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=self.detail_panel,
                    width=350,
                ),
            ],
            expand=True,
        )
        
        # Load data
        self.load_sheet_data(opco, device_type)
        
        return main_content
    
    def create_detail_panel(self) -> ft.Column:
        """Create the detail panel for showing selected record details"""
        return ft.Column(
            controls=[
                ft.Text(
                    "Record Details",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                ft.Text(
                    "Select a record to view details",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    italic=True,
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def update_detail_panel(self, record_data: tuple):
        """Update detail panel with selected record data"""
        if not self.detail_panel or not record_data:
            return
        
        from .ui_components.oor_parser import OORParser
        
        # Build detail fields
        fields = []
        field_labels = self.FULL_COLUMNS
        
        for i, label in enumerate(field_labels):
            value = record_data[i] if i < len(record_data) else ""
            
            # Special handling for OOR Serial
            if label == "OOR Serial" and value:
                parser = OORParser()
                if parser.parse(str(value)):
                    value_display = parser.get_detailed_breakdown()
                else:
                    value_display = str(value)
            else:
                value_display = str(value) if value is not None else ""
            
            fields.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(value_display, size=13, selectable=True),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.only(bottom=8),
                )
            )
        
        # Action buttons (only show in edit mode)
        action_buttons = []
        if self.edit_mode:
            action_buttons = [
                ft.Divider(),
                ft.Text("Actions", size=12, weight=ft.FontWeight.BOLD),
                ft.FilledButton(
                    text="Edit Record",
                    icon=ft.Icons.EDIT,
                    width=300,
                    on_click=lambda e: self.edit_record_from_detail(),
                ),
                ft.OutlinedButton(
                    text="Duplicate Record",
                    icon=ft.Icons.COPY,
                    width=300,
                    on_click=lambda e: self.duplicate_record(),
                ),
                ft.OutlinedButton(
                    text="Delete Record",
                    icon=ft.Icons.DELETE,
                    width=300,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    on_click=lambda e: self.delete_record_from_detail(),
                ),
            ]
        
        # Update detail panel controls
        self.detail_panel.controls = [
            ft.Text(
                "Record Details",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Divider(),
            *fields,
            *action_buttons,
        ]
        
        self.detail_panel.update()
    
    def on_row_selected(self, opco: str, device_type: str, row_idx: int):
        """Handle row selection to update detail panel"""
        sheet_name = f"{opco} - {device_type}"
        grid = self.sheet_grids.get(sheet_name)
        
        if grid:
            selected_data = grid.get_selected_data()
            if selected_data:
                self.selected_record_data = selected_data
                self.update_detail_panel(selected_data)
    
    def on_search_change(self, e):
        """Handle search field changes"""
        search_text = e.control.value.strip().lower()
        
        if self.current_view == "sheet" and self.current_sheet:
            # Find opco and device_type
            opco, device_type = None, None
            for o, d in self.SHEETS:
                if f"{o} - {d}" == self.current_sheet:
                    opco, device_type = o, d
                    break
            
            if opco and device_type:
                self.search_sheet_data(opco, device_type, search_text)
    
    def search_sheet_data(self, opco: str, device_type: str, search_text: str):
        """Search data across all columns"""
        sheet_name = f"{opco} - {device_type}"
        grid = self.sheet_grids.get(sheet_name)
        
        if not grid:
            return
        
        # Get all data from database
        items = self.db.get_items_by_sheet(opco, device_type)
        
        if search_text:
            # Filter items that match search text in any column
            filtered_items = []
            for item in items:
                # Convert item to grid format
                grid_item = self._convert_to_grid_format(item)
                # Search across all columns in the original item
                if any(search_text in str(val).lower() for val in item if val):
                    filtered_items.append(grid_item)
            
            grid.set_data(filtered_items)
        else:
            # Show all data in grid format
            grid_data = [self._convert_to_grid_format(item) for item in items]
            grid.set_data(grid_data)
    
    def _convert_to_grid_format(self, full_record: tuple) -> tuple:
        """Convert full database record to streamlined grid format"""
        grid_record = []
        for col_name in self.GRID_COLUMNS:
            idx = self.COLUMN_INDEX_MAP.get(col_name, 0)
            grid_record.append(full_record[idx] if idx < len(full_record) else "")
        return tuple(grid_record)
    
    def edit_record_from_detail(self):
        """Edit record from detail panel"""
        if self.current_sheet:
            opco, device_type = None, None
            for o, d in self.SHEETS:
                if f"{o} - {d}" == self.current_sheet:
                    opco, device_type = o, d
                    break
            if opco and device_type:
                self.edit_record(opco, device_type)
    
    def duplicate_record(self):
        """Duplicate the selected record"""
        if self.current_sheet and self.selected_record_data:
            opco, device_type = None, None
            for o, d in self.SHEETS:
                if f"{o} - {d}" == self.current_sheet:
                    opco, device_type = o, d
                    break
            if opco and device_type:
                self.add_record(opco, device_type, duplicate_from=self.selected_record_data)
    
    def delete_record_from_detail(self):
        """Delete record from detail panel"""
        if self.current_sheet:
            opco, device_type = None, None
            for o, d in self.SHEETS:
                if f"{o} - {d}" == self.current_sheet:
                    opco, device_type = o, d
                    break
            if opco and device_type:
                self.delete_record(opco, device_type)
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.current_view = "dashboard"
        self.current_sheet = None
        
        if self.breadcrumb_label:
            self.breadcrumb_label.value = "Dashboard"
        if self.subtitle_label:
            self.subtitle_label.value = "Overview of all device histories"
        
        if self.content_area:
            self.content_area.content = self.create_dashboard_view()
            self.content_area.update()
        
        self.page.update()
    
    def show_sheet(self, sheet_name: str):
        """Show specific sheet"""
        self.current_view = "sheet"
        self.current_sheet = sheet_name
        
        # Find opco and device_type
        opco, device_type = None, None
        for o, d in self.SHEETS:
            if f"{o} - {d}" == sheet_name:
                opco, device_type = o, d
                break
        
        if not opco or not device_type:
            return
        
        if self.breadcrumb_label:
            self.breadcrumb_label.value = sheet_name
        if self.subtitle_label:
            self.subtitle_label.value = f"Manage {sheet_name} device records"
        
        if self.content_area:
            self.content_area.content = self.create_sheet_view(opco, device_type)
            self.content_area.update()
        
        self.page.update()
    
    def load_sheet_data(self, opco: str, device_type: str):
        """Load data for sheet"""
        try:
            sheet_name = f"{opco} - {device_type}"
            grid = self.sheet_grids.get(sheet_name)
            if not grid:
                return
            
            items = self.db.get_items_by_sheet(opco, device_type)
            # Convert to grid format
            grid_data = [self._convert_to_grid_format(item) for item in items]
            grid.set_data(grid_data)
            
        except Exception as e:
            self.show_snackbar(f"Error loading data: {e}", is_error=True)
    
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
            if self.total_records_card:
                self.total_records_card.update_value(f"{total_records:,}")
            if self.total_devices_card:
                self.total_devices_card.update_value(f"{total_qty:,}")
            if self.total_value_card:
                self.total_value_card.update_value(f"${total_value:,.2f}")
            
            avg_cost = sum(costs) / len(costs) if costs else 0
            if self.avg_cost_card:
                self.avg_cost_card.update_value(f"${avg_cost:,.2f}")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def toggle_edit_mode(self, e):
        """Toggle edit mode with password"""
        if self.edit_mode:
            self.edit_mode = False
            if self.mode_indicator:
                self.mode_indicator.update_status('inactive', 'Read-Only')
            if self.edit_mode_btn:
                self.edit_mode_btn.text = "🔓 Enable Edit Mode"
            self.show_snackbar("Edit mode disabled")
        else:
            self.show_password_dialog()
        
        self.page.update()
    
    def show_password_dialog(self):
        """Show password dialog for edit mode"""
        password_field = ft.TextField(
            label="Master Password",
            password=True,
            can_reveal_password=True,
            autofocus=True,
        )
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def submit_password(e):
            password = password_field.value or ""
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            if password_hash == self.MASTER_PASSWORD_HASH:
                self.edit_mode = True
                if self.mode_indicator:
                    self.mode_indicator.update_status('success', 'Edit Mode')
                if self.edit_mode_btn:
                    self.edit_mode_btn.text = "🔒 Disable Edit Mode"
                self.show_snackbar("Edit mode enabled!")
                dialog.open = False
            else:
                self.show_snackbar("Incorrect password", is_error=True)
            
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Enter Password"),
            content=ft.Container(
                content=password_field,
                width=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("OK", on_click=submit_password),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def add_record(self, opco: str, device_type: str, duplicate_from: Optional[tuple] = None):
        """Add new record"""
        if not self.edit_mode:
            self.show_snackbar("Edit mode is locked. Enable edit mode first.", is_error=True)
            return
        
        # If duplicating, fetch the full record
        item_to_duplicate = None
        if duplicate_from:
            item_id = duplicate_from[0]  # First column is ID
            item_to_duplicate = self.db.get_item_by_id(item_id)
        
        self.show_add_edit_dialog(opco, device_type, item_to_duplicate, is_duplicate=bool(duplicate_from))
    
    def edit_record(self, opco: str, device_type: str):
        """Edit selected record"""
        if not self.edit_mode:
            self.show_snackbar("Edit mode is locked. Enable edit mode first.", is_error=True)
            return
        
        sheet_name = f"{opco} - {device_type}"
        grid = self.sheet_grids.get(sheet_name)
        if not grid:
            return
        
        row_data = grid.get_selected_data()
        if not row_data:
            self.show_snackbar("Please select a record to edit", is_error=True)
            return
        
        item_id = row_data[0]
        item = self.db.get_item_by_id(item_id)
        
        if not item:
            self.show_snackbar("Could not load record", is_error=True)
            return
        
        self.show_add_edit_dialog(opco, device_type, item)
    
    def show_add_edit_dialog(self, opco: str, device_type: str, item: Optional[Dict] = None, is_duplicate: bool = False):
        """Show add/edit record dialog"""
        is_edit = item is not None and not is_duplicate
        
        # Create form fields
        status_field = ft.TextField(label="Status", value=item.get('status', '') if item else '')
        mfr_field = ft.TextField(label="Manufacturer", value=item.get('mfr', '') if item else '')
        dev_code_field = ft.TextField(label="Device Code", value=item.get('dev_code', '') if item else '')
        beg_ser_field = ft.TextField(label="Beginning Serial", value=item.get('beg_ser', '') if item else '')
        end_ser_field = ft.TextField(label="Ending Serial", value=item.get('end_ser', '') if item else '')
        oor_serial_field = ft.TextField(
            label="OOR Serial (ranges/singles separated by commas)", 
            value=item.get('oor_serial', '') if item else '',
            multiline=True,
            hint_text="e.g., 1000-1010, 1050, 2000-2005"
        )
        qty_field = ft.TextField(label="Quantity", value=str(item.get('qty', 0)) if item else '0', keyboard_type=ft.KeyboardType.NUMBER)
        po_date_field = ft.TextField(label="PO Date", value=item.get('po_date', '') if item else '')
        po_number_field = ft.TextField(label="PO Number", value=item.get('po_number', '') if item else '')
        recv_date_field = ft.TextField(label="Received Date", value=item.get('recv_date', '') if item else '')
        unit_cost_field = ft.TextField(label="Unit Cost", value=str(item.get('unit_cost', 0.0)) if item else '0.00')
        cid_field = ft.TextField(label="CID", value=item.get('cid', '') if item else '')
        me_number_field = ft.TextField(label="M.E. #", value=item.get('me_number', '') if item else '')
        pur_code_field = ft.TextField(label="Purchase Code", value=item.get('pur_code', '') if item else '')
        est_field = ft.TextField(label="Est.", value=item.get('est', '') if item else '')
        use_field = ft.TextField(label="Use", value=item.get('use', '') if item else '')
        notes1_field = ft.TextField(label="Notes 1", value=item.get('notes1', '') if item else '', multiline=True)
        notes2_field = ft.TextField(label="Notes 2", value=item.get('notes2', '') if item else '', multiline=True)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def save_record(e):
            from .ui_components.oor_parser import OORParser
            
            try:
                # Auto-calculate Qty from OOR Serial or Beg/End Ser
                oor_serial_value = oor_serial_field.value or ''
                qty = 0
                
                if oor_serial_value.strip():
                    # Calculate from OOR Serial
                    parser = OORParser()
                    if parser.parse(oor_serial_value):
                        qty = parser.get_total_qty()
                    else:
                        self.show_snackbar("Invalid OOR Serial format", is_error=True)
                        return
                else:
                    # Try to calculate from Beg/End Ser
                    beg_ser = beg_ser_field.value or ''
                    end_ser = end_ser_field.value or ''
                    if beg_ser and end_ser:
                        parser = OORParser()
                        qty = parser.calculate_qty_from_range(beg_ser, end_ser)
                    else:
                        # Use manual qty
                        try:
                            qty = int(qty_field.value or 0)
                        except ValueError:
                            qty = 0
            except Exception as ex:
                self.show_snackbar(f"Error calculating quantity: {ex}", is_error=True)
                return
            
            try:
                unit_cost = float(unit_cost_field.value or 0.0)
            except ValueError:
                unit_cost = 0.0
            
            record_data = {
                'opco': opco,
                'device_type': device_type,
                'status': status_field.value or '',
                'mfr': mfr_field.value or '',
                'dev_code': dev_code_field.value or '',
                'beg_ser': beg_ser_field.value or '',
                'end_ser': end_ser_field.value or '',
                'oor_serial': oor_serial_value,
                'qty': qty,
                'po_date': po_date_field.value or '',
                'po_number': po_number_field.value or '',
                'recv_date': recv_date_field.value or '',
                'unit_cost': unit_cost,
                'cid': cid_field.value or '',
                'me_number': me_number_field.value or '',
                'pur_code': pur_code_field.value or '',
                'est': est_field.value or '',
                'use': use_field.value or '',
                'notes1': notes1_field.value or '',
                'notes2': notes2_field.value or '',
            }
            
            if is_edit:
                item_id = item.get('id')
                if self.db.update_item(item_id, record_data):
                    self.show_snackbar("Record updated successfully")
                else:
                    self.show_snackbar("Failed to update record", is_error=True)
            else:
                item_id = self.db.insert_item(record_data)
                if item_id > 0:
                    self.show_snackbar("Record added successfully")
                else:
                    self.show_snackbar("Failed to add record", is_error=True)
            
            dialog.open = False
            self.load_sheet_data(opco, device_type)
            self.update_dashboard_metrics()
            self.page.update()
        
        # Build form content
        form_content = ft.Column(
            controls=[
                ft.Row([
                    ft.Container(content=ft.TextField(label="OpCo", value=opco, read_only=True, disabled=True), expand=True),
                    ft.Container(content=ft.TextField(label="Device Type", value=device_type, read_only=True, disabled=True), expand=True),
                ], spacing=16),
                ft.Row([status_field, mfr_field], spacing=16, expand=True),
                ft.Row([dev_code_field, beg_ser_field, end_ser_field], spacing=16, expand=True),
                oor_serial_field,
                ft.Text("Note: Qty will auto-calculate from OOR Serial or Beg/End Ser", size=11, italic=True, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Row([qty_field, po_date_field, po_number_field], spacing=16, expand=True),
                ft.Row([recv_date_field, unit_cost_field, cid_field], spacing=16, expand=True),
                ft.Row([me_number_field, pur_code_field, est_field, use_field], spacing=16, expand=True),
                notes1_field,
                notes2_field,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Record" if is_edit else "Add New Record"),
            content=ft.Container(
                content=form_content,
                width=700,
                height=500,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save", on_click=save_record),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def delete_record(self, opco: str, device_type: str):
        """Delete selected record"""
        if not self.edit_mode:
            self.show_snackbar("Edit mode is locked. Enable edit mode first.", is_error=True)
            return
        
        sheet_name = f"{opco} - {device_type}"
        grid = self.sheet_grids.get(sheet_name)
        if not grid:
            return
        
        row_data = grid.get_selected_data()
        if not row_data:
            self.show_snackbar("Please select a record to delete", is_error=True)
            return
        
        item_id = row_data[0]
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_delete(e):
            if self.db.delete_item(item_id):
                self.show_snackbar("Record deleted successfully")
                self.load_sheet_data(opco, device_type)
                self.update_dashboard_metrics()
            else:
                self.show_snackbar("Failed to delete record", is_error=True)
            
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this record?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def toggle_filters(self, opco: str, device_type: str):
        """Toggle filter sidebar visibility"""
        sheet_name = f"{opco} - {device_type}"
        self.sheet_filter_visible[sheet_name] = not self.sheet_filter_visible.get(sheet_name, False)
        
        # Rebuild the sheet view
        self.show_sheet(sheet_name)
    
    def apply_filters(self, opco: str, device_type: str, filters: Dict):
        """Apply filters to grid"""
        sheet_name = f"{opco} - {device_type}"
        grid = self.sheet_grids.get(sheet_name)
        if not grid:
            return
        
        try:
            # Get all data for the sheet
            all_items = self.db.get_items_by_sheet(opco, device_type)
            
            # Apply filter conditions
            logic = filters.get('logic', 'AND')
            conditions = filters.get('conditions', [])
            
            if not conditions or not any(c.get('value') for c in conditions):
                # No valid filters, show all data
                grid.set_data(all_items)
                return
            
            # Filter the data
            filtered_items = []
            
            for item in all_items:
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
            grid.set_data(filtered_items)
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            self.load_sheet_data(opco, device_type)
    
    def import_data(self, opco: str, device_type: str):
        """Import data from file"""
        if not self.edit_mode:
            self.show_snackbar("Edit mode is locked. Enable edit mode first.", is_error=True)
            return
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            
            file_path = e.files[0].path
            if not file_path:
                return
            
            try:
                imported_count = 0
                
                if file_path.endswith('.xlsx'):
                    if not HAS_OPENPYXL:
                        self.show_snackbar("openpyxl is required for Excel import", is_error=True)
                        return
                    
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
                self.show_snackbar(f"Imported {imported_count} records")
                
            except Exception as ex:
                logger.error(f"Error importing file: {ex}")
                self.show_snackbar(f"Error importing file: {ex}", is_error=True)
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(
            allowed_extensions=["xlsx", "csv"],
            dialog_title="Select File to Import",
        )
    
    def export_data(self, opco: str, device_type: str):
        """Export data to CSV"""
        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.path:
                return
            
            file_path = e.path
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            
            try:
                items = self.db.get_items_by_sheet(opco, device_type)
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.COLUMNS)
                    writer.writerows(items)
                
                self.show_snackbar(f"Exported {len(items)} records to {file_path}")
                
            except Exception as ex:
                self.show_snackbar(f"Error exporting: {ex}", is_error=True)
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.save_file(
            file_name=f"{opco}_{device_type}.csv",
            dialog_title="Export CSV",
        )
    
    def show_statistics(self, opco: str, device_type: str):
        """Show statistics dialog"""
        try:
            stats = self.db.get_statistics(opco, device_type)
            
            stats_content = ft.Column(
                controls=[
                    ft.Row([
                        ft.Text("Total Records:", weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        ft.Text(f"{stats['total_items']:,}"),
                    ]),
                    ft.Row([
                        ft.Text("Total Quantity:", weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        ft.Text(f"{stats['total_qty']:,}"),
                    ]),
                    ft.Row([
                        ft.Text("Total Value:", weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        ft.Text(f"${stats['total_value']:,.2f}"),
                    ]),
                    ft.Row([
                        ft.Text("Average Cost per Unit:", weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        ft.Text(f"${stats['avg_cost']:,.2f}"),
                    ]),
                ],
                spacing=12,
            )
            
            def close_dialog(e):
                dialog.open = False
                self.page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text(f"Statistics - {opco} {device_type}"),
                content=ft.Container(
                    content=stats_content,
                    width=350,
                ),
                actions=[
                    ft.TextButton("Close", on_click=close_dialog),
                ],
            )
            
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
            
        except Exception as e:
            self.show_snackbar(f"Error getting statistics: {e}", is_error=True)
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.current_theme = "Dark"
            if hasattr(e.control, 'icon'):
                e.control.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.current_theme = "Light"
            if hasattr(e.control, 'icon'):
                e.control.icon = ft.Icons.LIGHT_MODE
        
        self.page.update()
    
    def load_sidebar_state(self):
        """Load sidebar state from database"""
        try:
            state = self.db.get_preference("sidebar_state", "expanded")
            # Note: Flet NavigationRail doesn't support collapsing the same way PyQt does
            # We could implement extended mode toggling if needed
        except Exception:
            pass
    
    def show_about(self, e):
        """Show about dialog"""
        about_content = ft.Column(
            controls=[
                ft.Text("Created Histories v2.0.0 (Flet)", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=12),
                ft.Text("Modern Professional Device History Tracking System", size=14),
                ft.Container(height=12),
                ft.Text("Features:", weight=ft.FontWeight.W_600),
                ft.Text("• Modern dashboard with real-time metrics"),
                ft.Text("• Multi-sheet support with advanced filtering"),
                ft.Text("• CRUD operations with password protection"),
                ft.Text("• Import/Export functionality"),
                ft.Text("• Light/Dark theme support"),
                ft.Container(height=12),
                ft.Text("Built with Flet (Flutter for Python)", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            spacing=2,
        )
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("About"),
            content=ft.Container(content=about_content, width=400),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_help(self, e):
        """Show help dialog"""
        help_content = ft.Column(
            controls=[
                ft.Text("How to Use:", weight=ft.FontWeight.W_600, size=16),
                ft.Container(height=8),
                ft.Text("1. Navigate using the rail on the left"),
                ft.Text("2. Click 'Enable Edit Mode' and enter password to edit"),
                ft.Text("3. Use toolbar buttons to add, edit, or delete records"),
                ft.Text("4. Use Filters to search and filter data"),
                ft.Text("5. Import Excel files or export to CSV"),
                ft.Container(height=12),
                ft.Text("Default Password: admin123", weight=ft.FontWeight.W_500),
            ],
            spacing=4,
        )
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Help"),
            content=ft.Container(content=help_content, width=400),
            actions=[ft.TextButton("Close", on_click=close_dialog)],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_snackbar(self, message: str, is_error: bool = False):
        """Show a snackbar notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.ERROR if is_error else None,
            action="OK",
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()


def main(page: ft.Page):
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("Created Histories Module (Flet)")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    CreatedHistoriesApp(page)


if __name__ == '__main__':
    ft.app(target=main)
