"""
Dashboard Cards for Flet - Professional metric and statistics cards
"""

import flet as ft
from typing import Dict, Any, Optional


class MetricCard(ft.Container):
    """Card for displaying key metrics"""
    
    def __init__(
        self, 
        title: str, 
        value: str, 
        icon: str = "", 
        subtitle: str = "",
        trend: str = "",
        on_click=None,
    ):
        self.title_text = title
        self.value_text = value
        self.icon_text = icon
        self.subtitle_text = subtitle
        self.trend_text = trend
        self._on_click = on_click
        
        # Create the value text control for later updates
        self.value_label = ft.Text(
            value,
            size=32,
            weight=ft.FontWeight.BOLD,
        )
        
        super().__init__(
            content=self._build_content(),
            padding=16,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE,
            ink=True,
            on_click=on_click,
            expand=True,
        )
    
    def _build_content(self) -> ft.Control:
        """Build card content"""
        # Header row with icon and title
        header_row = ft.Row(
            controls=[
                ft.Text(self.icon_text, size=20) if self.icon_text else ft.Container(),
                ft.Text(
                    self.title_text.upper(),
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=8,
        )
        
        # Build content list
        content_list = [
            header_row,
            ft.Container(height=8),
            self.value_label,
        ]
        
        # Add subtitle/trend if present
        if self.subtitle_text or self.trend_text:
            footer_row = ft.Row(
                controls=[
                    ft.Text(
                        self.subtitle_text,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ) if self.subtitle_text else ft.Container(),
                    ft.Text(
                        self.trend_text,
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ) if self.trend_text else ft.Container(),
                ],
            )
            content_list.append(footer_row)
        
        return ft.Column(
            controls=content_list,
            spacing=4,
        )
    
    def update_value(self, value: str):
        """Update the metric value"""
        self.value_text = value
        self.value_label.value = value
        if self.page:
            self.value_label.update()


class StatisticsCard(ft.Container):
    """Card for displaying detailed statistics"""
    
    def __init__(self, title: str, stats: Dict[str, Any], on_click=None):
        self.title_text = title
        self.stats = stats
        self._on_click = on_click
        self.stats_column = ft.Column(spacing=8)
        
        super().__init__(
            content=self._build_content(),
            padding=16,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE,
            ink=True,
            on_click=on_click,
            expand=True,
        )
    
    def _build_content(self) -> ft.Control:
        """Build card content"""
        # Title
        title_label = ft.Text(
            self.title_text,
            size=16,
            weight=ft.FontWeight.W_600,
        )
        
        # Build stats rows
        self._update_stats_rows()
        
        return ft.Column(
            controls=[
                title_label,
                ft.Divider(height=1),
                self.stats_column,
            ],
            spacing=8,
        )
    
    def _update_stats_rows(self):
        """Update the statistics rows"""
        self.stats_column.controls.clear()
        
        for key, value in self.stats.items():
            stat_row = ft.Row(
                controls=[
                    ft.Text(
                        key,
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        str(value),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            )
            self.stats_column.controls.append(stat_row)
    
    def update_stats(self, stats: Dict[str, Any]):
        """Update statistics"""
        self.stats = stats
        self._update_stats_rows()
        if self.page:
            self.stats_column.update()


class InfoCard(ft.Container):
    """Card for displaying informational content"""
    
    def __init__(self, title: str, content: str, icon: str = "", on_click=None):
        self.title_text = title
        self.content_text = content
        self.icon_text = icon
        self._on_click = on_click
        
        super().__init__(
            content=self._build_content(),
            padding=16,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            bgcolor=ft.Colors.SURFACE,
            ink=True,
            on_click=on_click,
            expand=True,
        )
    
    def _build_content(self) -> ft.Control:
        """Build card content"""
        # Header
        header_row = ft.Row(
            controls=[
                ft.Text(self.icon_text, size=28) if self.icon_text else ft.Container(),
                ft.Text(
                    self.title_text,
                    size=16,
                    weight=ft.FontWeight.W_600,
                ),
            ],
            spacing=12,
        )
        
        # Content
        content_label = ft.Text(
            self.content_text,
            size=14,
        )
        
        return ft.Column(
            controls=[
                header_row,
                ft.Container(height=8),
                content_label,
            ],
            spacing=4,
        )
