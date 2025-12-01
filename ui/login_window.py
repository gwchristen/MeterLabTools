"""
Login Window Component for MeterLabTools - Flet-based
"""

import flet as ft
from typing import Callable, Optional


class LoginWindow:
    """Login/Authentication component for Flet"""
    
    def __init__(
        self, 
        page: ft.Page, 
        on_login: Optional[Callable[[str, str], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        self.page = page
        self.on_login = on_login
        self.on_cancel = on_cancel
        self.dialog: Optional[ft.AlertDialog] = None
        
        # Input fields
        self.username_field = ft.TextField(
            label="Username",
            autofocus=True,
            on_submit=lambda e: self.password_field.focus(),
        )
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            on_submit=lambda e: self.handle_login(e),
        )
        self.error_text = ft.Text(
            "",
            color=ft.Colors.ERROR,
            visible=False,
            size=12,
        )
    
    def build_dialog(self) -> ft.AlertDialog:
        """Build the login dialog"""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.username_field,
                        ft.Container(height=10),
                        self.password_field,
                        self.error_text,
                    ],
                    tight=True,
                    spacing=5,
                ),
                width=300,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.handle_cancel),
                ft.FilledButton("Login", on_click=self.handle_login),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return self.dialog
    
    def show(self):
        """Show the login dialog"""
        if not self.dialog:
            self.build_dialog()
        
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
    
    def close(self):
        """Close the login dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
    
    def handle_login(self, e):
        """Handle login button click"""
        username = self.username_field.value or ""
        password = self.password_field.value or ""
        
        if not username:
            self.show_error("Please enter a username")
            return
        
        if not password:
            self.show_error("Please enter a password")
            return
        
        # Clear error
        self.error_text.visible = False
        
        if self.on_login:
            self.on_login(username, password)
        
        self.close()
    
    def handle_cancel(self, e):
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def show_error(self, message: str):
        """Show an error message"""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()
    
    def clear_fields(self):
        """Clear all input fields"""
        self.username_field.value = ""
        self.password_field.value = ""
        self.error_text.visible = False
        self.page.update()


def create_login_view(
    on_login: Optional[Callable[[str, str], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None
) -> ft.Container:
    """Create a login view as a standalone container (for full-page login)"""
    
    username_field = ft.TextField(
        label="Username",
        autofocus=True,
        width=300,
    )
    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=300,
    )
    error_text = ft.Text(
        "",
        color=ft.Colors.ERROR,
        visible=False,
        size=12,
    )
    
    def handle_login(e):
        username = username_field.value or ""
        password = password_field.value or ""
        
        if not username or not password:
            error_text.value = "Please enter username and password"
            error_text.visible = True
            error_text.update()
            return
        
        if on_login:
            on_login(username, password)
    
    def handle_cancel(e):
        if on_cancel:
            on_cancel()
    
    return ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Login", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(height=20),
                        username_field,
                        ft.Container(height=10),
                        password_field,
                        error_text,
                        ft.Container(height=20),
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancel", on_click=handle_cancel),
                                ft.FilledButton("Login", on_click=handle_login),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
            ),
        ),
        alignment=ft.alignment.center,
        expand=True,
    )