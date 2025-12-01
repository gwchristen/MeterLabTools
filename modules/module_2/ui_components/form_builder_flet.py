"""
Form Builder for Flet - Organized forms with field groups
"""

import flet as ft
from typing import Dict, Any, List, Optional, Callable


class FieldGroup(ft.Container):
    """Group of related form fields"""
    
    def __init__(self, title: str):
        self.title_text = title
        self.fields: Dict[str, ft.Control] = {}
        self.fields_column = ft.Column(spacing=12)
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PRIMARY,
                    ),
                    ft.Divider(height=1),
                    self.fields_column,
                ],
                spacing=8,
            ),
            padding=16,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            margin=ft.margin.only(bottom=12),
        )
    
    def add_field(
        self, 
        label: str, 
        widget: ft.Control, 
        required: bool = False,
        help_text: str = "",
    ):
        """Add a field to the group"""
        # Create label
        label_text = f"{label} *" if required else label
        label_widget = ft.Text(
            label_text,
            size=13,
            weight=ft.FontWeight.W_500,
        )
        
        # Create field row with optional help text
        field_controls = [label_widget]
        
        if help_text:
            field_controls.append(
                ft.Tooltip(
                    message=help_text,
                    content=ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=16,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                )
            )
        
        label_row = ft.Row(
            controls=field_controls,
            spacing=8,
        )
        
        # Add to column
        field_container = ft.Column(
            controls=[label_row, widget],
            spacing=4,
        )
        
        self.fields_column.controls.append(field_container)
        self.fields[label] = widget
        
        return widget
    
    def get_value(self, label: str) -> Any:
        """Get field value"""
        widget = self.fields.get(label)
        if not widget:
            return None
        
        if isinstance(widget, ft.TextField):
            return widget.value or ""
        elif isinstance(widget, ft.Dropdown):
            return widget.value or ""
        elif isinstance(widget, ft.Checkbox):
            return widget.value or False
        elif isinstance(widget, ft.Slider):
            return widget.value or 0
        
        return None
    
    def set_value(self, label: str, value: Any):
        """Set field value"""
        widget = self.fields.get(label)
        if not widget:
            return
        
        if isinstance(widget, ft.TextField):
            widget.value = str(value) if value is not None else ""
        elif isinstance(widget, ft.Dropdown):
            widget.value = str(value) if value is not None else None
        elif isinstance(widget, ft.Checkbox):
            widget.value = bool(value)
        elif isinstance(widget, ft.Slider):
            try:
                widget.value = float(value) if value is not None else 0
            except (ValueError, TypeError):
                widget.value = 0


class FormBuilder(ft.Column):
    """Professional form builder with field groups"""
    
    def __init__(self, on_form_changed: Optional[Callable[[], None]] = None):
        self.groups: Dict[str, FieldGroup] = {}
        self.on_form_changed = on_form_changed
        
        super().__init__(
            controls=[],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def add_group(self, title: str) -> FieldGroup:
        """Add a field group"""
        group = FieldGroup(title)
        self.groups[title] = group
        self.controls.append(group)
        return group
    
    def add_field_to_group(
        self, 
        group_title: str, 
        label: str, 
        field_type: str, 
        **kwargs
    ) -> ft.Control:
        """Add a field to a specific group"""
        group = self.groups.get(group_title)
        if not group:
            group = self.add_group(group_title)
        
        # Create widget based on type
        widget = self._create_field_widget(field_type, **kwargs)
        
        # Add to group
        required = kwargs.get('required', False)
        help_text = kwargs.get('help_text', '')
        group.add_field(label, widget, required, help_text)
        
        return widget
    
    def _create_field_widget(self, field_type: str, **kwargs) -> ft.Control:
        """Create a field widget based on type"""
        if field_type == 'text':
            widget = ft.TextField(
                hint_text=kwargs.get('placeholder', ''),
                max_length=kwargs.get('max_length'),
                dense=True,
                border_radius=8,
            )
            return widget
        
        elif field_type == 'multiline':
            widget = ft.TextField(
                hint_text=kwargs.get('placeholder', ''),
                multiline=True,
                min_lines=kwargs.get('min_lines', 2),
                max_lines=kwargs.get('max_lines', 4),
                dense=True,
                border_radius=8,
            )
            return widget
        
        elif field_type == 'number':
            widget = ft.TextField(
                hint_text="0",
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=ft.NumbersOnlyInputFilter(),
                dense=True,
                border_radius=8,
            )
            return widget
        
        elif field_type == 'decimal':
            widget = ft.TextField(
                hint_text="0.00",
                keyboard_type=ft.KeyboardType.NUMBER,
                dense=True,
                border_radius=8,
            )
            return widget
        
        elif field_type == 'dropdown':
            options = kwargs.get('options', [])
            widget = ft.Dropdown(
                options=[ft.dropdown.Option(opt) for opt in options],
                dense=True,
                border_radius=8,
            )
            return widget
        
        elif field_type == 'checkbox':
            widget = ft.Checkbox(
                label=kwargs.get('text', ''),
            )
            return widget
        
        elif field_type == 'date':
            # Flet doesn't have a built-in date picker, so we use a text field
            widget = ft.TextField(
                hint_text="YYYY-MM-DD",
                dense=True,
                border_radius=8,
            )
            return widget
        
        else:
            return ft.TextField(dense=True, border_radius=8)
    
    def get_all_values(self) -> Dict[str, Dict[str, Any]]:
        """Get all form values organized by group"""
        values = {}
        for group_title, group in self.groups.items():
            values[group_title] = {}
            for label in group.fields.keys():
                values[group_title][label] = group.get_value(label)
        return values
    
    def set_all_values(self, values: Dict[str, Dict[str, Any]]):
        """Set all form values"""
        for group_title, group_values in values.items():
            group = self.groups.get(group_title)
            if group:
                for label, value in group_values.items():
                    group.set_value(label, value)
        
        if self.page:
            self.update()
    
    def clear_form(self):
        """Clear all form values"""
        for group in self.groups.values():
            for label, widget in group.fields.items():
                if isinstance(widget, ft.TextField):
                    widget.value = ""
                elif isinstance(widget, ft.Dropdown):
                    widget.value = None
                elif isinstance(widget, ft.Checkbox):
                    widget.value = False
        
        if self.page:
            self.update()
