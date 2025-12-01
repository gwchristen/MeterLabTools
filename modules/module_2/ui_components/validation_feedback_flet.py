"""
Validation Feedback for Flet - Real-time validation feedback system
"""

import flet as ft
from typing import Callable, Any, List, Dict, Optional
import re


class Validator:
    """Validation rules and helpers"""
    
    @staticmethod
    def required(value: Any) -> tuple:
        """Required field validator"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, "This field is required"
        return True, ""
    
    @staticmethod
    def email(value: str) -> tuple:
        """Email validator"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, str(value)):
            return False, "Please enter a valid email address"
        return True, ""
    
    @staticmethod
    def min_length(length: int) -> Callable:
        """Minimum length validator"""
        def validate(value: str) -> tuple:
            if len(str(value)) < length:
                return False, f"Must be at least {length} characters"
            return True, ""
        return validate
    
    @staticmethod
    def max_length(length: int) -> Callable:
        """Maximum length validator"""
        def validate(value: str) -> tuple:
            if len(str(value)) > length:
                return False, f"Must be no more than {length} characters"
            return True, ""
        return validate
    
    @staticmethod
    def numeric(value: Any) -> tuple:
        """Numeric validator"""
        try:
            float(value)
            return True, ""
        except (ValueError, TypeError):
            return False, "Must be a number"
    
    @staticmethod
    def positive(value: Any) -> tuple:
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
        def validate(value: Any) -> tuple:
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
        def validate(value: str) -> tuple:
            if not re.match(pattern, str(value)):
                return False, message
            return True, ""
        return validate


class ValidationFeedback(ft.Container):
    """Real-time validation feedback widget"""
    
    def __init__(self):
        self.validators: List[Callable] = []
        self.is_valid = True
        self.error_message = ""
        
        self.icon_label = ft.Text("", size=14)
        self.message_label = ft.Text("", size=12)
        
        super().__init__(
            content=ft.Row(
                controls=[self.icon_label, self.message_label],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            visible=False,
        )
    
    def add_validator(self, validator: Callable):
        """Add a validator function"""
        self.validators.append(validator)
    
    def validate(self, value: Any) -> bool:
        """Validate value against all validators"""
        if not self.validators:
            self._hide()
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
        
        self.icon_label.value = "❌"
        self.icon_label.color = "#991b1b"
        
        self.message_label.value = message
        self.message_label.color = "#991b1b"
        
        self.bgcolor = "#fee2e2"
        self.border = ft.border.all(2, "#ef4444")
        self.visible = True
        
        if self.page:
            self.update()
    
    def show_success(self):
        """Show success feedback"""
        self.is_valid = True
        self.error_message = ""
        
        self.icon_label.value = "✓"
        self.icon_label.color = "#065f46"
        
        self.message_label.value = "Valid"
        self.message_label.color = "#065f46"
        
        self.bgcolor = "#d1fae5"
        self.border = ft.border.all(2, "#22c55e")
        self.visible = True
        
        if self.page:
            self.update()
    
    def show_warning(self, message: str):
        """Show warning feedback"""
        self.icon_label.value = "⚠"
        self.icon_label.color = "#92400e"
        
        self.message_label.value = message
        self.message_label.color = "#92400e"
        
        self.bgcolor = "#fef3c7"
        self.border = ft.border.all(2, "#f59e0b")
        self.visible = True
        
        if self.page:
            self.update()
    
    def clear(self):
        """Clear validation feedback"""
        self.is_valid = True
        self.error_message = ""
        self._hide()
    
    def _hide(self):
        """Hide the feedback container"""
        self.visible = False
        if self.page:
            self.update()


class ValidationGroup(ft.Column):
    """Group of validation feedbacks"""
    
    def __init__(self):
        self.feedbacks: Dict[str, ValidationFeedback] = {}
        
        super().__init__(
            controls=[],
            spacing=4,
        )
    
    def add_feedback(self, name: str, feedback: ValidationFeedback):
        """Add a validation feedback"""
        self.feedbacks[name] = feedback
        self.controls.append(feedback)
    
    def validate_all(self) -> bool:
        """Validate all feedbacks"""
        return all(fb.is_valid for fb in self.feedbacks.values())
    
    def clear_all(self):
        """Clear all feedbacks"""
        for feedback in self.feedbacks.values():
            feedback.clear()
    
    def get_errors(self) -> Dict[str, str]:
        """Get all error messages"""
        return {
            name: fb.error_message 
            for name, fb in self.feedbacks.items() 
            if not fb.is_valid
        }
