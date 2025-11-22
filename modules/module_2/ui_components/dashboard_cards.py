"""
Dashboard Cards - Professional metric and statistics cards
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QWidget, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont


class DashboardCard(QFrame):
    """Base dashboard card widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup card UI"""
        self.setMinimumHeight(120)
        self.setMaximumHeight(200)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        self.setLayout(layout)
    
    def setup_animations(self):
        """Setup hover animations"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.setProperty("hover", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class MetricCard(DashboardCard):
    """Card for displaying key metrics"""
    
    def __init__(self, title: str, value: str, icon: str = "", 
                 subtitle: str = "", trend: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.subtitle = subtitle
        self.trend = trend
        self.value_label = None  # Store reference for updates
        
        self.build_content()
    
    def build_content(self):
        """Build card content"""
        layout = self.layout()
        
        # Header row with icon and title
        header_layout = QHBoxLayout()
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("font-size: 24px; background: transparent;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setProperty("class", "caption")
        title_label.setStyleSheet("text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value - store reference for updates
        self.value_label = QLabel(self.value)
        value_font = QFont()
        value_font.setPointSize(32)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        layout.addWidget(self.value_label)
        
        # Subtitle and trend
        if self.subtitle or self.trend:
            footer_layout = QHBoxLayout()
            
            if self.subtitle:
                subtitle_label = QLabel(self.subtitle)
                subtitle_label.setProperty("class", "caption")
                footer_layout.addWidget(subtitle_label)
            
            if self.trend:
                trend_label = QLabel(self.trend)
                trend_label.setProperty("class", "caption")
                trend_label.setStyleSheet("font-weight: 600;")
                footer_layout.addWidget(trend_label)
            
            footer_layout.addStretch()
            layout.addLayout(footer_layout)
        
        layout.addStretch()
    
    def update_value(self, value: str):
        """Update the metric value"""
        self.value = value
        if self.value_label:
            self.value_label.setText(value)


class StatisticsCard(DashboardCard):
    """Card for displaying detailed statistics"""
    
    def __init__(self, title: str, stats: dict, parent=None):
        self.title = title
        self.stats = stats
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.build_content()
    
    def build_content(self):
        """Build card content"""
        layout = self.layout()
        
        # Title
        title_label = QLabel(self.title)
        title_label.setProperty("class", "subheading")
        layout.addWidget(title_label)
        
        # Statistics grid
        for key, value in self.stats.items():
            stat_layout = QHBoxLayout()
            
            key_label = QLabel(key)
            key_label.setProperty("class", "caption")
            stat_layout.addWidget(key_label)
            
            stat_layout.addStretch()
            
            value_label = QLabel(str(value))
            value_font = QFont()
            value_font.setPointSize(16)
            value_font.setBold(True)
            value_label.setFont(value_font)
            stat_layout.addWidget(value_label)
            
            layout.addLayout(stat_layout)
        
        layout.addStretch()
    
    def update_stats(self, stats: dict):
        """Update statistics"""
        self.stats = stats
        # Clear and rebuild
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    subitem = item.layout().takeAt(0)
                    if subitem.widget():
                        subitem.widget().deleteLater()
        self.build_content()


class InfoCard(DashboardCard):
    """Card for displaying informational content"""
    
    def __init__(self, title: str, content: str, icon: str = "", parent=None):
        self.title = title
        self.content = content
        self.icon = icon
        super().__init__(parent)
        self.build_content()
    
    def build_content(self):
        """Build card content"""
        layout = self.layout()
        
        # Header
        header_layout = QHBoxLayout()
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("font-size: 28px; background: transparent;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setProperty("class", "subheading")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Content
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("line-height: 1.5;")
        layout.addWidget(content_label)
        
        layout.addStretch()
