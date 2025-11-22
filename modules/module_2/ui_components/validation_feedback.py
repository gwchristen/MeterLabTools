"""
Validation Feedback - Real-time validation feedback system
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Callable, Any, Optional
import re


class Validator:
    """Validation rules and helpers"""
    
    @staticmethod
    def required(value: Any) -> tuple[bool, str]:
        """Required field validator"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, "This field is required"
        return True, ""
    
    @staticmethod
    def email(value: str) -> tuple[bool, str]:
        """Email validator"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Please enter a valid email address"
        return True, ""
    
    @staticmethod
    def min_length(length: int) -> Callable:
        """Minimum length validator"""
        def validate(value: str) -> tuple[bool, str]:
            if len(str(value)) < length:
                return False, f"Must be at least {length} characters"
            return True, ""
        return validate
    
    @staticmethod
    def max_length(length: int) -> Callable:
        """Maximum length validator"""
        def validate(value: str) -> tuple[bool, str]:
            if len(str(value)) > length:
                return False, f"Must be no more than {length} characters"
            return True, ""
        return validate
    
    @staticmethod
    def numeric(value: Any) -> tuple[bool, str]:
        """Numeric validator"""
        try:
            float(value)
            return True, ""
        except (ValueError, TypeError):
            return False, "Must be a number"
    
    @staticmethod
    def positive(value: Any) -> tuple[bool, str]:
        """Positive number validator"""
        try:
            num = float(value)
            if num <= 0:
                return False, "Must be a positive number"
            return True, ""
        except (ValueError, TypeError):
            return False, "Must be a number"
    
    @staticmethod
    def range_validator(min_val: float, max_val: float) -> Callable:
        """Range validator"""
        def validate(value: Any) -> tuple[bool, str]:
            try:
                num = float(value)
                if num < min_val or num > max_val:
                    return False, f"Must be between {min_val} and {max_val}"
                return True, ""
            except (ValueError, TypeError):
                return False, "Must be a number"
        return validate
    
    @staticmethod
    def pattern(pattern: str, message: str = "Invalid format") -> Callable:
        """Pattern validator"""
        def validate(value: str) -> tuple[bool, str]:
            if not re.match(pattern, str(value)):
                return False, message
            return True, ""
        return validate


class ValidationFeedback(QFrame):
    """Real-time validation feedback widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validators = []
        self.is_valid = True
        self.error_message = ""
        self.setup_ui()
        self.hide()  # Hidden by default
    
    def setup_ui(self):
        """Setup feedback UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(20)
        layout.addWidget(self.icon_label)
        
        # Message
        self.message_label = QLabel()
        self.message_label.setProperty("class", "caption")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMaximumHeight(40)
    
    def add_validator(self, validator: Callable):
        """Add a validator function"""
        self.validators.append(validator)
    
    def validate(self, value: Any) -> bool:
        """Validate value against all validators"""
        if not self.validators:
            self.hide()
            return True
        
        for validator in self.validators:
            is_valid, message = validator(value)
            if not is_valid:
                self.show_error(message)
                return False
        
        self.show_success()
        return True
    
    def show_error(self, message: str):
        """Show error feedback"""
        self.is_valid = False
        self.error_message = message
        
        self.icon_label.setText("❌")
        self.message_label.setText(message)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #fee2e2;
                border: 2px solid #ef4444;
                border-radius: 6px;
            }
            QLabel {
                color: #991b1b;
                background: transparent;
            }
        """)
        
        self.show()
    
    def show_success(self):
        """Show success feedback"""
        self.is_valid = True
        self.error_message = ""
        
        self.icon_label.setText("✓")
        self.message_label.setText("Valid")
        
        self.setStyleSheet("""
            QFrame {
                background-color: #d1fae5;
                border: 2px solid #22c55e;
                border-radius: 6px;
            }
            QLabel {
                color: #065f46;
                background: transparent;
            }
        """)
        
        # Auto-hide success after 2 seconds
        QTimer.singleShot(2000, self.hide)
    
    def show_warning(self, message: str):
        """Show warning feedback"""
        self.icon_label.setText("⚠")
        self.message_label.setText(message)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 2px solid #f59e0b;
                border-radius: 6px;
            }
            QLabel {
                color: #92400e;
                background: transparent;
            }
        """)
        
        self.show()
    
    def clear(self):
        """Clear validation feedback"""
        self.is_valid = True
        self.error_message = ""
        self.hide()


class ValidationGroup(QWidget):
    """Group of validation feedbacks"""
    
    validation_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.feedbacks = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup group UI"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)
    
    def add_feedback(self, name: str, feedback: ValidationFeedback):
        """Add a validation feedback"""
        self.feedbacks[name] = feedback
        self.layout.addWidget(feedback)
    
    def validate_all(self) -> bool:
        """Validate all feedbacks"""
        all_valid = all(fb.is_valid for fb in self.feedbacks.values())
        self.validation_changed.emit(all_valid)
        return all_valid
    
    def clear_all(self):
        """Clear all feedbacks"""
        for feedback in self.feedbacks.values():
            feedback.clear()
    
    def get_errors(self) -> dict:
        """Get all error messages"""
        return {
            name: fb.error_message 
            for name, fb in self.feedbacks.items() 
            if not fb.is_valid
        }
