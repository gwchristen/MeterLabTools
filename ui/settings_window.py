"""
Settings Window Component for MeterLabTools - Flet-based
"""

import flet as ft
from typing import Callable, Optional, Dict, Any


class SettingsWindow:
    """Settings and preferences component for Flet"""
    
    def __init__(
        self,
        page: ft.Page,
        on_apply: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        initial_theme: str = "Light",
        initial_font_size: int = 10,
    ):
        self.page = page
        self.on_apply = on_apply
        self.on_cancel = on_cancel
        self.dialog: Optional[ft.AlertDialog] = None
        
        # Settings controls
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            value=initial_theme,
            options=[
                ft.dropdown.Option("Light"),
                ft.dropdown.Option("Dark"),
            ],
            width=200,
        )
        
        self.font_size_slider = ft.Slider(
            min=8,
            max=20,
            value=initial_font_size,
            divisions=12,
            label="{value}",
        )
        
        self.font_size_text = ft.Text(f"Font Size: {initial_font_size}")
    
    def build_dialog(self) -> ft.AlertDialog:
        """Build the settings dialog"""
        
        def on_slider_change(e):
            self.font_size_text.value = f"Font Size: {int(e.control.value)}"
            self.page.update()
        
        self.font_size_slider.on_change = on_slider_change
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Settings"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Appearance", weight=ft.FontWeight.W_500),
                        ft.Container(height=10),
                        self.theme_dropdown,
                        ft.Container(height=20),
                        self.font_size_text,
                        self.font_size_slider,
                    ],
                    tight=True,
                    spacing=5,
                ),
                width=300,
                height=200,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.handle_cancel),
                ft.FilledButton("Apply", on_click=self.handle_apply),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return self.dialog
    
    def show(self):
        """Show the settings dialog"""
        if not self.dialog:
            self.build_dialog()
        
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
    
    def close(self):
        """Close the settings dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
    
    def handle_apply(self, e):
        """Handle apply button click"""
        settings = {
            "theme": self.theme_dropdown.value,
            "font_size": int(self.font_size_slider.value),
        }
        
        if self.on_apply:
            self.on_apply(settings)
        
        self.close()
    
    def handle_cancel(self, e):
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings values"""
        return {
            "theme": self.theme_dropdown.value,
            "font_size": int(self.font_size_slider.value),
        }


def create_settings_view(
    on_theme_change: Optional[Callable[[str], None]] = None,
    on_font_size_change: Optional[Callable[[int], None]] = None,
    current_theme: str = "Light",
    current_font_size: int = 14,
) -> ft.Container:
    """Create a settings view as a standalone container"""
    
    def handle_theme_change(e):
        if on_theme_change:
            on_theme_change(e.control.value)
    
    def handle_font_size_change(e):
        font_size_text.value = f"Font Size: {int(e.control.value)}"
        font_size_text.update()
        if on_font_size_change:
            on_font_size_change(int(e.control.value))
    
    theme_dropdown = ft.Dropdown(
        label="Theme",
        value=current_theme,
        options=[
            ft.dropdown.Option("Light"),
            ft.dropdown.Option("Dark"),
        ],
        on_change=handle_theme_change,
    )
    
    font_size_text = ft.Text(f"Font Size: {current_font_size}")
    
    font_size_slider = ft.Slider(
        min=8,
        max=20,
        value=current_font_size,
        divisions=12,
        label="{value}",
        on_change=handle_font_size_change,
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Appearance", size=18, weight=ft.FontWeight.W_500),
                                ft.Divider(height=1),
                                ft.Container(height=10),
                                theme_dropdown,
                                ft.Container(height=20),
                                font_size_text,
                                font_size_slider,
                            ],
                        ),
                        padding=20,
                    ),
                ),
            ],
        ),
        expand=True,
        padding=20,
    )