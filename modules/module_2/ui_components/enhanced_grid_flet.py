"""
Enhanced Data Grid for Flet - Professional data table with sorting and selection
"""

import flet as ft
from typing import List, Optional, Callable, Any
from datetime import datetime


class EnhancedDataGrid(ft.Column):
    """Enhanced data grid with sorting, filtering, and row selection"""
    
    def __init__(
        self, 
        columns: List[str],
        on_row_select: Optional[Callable[[int], None]] = None,
        on_row_double_click: Optional[Callable[[int], None]] = None,
        column_alignments: Optional[List[str]] = None,
    ):
        self.columns = columns
        self.data: List[tuple] = []
        self.filtered_data: List[tuple] = []
        self.sort_column = -1
        self.sort_ascending = True
        self.selected_row = -1
        self.on_row_select = on_row_select
        self.on_row_double_click = on_row_double_click
        self.column_alignments = column_alignments or ["left"] * len(columns)
        
        # Create data table with columns
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(col, weight=ft.FontWeight.BOLD, size=13),
                    on_sort=lambda e, idx=i: self._sort_by_column(idx),
                )
                for i, col in enumerate(columns)
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.3, ft.Colors.OUTLINE)),
            horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.3, ft.Colors.OUTLINE)),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            heading_row_height=48,
            data_row_min_height=40,
            data_row_max_height=48,
            column_spacing=16,
            show_checkbox_column=False,
            divider_thickness=0,
        )
        
        # Status bar
        self.status_label = ft.Text("Ready", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self.row_count_label = ft.Text("0 rows", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        
        status_bar = ft.Container(
            content=ft.Row(
                controls=[
                    self.status_label,
                    ft.Container(expand=True),
                    self.row_count_label,
                ],
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        )
        
        # Wrap data table in scrollable container
        scrollable_table = ft.Container(
            content=ft.Column(
                controls=[self.data_table],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
        )
        
        super().__init__(
            controls=[scrollable_table, status_bar],
            spacing=0,
            expand=True,
        )
    
    def set_data(self, data: List[tuple]):
        """Set grid data"""
        self.data = list(data)
        self.filtered_data = list(data)
        self.selected_row = -1
        self._refresh_display()
    
    def _format_cell_value(self, value: Any, column_name: str) -> str:
        """Format cell value based on column type"""
        if value is None or value == "":
            return ""
        
        # Date formatting (MM/DD/YYYY)
        if "date" in column_name.lower() and isinstance(value, str):
            try:
                # Try parsing common date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"]:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return dt.strftime("%m/%d/%Y")
                    except ValueError:
                        continue
            except:
                pass
        
        # Currency formatting
        if column_name in ["Unit Cost"] and isinstance(value, (int, float)):
            return f"${value:,.2f}"
        
        # Quantity formatting (thousands separator, no decimals)
        if column_name == "Qty" and isinstance(value, (int, float)):
            return f"{int(value):,}"
        
        # OOR Serial compact display
        if column_name == "OOR Serial" and value:
            # Import here to avoid circular dependency
            from .oor_parser import OORParser
            parser = OORParser()
            if parser.parse(str(value)):
                return parser.format_display(max_length=30)
            return str(value)
        
        return str(value)
    
    def _get_cell_tooltip(self, value: Any, column_name: str) -> Optional[str]:
        """Get tooltip for cell if needed"""
        if column_name == "OOR Serial" and value:
            from .oor_parser import OORParser
            parser = OORParser()
            if parser.parse(str(value)):
                return parser.get_detailed_breakdown()
        return None
    
    def _refresh_display(self):
        """Refresh the table display"""
        # Clear and rebuild rows
        self.data_table.rows.clear()
        
        for row_idx, row_data in enumerate(self.filtered_data):
            cells = []
            for col_idx, value in enumerate(row_data):
                column_name = self.columns[col_idx] if col_idx < len(self.columns) else ""
                text_value = self._format_cell_value(value, column_name)
                tooltip = self._get_cell_tooltip(value, column_name)
                alignment = self.column_alignments[col_idx] if col_idx < len(self.column_alignments) else "left"
                
                cell_text = ft.Text(
                    text_value,
                    size=13,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    text_align=ft.TextAlign.CENTER if alignment == "center" else ft.TextAlign.LEFT,
                )
                
                # Add tooltip if available
                if tooltip:
                    cell_text = ft.Tooltip(
                        message=tooltip,
                        content=cell_text,
                    )
                
                cells.append(
                    ft.DataCell(
                        cell_text,
                        on_tap=lambda e, idx=row_idx: self._on_cell_tap(idx),
                        on_double_tap=lambda e, idx=row_idx: self._on_cell_double_tap(idx),
                    )
                )
            
            is_selected = row_idx == self.selected_row
            row = ft.DataRow(
                cells=cells,
                selected=is_selected,
                on_select_changed=lambda e, idx=row_idx: self._on_row_selected(idx),
                color={
                    ft.ControlState.SELECTED: ft.Colors.PRIMARY_CONTAINER,
                    ft.ControlState.HOVERED: ft.Colors.SURFACE_CONTAINER_HIGHEST,
                },
            )
            self.data_table.rows.append(row)
        
        # Update status
        self._update_status()
        
        if self.page:
            self.update()
    
    def _update_status(self):
        """Update status bar"""
        total = len(self.data)
        filtered = len(self.filtered_data)
        
        if filtered == total:
            self.row_count_label.value = f"{total} rows"
            self.status_label.value = "Ready"
        else:
            self.row_count_label.value = f"{filtered} of {total} rows"
            self.status_label.value = "Filtered"
    
    def _sort_by_column(self, column: int):
        """Sort by column"""
        if self.sort_column == column:
            # Toggle sort order
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
        
        # Sort data with proper type handling
        def sort_key(row):
            value = row[column] if column < len(row) else None
            if value is None:
                # None values sort to the end
                return (1, "")
            elif isinstance(value, (int, float)):
                # Numbers sort numerically
                return (0, value)
            else:
                # Strings sort alphabetically (case-insensitive)
                return (0, str(value).lower())
        
        self.filtered_data.sort(key=sort_key, reverse=not self.sort_ascending)
        
        direction = "▲" if self.sort_ascending else "▼"
        self.status_label.value = f"Sorted by {self.columns[column]} {direction}"
        
        self._refresh_display()
    
    def filter_data(self, column: int, value: str):
        """Filter data by column value"""
        if not value:
            self.filtered_data = list(self.data)
        else:
            self.filtered_data = [
                row for row in self.data 
                if value.lower() in str(row[column] if column < len(row) else "").lower()
            ]
        
        self._refresh_display()
    
    def clear_filters(self):
        """Clear all filters"""
        self.filtered_data = list(self.data)
        self._refresh_display()
    
    def _on_cell_tap(self, row_idx: int):
        """Handle cell tap"""
        self.selected_row = row_idx
        self._refresh_display()
        if self.on_row_select:
            self.on_row_select(row_idx)
    
    def _on_cell_double_tap(self, row_idx: int):
        """Handle cell double tap"""
        self.selected_row = row_idx
        if self.on_row_double_click:
            self.on_row_double_click(row_idx)
    
    def _on_row_selected(self, row_idx: int):
        """Handle row selection"""
        self.selected_row = row_idx
        self._refresh_display()
        if self.on_row_select:
            self.on_row_select(row_idx)
    
    def get_selected_row(self) -> int:
        """Get selected row index"""
        return self.selected_row
    
    def get_selected_data(self) -> Optional[tuple]:
        """Get selected row data"""
        if 0 <= self.selected_row < len(self.filtered_data):
            return self.filtered_data[self.selected_row]
        return None
