"""
Status Indicators for Flet - Visual status and progress indicators
"""

import flet as ft
from typing import Optional


class StatusIndicator(ft.Container):
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
    
    def __init__(self, status: str = 'inactive', label: str = ''):
        self.status = status
        self.label_text = label
        
        # Create controls
        self.icon_label = ft.Text("", size=12)
        self.text_label = ft.Text("", size=12, weight=ft.FontWeight.W_600)
        
        super().__init__(
            content=ft.Row(
                controls=[self.icon_label, self.text_label],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=14,
            height=28,
        )
        
        self.update_status(status, label)
    
    def update_status(self, status: str, label: Optional[str] = None):
        """Update status"""
        self.status = status
        if label is not None:
            self.label_text = label
        
        style = self.STATUS_STYLES.get(status, self.STATUS_STYLES['inactive'])
        
        self.icon_label.value = style['icon']
        self.icon_label.color = style['text']
        self.text_label.value = self.label_text or status.title()
        self.text_label.color = style['text']
        
        self.bgcolor = style['bg']
        self.border = ft.border.all(2, style['border'])
        
        if self.page:
            self.update()


class ProgressIndicator(ft.Column):
    """Progress indicator with label"""
    
    def __init__(self, label: str = "Progress"):
        self.label_text = label
        self.progress_value = 0
        
        self.label_control = ft.Text(
            label,
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        self.percentage_label = ft.Text(
            "0%",
            size=12,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        
        label_row = ft.Row(
            controls=[
                self.label_control,
                ft.Container(expand=True),
                self.percentage_label,
            ],
        )
        
        self.progress_bar = ft.ProgressBar(
            value=0,
            border_radius=4,
        )
        
        super().__init__(
            controls=[label_row, self.progress_bar],
            spacing=8,
        )
    
    def set_progress(self, value: int, label: Optional[str] = None):
        """Set progress value (0-100)"""
        self.progress_value = max(0, min(100, value))
        
        self.progress_bar.value = self.progress_value / 100
        self.percentage_label.value = f"{self.progress_value}%"
        
        if label:
            self.label_control.value = label
        
        if self.page:
            self.update()
    
    def reset(self):
        """Reset progress"""
        self.set_progress(0)
        self.label_control.value = self.label_text
        if self.page:
            self.update()
    
    def set_indeterminate(self, active: bool = True):
        """Set indeterminate mode (spinning)"""
        self.progress_bar.value = None if active else self.progress_value / 100
        if self.page:
            self.update()


class ActivityIndicator(ft.Row):
    """Activity indicator for loading states"""
    
    def __init__(self, message: str = "Loading..."):
        self.message = message
        self.is_visible = False
        
        self.spinner = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
        )
        
        self.message_label = ft.Text(message, size=14)
        
        super().__init__(
            controls=[self.spinner, self.message_label],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=self.is_visible,
        )
    
    def start(self, message: Optional[str] = None):
        """Start the activity indicator"""
        if message:
            self.message_label.value = message
        
        self.visible = True
        if self.page:
            self.update()
    
    def stop(self):
        """Stop the activity indicator"""
        self.visible = False
        if self.page:
            self.update()
    
    def set_message(self, message: str):
        """Update message"""
        self.message_label.value = message
        if self.page:
            self.update()


class CountBadge(ft.Container):
    """Small count badge"""
    
    def __init__(self, count: int = 0):
        self.count_value = count
        self.count_label = ft.Text(
            str(count),
            size=10,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        
        super().__init__(
            content=self.count_label,
            width=24,
            height=24,
            border_radius=12,
            alignment=ft.alignment.center,
        )
        
        self.update_count(count)
    
    def update_count(self, count: int):
        """Update count"""
        self.count_value = count
        
        if count > 99:
            self.count_label.value = "99+"
        else:
            self.count_label.value = str(count)
        
        # Color based on count
        if count == 0:
            self.bgcolor = "#e5e7eb"
            self.count_label.color = "#6b7280"
            self.visible = False
        elif count < 10:
            self.bgcolor = "#3b82f6"
            self.count_label.color = ft.Colors.WHITE
            self.visible = True
        else:
            self.bgcolor = "#ef4444"
            self.count_label.color = ft.Colors.WHITE
            self.visible = True
        
        if self.page:
            self.update()
