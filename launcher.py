"""
MeterLabTools Launcher - Flet-based UI
A modern, Material Design launcher for operational tools.
"""

import flet as ft
import json
import os
from typing import List, Dict, Any, Optional

# Import from our modules
from database.db_manager import DatabaseManager
from database.init_db import init_db
from shared.constants import APP_NAME, APP_VERSION
from shared.utils import current_datetime_utc


class MeterLabToolsLauncher:
    """Main MeterLabTools Launcher Application using Flet"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_view = "home"
        self.db: Optional[DatabaseManager] = None
        self.config: Dict[str, Any] = {}
        
        # Setup page
        self.setup_page()
        
        # Initialize database
        print("Initializing database...")
        try:
            init_db('meter_lab_tools.db')
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
        
        self.db = DatabaseManager('meter_lab_tools.db')
        self.db.connect()
        
        # Load configuration
        print("Loading configuration...")
        self.config = self.load_config()
        
        # Build UI
        print("Setting up UI...")
        self.build_ui()
        
        print("Launcher ready!")
    
    def setup_page(self):
        """Configure the page settings"""
        self.page.title = f"{APP_NAME} v{APP_VERSION}"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
    
    def load_config(self) -> Dict[str, Any]:
        """Load module configuration from config.json"""
        try:
            config_path = 'config.json'
            if not os.path.exists(config_path):
                print(f"Error: {config_path} not found")
                return {"modules": []}
            
            with open(config_path, 'r') as f:
                config = json.load(f)
                print(f"Loaded {len(config.get('modules', []))} modules")
                return config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config.json - {e}")
            return {"modules": []}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"modules": []}
    
    def build_ui(self):
        """Build the main user interface"""
        # Create AppBar
        app_bar = self.create_app_bar()
        
        # Create NavigationRail
        nav_rail = self.create_navigation_rail()
        
        # Create main content area
        self.content_area = ft.Container(
            content=self.create_home_view(),
            expand=True,
            padding=20,
        )
        
        # Main layout with NavigationRail and content
        main_content = ft.Row(
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
            spacing=0,
        )
        
        # Set page controls
        self.page.appbar = app_bar
        self.page.add(main_content)
    
    def create_app_bar(self) -> ft.AppBar:
        """Create the application bar"""
        return ft.AppBar(
            leading=ft.Icon(ft.Icons.DASHBOARD),
            leading_width=50,
            title=ft.Text(f"{APP_NAME} v{APP_VERSION}", weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Modules",
                    on_click=self.refresh_modules,
                ),
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE,
                    tooltip="Toggle Theme",
                    on_click=self.toggle_theme,
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="About",
                            icon=ft.Icons.INFO_OUTLINE,
                            on_click=self.show_about,
                        ),
                        ft.PopupMenuItem(
                            text="Documentation",
                            icon=ft.Icons.DESCRIPTION,
                            on_click=self.show_documentation,
                        ),
                    ],
                ),
            ],
        )
    
    def create_navigation_rail(self) -> ft.NavigationRail:
        """Create the navigation rail"""
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.HISTORY_OUTLINED,
                    selected_icon=ft.Icons.HISTORY,
                    label="Recent",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.HELP_OUTLINE,
                    selected_icon=ft.Icons.HELP,
                    label="Help",
                ),
            ],
            on_change=self.on_nav_change,
        )
    
    def on_nav_change(self, e):
        """Handle navigation rail selection changes"""
        index = e.control.selected_index
        
        if index == 0:
            self.current_view = "home"
            self.content_area.content = self.create_home_view()
        elif index == 1:
            self.current_view = "recent"
            self.content_area.content = self.create_recent_view()
        elif index == 2:
            self.current_view = "settings"
            self.content_area.content = self.create_settings_view()
        elif index == 3:
            self.current_view = "help"
            self.content_area.content = self.create_help_view()
        
        self.page.update()
    
    def create_home_view(self) -> ft.Control:
        """Create the home view with module cards grid"""
        modules = self.config.get('modules', [])
        
        if not modules:
            return ft.Container(
                content=ft.Text(
                    "No modules found in config.json",
                    size=16,
                    color=ft.Colors.GREY_500,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Create module cards
        cards = []
        for module in modules:
            card = self.create_module_card(module)
            cards.append(card)
        
        # Create responsive grid using Row with wrap
        grid = ft.Column(
            controls=[
                ft.Row(
                    controls=cards,
                    wrap=True,
                    spacing=20,
                    run_spacing=20,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Modules",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                grid,
            ],
            expand=True,
        )
    
    def create_module_card(self, module: Dict[str, Any]) -> ft.Card:
        """Create a card for a module"""
        name = module.get('name', 'Unknown Module')
        description = module.get('description', 'No description available')
        version = module.get('version', '1.0')
        author = module.get('author', 'Unknown')
        
        # Get icon based on module name
        icon = self.get_module_icon(name)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon, size=32, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    name,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            description,
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(expand=True),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"v{version}",
                                    size=12,
                                    color=ft.Colors.GREY_500,
                                ),
                                ft.Container(expand=True),
                                ft.FilledButton(
                                    text="Launch",
                                    icon=ft.Icons.PLAY_ARROW,
                                    on_click=lambda e, m=name: self.launch_module(m),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=5,
                ),
                padding=20,
                width=350,
                height=180,
            ),
            elevation=2,
        )
    
    def get_module_icon(self, module_name: str) -> str:
        """Get an icon for a module based on its name"""
        icon_map = {
            "Created Histories": ft.Icons.HISTORY_EDU,
            "Sales Calculator": ft.Icons.CALCULATE,
            "Employee Directory": ft.Icons.PEOPLE,
            "Financial Reports": ft.Icons.BAR_CHART,
            "Project Tracker": ft.Icons.TRACK_CHANGES,
            "Time Logging": ft.Icons.ACCESS_TIME,
            "Budget Planner": ft.Icons.ACCOUNT_BALANCE_WALLET,
            "Resource Allocation": ft.Icons.INVENTORY_2,
        }
        return icon_map.get(module_name, ft.Icons.APPS)
    
    def create_recent_view(self) -> ft.Control:
        """Create the recently used modules view"""
        try:
            recent = self.db.get_recently_used(limit=10) if self.db else []
        except Exception as e:
            print(f"Error getting recently used modules: {e}")
            recent = []
        
        if not recent:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.HISTORY, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No recently used modules",
                            size=18,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Text(
                            "Launch a module to see it here",
                            size=14,
                            color=ft.Colors.GREY_400,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Create list tiles for recent modules
        tiles = []
        for idx, module_dict in enumerate(recent):
            module_id = module_dict.get('module_id', 'Unknown')
            timestamp = module_dict.get('timestamp', '')
            
            tile = ft.ListTile(
                leading=ft.Icon(self.get_module_icon(module_id)),
                title=ft.Text(module_id, weight=ft.FontWeight.W_500),
                subtitle=ft.Text(f"Last used: {timestamp}"),
                trailing=ft.IconButton(
                    icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                    tooltip="Launch",
                    on_click=lambda e, m=module_id: self.launch_module(m),
                ),
                on_click=lambda e, m=module_id: self.launch_module(m),
            )
            tiles.append(tile)
            if idx < len(recent) - 1:
                tiles.append(ft.Divider(height=1))
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Recently Used",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(controls=tiles),
                        padding=10,
                    ),
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def create_settings_view(self) -> ft.Control:
        """Create the settings view"""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Settings",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Appearance", size=18, weight=ft.FontWeight.W_500),
                                ft.Divider(height=1),
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.DARK_MODE),
                                    title=ft.Text("Dark Mode"),
                                    subtitle=ft.Text("Toggle dark/light theme"),
                                    trailing=ft.Switch(
                                        value=self.page.theme_mode == ft.ThemeMode.DARK,
                                        on_change=self.on_theme_switch_change,
                                    ),
                                ),
                                ft.Container(height=20),
                                ft.Text("Database", size=18, weight=ft.FontWeight.W_500),
                                ft.Divider(height=1),
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.DELETE_SWEEP),
                                    title=ft.Text("Clear Recent History"),
                                    subtitle=ft.Text("Remove all recently used entries"),
                                    trailing=ft.OutlinedButton(
                                        text="Clear",
                                        on_click=self.clear_recent_history,
                                    ),
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=20,
                    ),
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def create_help_view(self) -> ft.Control:
        """Create the help view"""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Help & About",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                                    title=ft.Text("About MeterLabTools"),
                                    subtitle=ft.Text(
                                        f"Version {APP_VERSION}\n"
                                        "A modular launcher for operational tools\n"
                                        "Created by: gwchristen"
                                    ),
                                ),
                                ft.Divider(height=1),
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.APPS),
                                    title=ft.Text("Modules"),
                                    subtitle=ft.Text(
                                        "• 8 pre-configured modules\n"
                                        "• Click 'Launch' to start a module\n"
                                        "• Recently used modules are tracked"
                                    ),
                                ),
                                ft.Divider(height=1),
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.NAVIGATION),
                                    title=ft.Text("Navigation"),
                                    subtitle=ft.Text(
                                        "• Home: View all modules\n"
                                        "• Recent: See recently used modules\n"
                                        "• Settings: Customize appearance\n"
                                        "• Help: View this information"
                                    ),
                                ),
                                ft.Divider(height=1),
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.PALETTE),
                                    title=ft.Text("Themes"),
                                    subtitle=ft.Text(
                                        "Use the theme toggle in the app bar or\n"
                                        "Settings to switch between light and dark modes"
                                    ),
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=10,
                    ),
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def launch_module(self, module_id: str):
        """Launch a selected module"""
        print(f"\n{'='*50}")
        print(f"Launching module: {module_id}")
        print(f"Time: {current_datetime_utc()}")
        print(f"User: gwchristen")
        print(f"{'='*50}\n")
        
        # Record in database
        try:
            if self.db:
                timestamp = current_datetime_utc()
                self.db.add_recent_module(module_id, timestamp)
                print("Recorded module usage in database")
        except Exception as e:
            print(f"Error recording module: {e}")
        
        # Show snackbar for module launch
        if module_id == "Created Histories":
            self.launch_created_histories()
        else:
            self.show_snackbar(f"{module_id} - Coming soon!")
    
    def launch_created_histories(self):
        """Launch the Created Histories module"""
        try:
            import subprocess
            import sys
            import os
            
            # Get the path to the module directory and app file
            module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', 'module_2')
            module_path = os.path.join(module_dir, 'app.py')
            
            # Verify the module exists
            if not os.path.exists(module_path):
                self.show_snackbar(f"Module not found: {module_path}", is_error=True)
                return
            
            # Launch the module in a separate process with correct working directory
            self.show_snackbar("Launching Created Histories module...")
            subprocess.Popen(
                [sys.executable, module_path],
                cwd=module_dir,  # Set working directory to module folder
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"Created Histories module launched from: {module_dir}")
            
        except Exception as e:
            error_msg = f"Error launching Created Histories: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.show_snackbar(error_msg, is_error=True)
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            # Update button icon if it's an IconButton
            if hasattr(e.control, 'icon'):
                e.control.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            # Update button icon if it's an IconButton
            if hasattr(e.control, 'icon'):
                e.control.icon = ft.Icons.LIGHT_MODE
        
        self.page.update()
        print(f"Theme switched to: {self.page.theme_mode}")
    
    def on_theme_switch_change(self, e):
        """Handle theme switch toggle in settings"""
        if e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.page.update()
        print(f"Theme switched to: {self.page.theme_mode}")
    
    def refresh_modules(self, e):
        """Refresh the modules list"""
        print("Refreshing modules...")
        self.config = self.load_config()
        
        # Update the content area if on home view
        if self.current_view == "home":
            self.content_area.content = self.create_home_view()
            self.page.update()
        
        self.show_snackbar("Modules refreshed successfully")
        print("Modules refreshed successfully")
    
    def clear_recent_history(self, e):
        """Clear the recent history"""
        # Show confirmation dialog
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def confirm_clear(e):
            try:
                if self.db:
                    self.db.execute_update("DELETE FROM recently_used")
                    self.show_snackbar("Recent history cleared")
                    print("Recent history cleared")
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", is_error=True)
            finally:
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear Recent History"),
            content=ft.Text("Are you sure you want to clear all recent history?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Clear", on_click=confirm_clear),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_about(self, e):
        """Show about dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("About MeterLabTools"),
            content=ft.Column(
                controls=[
                    ft.Text(f"{APP_NAME} v{APP_VERSION}", weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("A modular launcher for operational tools"),
                    ft.Container(height=10),
                    ft.Text(f"Current Time: {current_datetime_utc()}"),
                    ft.Text("Current User: gwchristen"),
                    ft.Container(height=10),
                    ft.Text("© 2025 - All rights reserved", size=12, color=ft.Colors.GREY_500),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog)),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def show_documentation(self, e):
        """Show documentation dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Documentation"),
            content=ft.Column(
                controls=[
                    ft.Text("How to use MeterLabTools:", weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("1. Navigate using the rail on the left"),
                    ft.Text("2. Click 'Launch' on any module card"),
                    ft.Text("3. Recently used modules appear in Recent"),
                    ft.Container(height=10),
                    ft.Text("Keyboard Shortcuts:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Use theme toggle to switch themes"),
                    ft.Text("• Use refresh button to reload modules"),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dialog(dialog)),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog: ft.AlertDialog):
        """Close a dialog"""
        dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message: str, is_error: bool = False):
        """Show a snackbar notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.ERROR if is_error else None,
            action="OK",
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()


def main(page: ft.Page):
    """Main application entry point"""
    print(f"\n{'='*60}")
    print(f"MeterLabTools Launcher (Flet)")
    print(f"Version: {APP_VERSION}")
    print(f"Started: {current_datetime_utc()}")
    print(f"User: gwchristen")
    print(f"{'='*60}\n")
    
    MeterLabToolsLauncher(page)


if __name__ == '__main__':
    ft.app(target=main)