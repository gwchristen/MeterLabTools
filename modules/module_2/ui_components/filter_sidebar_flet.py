"""
Filter Sidebar for Flet - Advanced filtering with AND/OR logic
"""

import flet as ft
from typing import List, Dict, Any, Optional, Callable

# Minimum number of filter conditions to keep
MIN_CONDITIONS = 1


class FilterCondition(ft.Container):
    """Single filter condition widget"""
    
    def __init__(
        self, 
        fields: List[str], 
        on_remove: Optional[Callable[['FilterCondition'], None]] = None,
    ):
        self.fields = fields
        self.on_remove = on_remove
        
        # Create controls
        self.field_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(f) for f in fields],
            value=fields[0] if fields else None,
            width=140,
            dense=True,
        )
        
        self.operator_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Contains"),
                ft.dropdown.Option("Equals"),
                ft.dropdown.Option("Starts with"),
                ft.dropdown.Option("Ends with"),
                ft.dropdown.Option("Greater than"),
                ft.dropdown.Option("Less than"),
                ft.dropdown.Option("Is empty"),
                ft.dropdown.Option("Is not empty"),
            ],
            value="Contains",
            width=120,
            dense=True,
        )
        
        self.value_input = ft.TextField(
            hint_text="Value...",
            dense=True,
            expand=True,
        )
        
        self.remove_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=18,
            icon_color=ft.Colors.ERROR,
            tooltip="Remove condition",
            on_click=self._handle_remove,
        )
        
        super().__init__(
            content=ft.Row(
                controls=[
                    self.field_dropdown,
                    self.operator_dropdown,
                    self.value_input,
                    self.remove_btn,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=8,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
        )
    
    def _handle_remove(self, e):
        """Handle remove button click"""
        if self.on_remove:
            self.on_remove(self)
    
    def get_condition(self) -> Dict[str, str]:
        """Get condition data"""
        return {
            'field': self.field_dropdown.value or '',
            'operator': self.operator_dropdown.value or '',
            'value': self.value_input.value or ''
        }


class FilterBuilder(ft.Column):
    """Advanced filter builder with AND/OR logic"""
    
    def __init__(
        self, 
        fields: List[str],
        on_filters_changed: Optional[Callable[[], None]] = None,
    ):
        self.fields = fields
        self.conditions: List[FilterCondition] = []
        self.on_filters_changed = on_filters_changed
        
        # Logic selector
        self.logic_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("All conditions (AND)"),
                ft.dropdown.Option("Any condition (OR)"),
            ],
            value="All conditions (AND)",
            width=200,
            dense=True,
        )
        
        logic_row = ft.Row(
            controls=[
                ft.Text("Match:", weight=ft.FontWeight.W_500),
                self.logic_dropdown,
            ],
            spacing=8,
        )
        
        # Conditions container
        self.conditions_column = ft.Column(
            controls=[],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Add condition button
        add_btn = ft.OutlinedButton(
            text="Add Condition",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.add_condition(),
        )
        
        super().__init__(
            controls=[
                logic_row,
                ft.Container(height=8),
                self.conditions_column,
                ft.Container(height=8),
                add_btn,
            ],
            spacing=0,
        )
        
        # Add initial condition
        self.add_condition()
    
    def add_condition(self):
        """Add a new filter condition"""
        condition = FilterCondition(
            fields=self.fields,
            on_remove=self.remove_condition,
        )
        self.conditions.append(condition)
        self.conditions_column.controls.append(condition)
        
        if self.page:
            self.update()
        
        if self.on_filters_changed:
            self.on_filters_changed()
    
    def remove_condition(self, condition: FilterCondition):
        """Remove a filter condition"""
        if len(self.conditions) > MIN_CONDITIONS:
            self.conditions.remove(condition)
            if condition in self.conditions_column.controls:
                self.conditions_column.controls.remove(condition)
            
            if self.page:
                self.update()
            
            if self.on_filters_changed:
                self.on_filters_changed()
    
    def get_filters(self) -> Dict[str, Any]:
        """Get all filter conditions"""
        logic = 'AND' if 'All' in (self.logic_dropdown.value or '') else 'OR'
        return {
            'logic': logic,
            'conditions': [c.get_condition() for c in self.conditions]
        }
    
    def clear_filters(self):
        """Clear all conditions"""
        # Remove all conditions except the minimum required
        while len(self.conditions) > MIN_CONDITIONS:
            condition = self.conditions.pop()
            if condition in self.conditions_column.controls:
                self.conditions_column.controls.remove(condition)
        
        # Clear the remaining condition's value
        if self.conditions:
            self.conditions[0].value_input.value = ""
        
        if self.page:
            self.update()
        
        if self.on_filters_changed:
            self.on_filters_changed()


class FilterSidebar(ft.Container):
    """Sidebar for advanced filtering"""
    
    def __init__(
        self, 
        fields: List[str],
        on_apply_filters: Optional[Callable[[Dict], None]] = None,
        on_clear_filters: Optional[Callable[[], None]] = None,
    ):
        self.fields = fields
        self.on_apply_filters = on_apply_filters
        self.on_clear_filters = on_clear_filters
        
        # Title
        title = ft.Text("Filters", size=18, weight=ft.FontWeight.W_600)
        
        # Active filter count
        self.filter_count_label = ft.Text(
            "0 active filters",
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        # Filter builder
        self.filter_builder = FilterBuilder(
            fields=fields,
            on_filters_changed=self._on_filters_changed,
        )
        
        # Action buttons
        apply_btn = ft.FilledButton(
            text="Apply Filters",
            icon=ft.Icons.CHECK,
            on_click=self._apply_filters,
            expand=True,
        )
        
        clear_btn = ft.OutlinedButton(
            text="Clear All",
            icon=ft.Icons.CLEAR_ALL,
            on_click=self._clear_filters,
            expand=True,
        )
        
        button_row = ft.Row(
            controls=[apply_btn, clear_btn],
            spacing=8,
        )
        
        super().__init__(
            content=ft.Column(
                controls=[
                    title,
                    self.filter_count_label,
                    ft.Divider(height=1),
                    ft.Container(height=8),
                    self.filter_builder,
                    ft.Container(expand=True),
                    button_row,
                ],
                spacing=8,
            ),
            padding=16,
            width=320,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.only(left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        )
    
    def _on_filters_changed(self):
        """Handle filter changes"""
        filters = self.filter_builder.get_filters()
        count = sum(1 for c in filters['conditions'] if c['value'])
        self.filter_count_label.value = f"{count} active filter{'s' if count != 1 else ''}"
        if self.page:
            self.filter_count_label.update()
    
    def _apply_filters(self, e):
        """Apply current filters"""
        if self.on_apply_filters:
            filters = self.filter_builder.get_filters()
            self.on_apply_filters(filters)
    
    def _clear_filters(self, e):
        """Clear all filters"""
        self.filter_builder.clear_filters()
        self._on_filters_changed()
        
        if self.on_clear_filters:
            self.on_clear_filters()
