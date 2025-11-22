"""
Filter Sidebar - Advanced filtering with AND/OR logic
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QComboBox, QLineEdit, QFrame,
                            QScrollArea, QCheckBox, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any


class FilterCondition(QFrame):
    """Single filter condition widget"""
    
    remove_requested = pyqtSignal(object)
    
    def __init__(self, fields: List[str], parent=None):
        super().__init__(parent)
        self.fields = fields
        self.setup_ui()
    
    def setup_ui(self):
        """Setup condition UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Field selector
        self.field_combo = QComboBox()
        self.field_combo.addItems(self.fields)
        self.field_combo.setMinimumWidth(150)
        layout.addWidget(self.field_combo)
        
        # Operator selector
        self.operator_combo = QComboBox()
        self.operator_combo.addItems([
            "Contains",
            "Equals",
            "Starts with",
            "Ends with",
            "Greater than",
            "Less than",
            "Is empty",
            "Is not empty"
        ])
        self.operator_combo.setMinimumWidth(120)
        layout.addWidget(self.operator_combo)
        
        # Value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value...")
        layout.addWidget(self.value_input)
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setMaximumWidth(30)
        remove_btn.setProperty("class", "error")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
    
    def get_condition(self) -> Dict[str, str]:
        """Get condition data"""
        return {
            'field': self.field_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'value': self.value_input.text()
        }


class FilterBuilder(QWidget):
    """Advanced filter builder with AND/OR logic"""
    
    filters_changed = pyqtSignal()
    
    def __init__(self, fields: List[str], parent=None):
        super().__init__(parent)
        self.fields = fields
        self.conditions = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup builder UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Logic selector
        logic_layout = QHBoxLayout()
        logic_label = QLabel("Match:")
        logic_layout.addWidget(logic_label)
        
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["All conditions (AND)", "Any condition (OR)"])
        self.logic_combo.setMinimumWidth(180)
        logic_layout.addWidget(self.logic_combo)
        logic_layout.addStretch()
        
        layout.addLayout(logic_layout)
        
        # Conditions container
        self.conditions_container = QWidget()
        self.conditions_layout = QVBoxLayout()
        self.conditions_layout.setContentsMargins(0, 0, 0, 0)
        self.conditions_layout.setSpacing(8)
        self.conditions_container.setLayout(self.conditions_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.conditions_container)
        scroll.setMaximumHeight(300)
        layout.addWidget(scroll)
        
        # Add condition button
        add_btn = QPushButton("➕ Add Condition")
        add_btn.setProperty("class", "secondary")
        add_btn.clicked.connect(self.add_condition)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
        
        # Add initial condition
        self.add_condition()
    
    def add_condition(self):
        """Add a new filter condition"""
        condition = FilterCondition(self.fields, self)
        condition.remove_requested.connect(self.remove_condition)
        self.conditions.append(condition)
        self.conditions_layout.addWidget(condition)
        self.filters_changed.emit()
    
    def remove_condition(self, condition):
        """Remove a filter condition"""
        if len(self.conditions) > 1:  # Keep at least one condition
            self.conditions.remove(condition)
            condition.deleteLater()
            self.filters_changed.emit()
    
    def get_filters(self) -> Dict[str, Any]:
        """Get all filter conditions"""
        return {
            'logic': 'AND' if 'All' in self.logic_combo.currentText() else 'OR',
            'conditions': [c.get_condition() for c in self.conditions]
        }
    
    def clear_filters(self):
        """Clear all conditions"""
        for condition in self.conditions[1:]:  # Keep first one
            condition.deleteLater()
        self.conditions = [self.conditions[0]]
        self.conditions[0].value_input.clear()
        self.filters_changed.emit()


class FilterSidebar(QFrame):
    """Sidebar for advanced filtering"""
    
    apply_filters = pyqtSignal(dict)
    clear_filters = pyqtSignal()
    
    def __init__(self, fields: List[str], parent=None):
        super().__init__(parent)
        self.fields = fields
        self.saved_filters = {}
        self.setProperty("class", "sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Filters")
        title.setProperty("class", "subheading")
        layout.addWidget(title)
        
        # Active filter count
        self.filter_count_label = QLabel("0 active filters")
        self.filter_count_label.setProperty("class", "caption")
        layout.addWidget(self.filter_count_label)
        
        # Saved filters
        saved_layout = QVBoxLayout()
        saved_label = QLabel("Saved Filters")
        saved_label.setProperty("class", "caption")
        saved_label.setStyleSheet("font-weight: 600; text-transform: uppercase;")
        saved_layout.addWidget(saved_label)
        
        self.saved_filters_combo = QComboBox()
        self.saved_filters_combo.addItem("-- Select --")
        self.saved_filters_combo.currentTextChanged.connect(self.load_saved_filter)
        saved_layout.addWidget(self.saved_filters_combo)
        
        save_btn = QPushButton("💾 Save Current")
        save_btn.setProperty("class", "secondary")
        save_btn.clicked.connect(self.save_current_filter)
        saved_layout.addWidget(save_btn)
        
        layout.addLayout(saved_layout)
        
        # Filter builder
        self.filter_builder = FilterBuilder(self.fields, self)
        self.filter_builder.filters_changed.connect(self.on_filters_changed)
        layout.addWidget(self.filter_builder)
        
        layout.addStretch()
        
        # Action buttons
        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self.apply_current_filters)
        layout.addWidget(apply_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self.clear_all_filters)
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
        self.setMinimumWidth(320)
        self.setMaximumWidth(400)
    
    def on_filters_changed(self):
        """Handle filter changes"""
        filters = self.filter_builder.get_filters()
        count = sum(1 for c in filters['conditions'] if c['value'])
        self.filter_count_label.setText(f"{count} active filter{'s' if count != 1 else ''}")
    
    def apply_current_filters(self):
        """Apply current filters"""
        filters = self.filter_builder.get_filters()
        self.apply_filters.emit(filters)
    
    def clear_all_filters(self):
        """Clear all filters"""
        self.filter_builder.clear_filters()
        self.filter_count_label.setText("0 active filters")
        self.clear_filters.emit()
    
    def save_current_filter(self):
        """Save current filter configuration"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Save Filter", "Filter name:")
        if ok and name:
            filters = self.filter_builder.get_filters()
            self.saved_filters[name] = filters
            
            # Update combo
            if self.saved_filters_combo.findText(name) == -1:
                self.saved_filters_combo.addItem(name)
    
    def load_saved_filter(self, name: str):
        """Load a saved filter"""
        if name in self.saved_filters:
            # This would need to rebuild the filter UI
            # For now, just apply it
            self.apply_filters.emit(self.saved_filters[name])
