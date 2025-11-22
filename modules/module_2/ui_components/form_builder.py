"""
Form Builder - Organized forms with field groups and validation
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                            QComboBox, QCheckBox, QDateEdit, QFrame,
                            QScrollArea, QGroupBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, List, Optional


class FieldGroup(QGroupBox):
    """Group of related form fields"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.fields = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup group UI"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 16, 12, 12)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        # Style the group box
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.setFont(title_font)
    
    def add_field(self, label: str, widget: QWidget, required: bool = False,
                 help_text: str = ""):
        """Add a field to the group"""
        field_layout = QVBoxLayout()
        field_layout.setSpacing(4)
        
        # Label row
        label_layout = QHBoxLayout()
        
        field_label = QLabel(label)
        if required:
            field_label.setText(f"{label} <span style='color: red;'>*</span>")
        field_label.setStyleSheet("font-weight: 600;")
        label_layout.addWidget(field_label)
        
        if help_text:
            help_label = QLabel(f"ⓘ")
            help_label.setToolTip(help_text)
            help_label.setProperty("class", "caption")
            label_layout.addWidget(help_label)
        
        label_layout.addStretch()
        field_layout.addLayout(label_layout)
        
        # Widget
        field_layout.addWidget(widget)
        
        self.layout.addLayout(field_layout)
        self.fields[label] = widget
        
        return widget
    
    def get_value(self, label: str) -> Any:
        """Get field value"""
        widget = self.fields.get(label)
        if not widget:
            return None
        
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QDateEdit):
            return widget.date().toString("yyyy-MM-dd")
        
        return None
    
    def set_value(self, label: str, value: Any):
        """Set field value"""
        widget = self.fields.get(label)
        if not widget:
            return
        
        if isinstance(widget, QLineEdit):
            widget.setText(str(value) if value else "")
        elif isinstance(widget, QTextEdit):
            widget.setText(str(value) if value else "")
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value) if value else 0)
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value) if value else 0.0)
        elif isinstance(widget, QComboBox):
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QDateEdit):
            # Parse date string
            if value:
                date = QDate.fromString(str(value), "yyyy-MM-dd")
                if date.isValid():
                    widget.setDate(date)


class FormBuilder(QScrollArea):
    """Professional form builder with field groups"""
    
    form_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups = {}
        self.validators = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup form UI"""
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container widget
        container = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)
        container.setLayout(self.main_layout)
        
        self.setWidget(container)
    
    def add_group(self, title: str) -> FieldGroup:
        """Add a field group"""
        group = FieldGroup(title, self)
        self.groups[title] = group
        self.main_layout.addWidget(group)
        return group
    
    def add_field_to_group(self, group_title: str, label: str, 
                          field_type: str, **kwargs) -> QWidget:
        """Add a field to a specific group"""
        group = self.groups.get(group_title)
        if not group:
            group = self.add_group(group_title)
        
        # Create widget based on type
        widget = self._create_field_widget(field_type, **kwargs)
        
        # Connect change signals
        self._connect_change_signal(widget)
        
        # Add to group
        required = kwargs.get('required', False)
        help_text = kwargs.get('help_text', '')
        group.add_field(label, widget, required, help_text)
        
        return widget
    
    def _create_field_widget(self, field_type: str, **kwargs) -> QWidget:
        """Create a field widget based on type"""
        if field_type == 'text':
            widget = QLineEdit()
            if 'placeholder' in kwargs:
                widget.setPlaceholderText(kwargs['placeholder'])
            if 'max_length' in kwargs:
                widget.setMaxLength(kwargs['max_length'])
            return widget
        
        elif field_type == 'multiline':
            widget = QTextEdit()
            widget.setMaximumHeight(kwargs.get('height', 80))
            if 'placeholder' in kwargs:
                widget.setPlaceholderText(kwargs['placeholder'])
            return widget
        
        elif field_type == 'number':
            widget = QSpinBox()
            widget.setMaximum(kwargs.get('max', 999999))
            widget.setMinimum(kwargs.get('min', 0))
            return widget
        
        elif field_type == 'decimal':
            widget = QDoubleSpinBox()
            widget.setMaximum(kwargs.get('max', 999999.99))
            widget.setMinimum(kwargs.get('min', 0.0))
            widget.setDecimals(kwargs.get('decimals', 2))
            return widget
        
        elif field_type == 'dropdown':
            widget = QComboBox()
            if 'options' in kwargs:
                widget.addItems(kwargs['options'])
            return widget
        
        elif field_type == 'checkbox':
            widget = QCheckBox(kwargs.get('text', ''))
            return widget
        
        elif field_type == 'date':
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDate(QDate.currentDate())
            return widget
        
        else:
            return QLineEdit()
    
    def _connect_change_signal(self, widget: QWidget):
        """Connect change signal for widget"""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.form_changed.emit)
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(self.form_changed.emit)
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(self.form_changed.emit)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(self.form_changed.emit)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(self.form_changed.emit)
        elif isinstance(widget, QDateEdit):
            widget.dateChanged.connect(self.form_changed.emit)
    
    def get_all_values(self) -> Dict[str, Dict[str, Any]]:
        """Get all form values organized by group"""
        values = {}
        for group_title, group in self.groups.items():
            values[group_title] = {}
            for label, widget in group.fields.items():
                values[group_title][label] = group.get_value(label)
        return values
    
    def set_all_values(self, values: Dict[str, Dict[str, Any]]):
        """Set all form values"""
        for group_title, group_values in values.items():
            group = self.groups.get(group_title)
            if group:
                for label, value in group_values.items():
                    group.set_value(label, value)
    
    def clear_form(self):
        """Clear all form values"""
        for group in self.groups.values():
            for label, widget in group.fields.items():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QTextEdit):
                    widget.clear()
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    widget.setValue(0)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(False)
                elif isinstance(widget, QDateEdit):
                    widget.setDate(QDate.currentDate())
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate all form fields"""
        errors = []
        
        # Check required fields
        for group in self.groups.values():
            for label, widget in group.fields.items():
                # This is a simple check - you'd expand this with validators
                if hasattr(widget, 'property') and widget.property('required'):
                    value = group.get_value(label)
                    if not value or (isinstance(value, str) and not value.strip()):
                        errors.append(f"{label} is required")
        
        return len(errors) == 0, errors
