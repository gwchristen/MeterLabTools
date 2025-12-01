"""
Main Window Component for MeterLabTools - Flet-based
"""

import flet as ft
from typing import Optional, Callable

from shared.constants import APP_NAME, APP_VERSION


class MainWindow:
    """Main application window component for Flet"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.content_area: Optional[ft.Container] = None
        
        # Configure page
        self.setup_page()
    
    def setup_page(self):
        """Configure the page settings"""
        self.page.title = f"{APP_NAME} - Main Window"
        self.page.window.width = 1000
        self.page.window.height = 700
        self.page.padding = 0
    
    def build(self) -> ft.Control:
        """Build the main window layout"""
        # App bar
        app_bar = ft.AppBar(
            leading=ft.Icon(ft.Icons.DASHBOARD),
            title=ft.Text(APP_NAME, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        
        # Content area
        self.content_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            APP_NAME,
                            size=32,
                            weight=ft.FontWeight.BOLD,
                        ),
                        margin=ft.margin.only(bottom=20),
                    ),
                    ft.Text(
                        f"Version {APP_VERSION}",
                        size=16,
                        color=ft.Colors.GREY_500,
                    ),
                ],
                expand=True,
            ),
            expand=True,
            padding=20,
        )
        
        self.page.appbar = app_bar
        return self.content_area
    
    def set_content(self, content: ft.Control):
        """Set the main content area"""
        if self.content_area:
            self.content_area.content = content
            self.page.update()


def create_main_layout(
    title: str = APP_NAME,
    content: Optional[ft.Control] = None,
) -> ft.Column:
    """Create a standard main layout container"""
    
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.only(bottom=20),
    )
    
    body = ft.Container(
        content=content or ft.Text("Content goes here"),
        expand=True,
    )
    
    return ft.Column(
        controls=[header, body],
        expand=True,
    )