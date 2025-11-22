"""
Status Indicators - Visual status and progress indicators
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QProgressBar, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class StatusIndicator(QFrame):
    """Visual status indicator badge"""
    
    # Status types with colors
    STATUS_STYLES = {
        'active': {
            'bg': '#d1fae5',
            'border': '#22c55e',
            'text': '#065f46',
            'icon': '●'
        },
        'inactive': {
            'bg': '#e5e7eb',
            'border': '#9ca3af',
            'text': '#374151',
            'icon': '○'
        },
        'pending': {
            'bg': '#fef3c7',
            'border': '#f59e0b',
            'text': '#92400e',
            'icon': '◐'
        },
        'error': {
            'bg': '#fee2e2',
            'border': '#ef4444',
            'text': '#991b1b',
            'icon': '✕'
        },
        'success': {
            'bg': '#d1fae5',
            'border': '#22c55e',
            'text': '#065f46',
            'icon': '✓'
        },
        'warning': {
            'bg': '#fed7aa',
            'border': '#f97316',
            'text': '#7c2d12',
            'icon': '⚠'
        },
        'info': {
            'bg': '#dbeafe',
            'border': '#3b82f6',
            'text': '#1e40af',
            'icon': 'ⓘ'
        }
    }
    
    def __init__(self, status: str = 'inactive', label: str = '', parent=None):
        super().__init__(parent)
        self.status = status
        self.label_text = label
        self.setup_ui()
        self.update_status(status, label)
    
    def setup_ui(self):
        """Setup indicator UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)
        
        # Label
        self.text_label = QLabel()
        self.text_label.setStyleSheet("background: transparent; font-weight: 600;")
        layout.addWidget(self.text_label)
        
        self.setLayout(layout)
        self.setMaximumHeight(28)
    
    def update_status(self, status: str, label: str = None):
        """Update status"""
        self.status = status
        if label:
            self.label_text = label
        
        style = self.STATUS_STYLES.get(status, self.STATUS_STYLES['inactive'])
        
        self.icon_label.setText(style['icon'])
        self.text_label.setText(self.label_text or status.title())
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {style['bg']};
                border: 2px solid {style['border']};
                border-radius: 14px;
            }}
            QLabel {{
                color: {style['text']};
                background: transparent;
                font-size: 12px;
            }}
        """)


class ProgressIndicator(QWidget):
    """Progress indicator with label"""
    
    progress_complete = pyqtSignal()
    
    def __init__(self, label: str = "Progress", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.setup_ui()
    
    def setup_ui(self):
        """Setup progress UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label with percentage
        label_layout = QHBoxLayout()
        
        self.label = QLabel(self.label_text)
        self.label.setProperty("class", "caption")
        label_layout.addWidget(self.label)
        
        label_layout.addStretch()
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setProperty("class", "caption")
        self.percentage_label.setStyleSheet("font-weight: 600;")
        label_layout.addWidget(self.percentage_label)
        
        layout.addLayout(label_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def set_progress(self, value: int, label: str = None):
        """Set progress value (0-100)"""
        value = max(0, min(100, value))
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        
        if label:
            self.label.setText(label)
        
        if value >= 100:
            self.progress_complete.emit()
    
    def reset(self):
        """Reset progress"""
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.label.setText(self.label_text)
    
    def set_indeterminate(self, active: bool = True):
        """Set indeterminate mode (spinning)"""
        if active:
            self.progress_bar.setMaximum(0)  # Indeterminate
        else:
            self.progress_bar.setMaximum(100)


class ActivityIndicator(QWidget):
    """Spinning activity indicator for loading states"""
    
    def __init__(self, message: str = "Loading...", parent=None):
        super().__init__(parent)
        self.message = message
        self.timer = QTimer()
        self.frame = 0
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.setup_ui()
    
    def setup_ui(self):
        """Setup activity UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Spinner
        self.spinner_label = QLabel(self.frames[0])
        spinner_font = QFont()
        spinner_font.setPointSize(16)
        self.spinner_label.setFont(spinner_font)
        layout.addWidget(self.spinner_label)
        
        # Message
        self.message_label = QLabel(self.message)
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Setup timer for animation
        self.timer.timeout.connect(self.update_spinner)
    
    def update_spinner(self):
        """Update spinner animation"""
        self.frame = (self.frame + 1) % len(self.frames)
        self.spinner_label.setText(self.frames[self.frame])
    
    def start(self, message: str = None):
        """Start the activity indicator"""
        if message:
            self.message_label.setText(message)
        self.timer.start(80)  # Update every 80ms
        self.show()
    
    def stop(self):
        """Stop the activity indicator"""
        self.timer.stop()
        self.hide()
    
    def set_message(self, message: str):
        """Update message"""
        self.message_label.setText(message)


class CountBadge(QLabel):
    """Small count badge"""
    
    def __init__(self, count: int = 0, parent=None):
        super().__init__(parent)
        self.count = count
        self.setup_ui()
        self.update_count(count)
    
    def setup_ui(self):
        """Setup badge UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(24, 24)
        self.setMaximumSize(40, 24)
        
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
    
    def update_count(self, count: int):
        """Update count"""
        self.count = count
        
        if count > 99:
            self.setText("99+")
        else:
            self.setText(str(count))
        
        # Color based on count
        if count == 0:
            bg_color = "#e5e7eb"
            text_color = "#6b7280"
        elif count < 10:
            bg_color = "#3b82f6"
            text_color = "#ffffff"
        else:
            bg_color = "#ef4444"
            text_color = "#ffffff"
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 12px;
                padding: 2px 6px;
            }}
        """)
        
        self.setVisible(count > 0)
