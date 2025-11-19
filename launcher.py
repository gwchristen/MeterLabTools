import sys
import json
import os
from datetime import datetime
from pathlib import Path

# PyQt6 imports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

# Import from our modules
from database.db_manager import DatabaseManager
from database.init_db import init_db
from shared.constants import APP_NAME, APP_VERSION
from shared.utils import current_datetime_utc
from ui.styles import ThemeManager, Theme
from ui.resources import Colors, UIResources


class MeterLabToolsLauncher(QMainWindow):
    """Main MeterLabTools Launcher Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize database
        print("Initializing database...")
        try:
            init_db('meter_lab_tools.db')
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
        
        self.db = DatabaseManager('meter_lab_tools.db')
        self.db.connect()
        
        print("Loading configuration...")
        self.config = self.load_config()
        
        print("Setting up UI...")
        self.setup_ui()
        
        print("Launcher ready!")
    
    def load_config(self):
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
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout (sidebar + content)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 1)
        
        # Main content area with modules grid
        content = self.create_modules_content()
        main_layout.addWidget(content, 3)
        
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply initial theme
        self.apply_light_theme()
    
    def create_sidebar(self):
        """Create the sidebar with recently used modules"""
        sidebar_frame = QFrame()
        sidebar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(10)
        
        # Title
        title = QLabel("Recently Used")
        title_font = QFont("Arial", 12)
        title_font.setBold(True)
        title.setFont(title_font)
        sidebar_layout.addWidget(title)
        
        # Recently used modules
        try:
            recent = self.db.get_recently_used(limit=5)
            if recent:
                for module_dict in recent:
                    module_id = module_dict.get('module_id', 'Unknown')
                    btn = QPushButton(module_id)
                    btn.setMinimumHeight(50)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.clicked.connect(lambda checked, m=module_id: self.launch_module(m))
                    sidebar_layout.addWidget(btn)
            else:
                empty_label = QLabel("No recent modules yet")
                empty_label.setStyleSheet("color: gray; font-style: italic;")
                sidebar_layout.addWidget(empty_label)
        except Exception as e:
            error_label = QLabel(f"Error loading recent")
            sidebar_layout.addWidget(error_label)
            print(f"Error getting recently used modules: {e}")
        
        # Spacer
        sidebar_layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setMinimumHeight(40)
        settings_btn.clicked.connect(self.show_settings)
        sidebar_layout.addWidget(settings_btn)
        
        # Help button
        help_btn = QPushButton("❓ Help")
        help_btn.setMinimumHeight(40)
        help_btn.clicked.connect(self.show_help)
        sidebar_layout.addWidget(help_btn)
        
        sidebar_frame.setLayout(sidebar_layout)
        sidebar_frame.setMaximumWidth(220)
        
        return sidebar_frame
    
    def create_modules_content(self):
        """Create the modules grid content area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Container for grid
        container = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add module buttons
        modules = self.config.get('modules', [])
        print(f"Creating {len(modules)} module buttons")
        
        if not modules:
            no_modules_label = QLabel("No modules found in config.json")
            grid_layout.addWidget(no_modules_label)
        else:
            for idx, module in enumerate(modules):
                btn = self.create_module_button(module)
                row = idx // 2
                col = idx % 2
                grid_layout.addWidget(btn, row, col)
        
        # Add stretch to fill remaining space
        grid_layout.setRowStretch(len(modules) // 2 + 1, 1)
        grid_layout.setColumnStretch(2, 1)
        
        container.setLayout(grid_layout)
        scroll.setWidget(container)
        
        return scroll
    
    def create_module_button(self, module):
        """Create a button for a module"""
        btn = QPushButton()
        btn.setMinimumSize(QSize(450, 130))
        btn.setMaximumSize(QSize(500, 150))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Get module info
        name = module.get('name', 'Unknown Module')
        description = module.get('description', 'No description available')
        version = module.get('version', '1.0')
        
        # Format button text with newlines
        button_text = f"{name}\n\n{description}\n\nv{version}"
        btn.setText(button_text)
        
        # Set font
        font = QFont("Arial", 10)
        btn.setFont(font)
        
        # Store module info
        btn.module_name = name
        btn.module_id = name
        
        # Connect click
        btn.clicked.connect(lambda: self.launch_module(btn.module_id))
        
        return btn
    
    def launch_module(self, module_id):
        """Launch a selected module"""
        print(f"\n{'='*50}")
        print(f"Launching module: {module_id}")
        print(f"Time: {current_datetime_utc()}")
        print(f"User: gwchristen")
        print(f"{'='*50}\n")
        
        # Record in database
        try:
            timestamp = current_datetime_utc()
            self.db.add_recent_module(module_id, timestamp)
            print(f"Recorded module usage in database")
        except Exception as e:
            print(f"Error recording module: {e}")
        
        # Show message
        msg = (f"Module '{module_id}' launched!\n\n"
               f"Timestamp: {current_datetime_utc()}\n"
               f"User: gwchristen\n\n"
               f"This is a placeholder. Implement actual module launching here.")
        
        QMessageBox.information(self, "Module Launched", msg)
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Refresh Modules', self.refresh_modules)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # View Menu
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Light Theme', self.apply_light_theme)
        view_menu.addAction('Dark Theme', self.apply_dark_theme)
        view_menu.addSeparator()
        view_menu.addAction('Refresh', self.refresh_modules)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
        help_menu.addAction('Documentation', self.show_documentation)
    
    def refresh_modules(self):
        """Refresh the modules list"""
        print("Refreshing modules...")
        self.config = self.load_config()
        
        # Clear current layout
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.deleteLater()
        
        # Recreate UI
        self.setup_ui()
        print("Modules refreshed successfully")
    
    def apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QMenuBar {
                background-color: #f8f9fa;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #e9ecef;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QPushButton {
                background-color: #ecf0f1;
                color: #000000;
                border: 1px solid #bdc3c7;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: #ffffff;
                border: 1px solid #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QLabel {
                color: #000000;
            }
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
            }
            QScrollArea {
                background-color: #ffffff;
            }
        """)
        print("Light theme applied")
    
    def apply_dark_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: #ffffff;
                border: 1px solid #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
            QLabel {
                color: #ffffff;
            }
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
            }
            QScrollArea {
                background-color: #1e1e1e;
            }
        """)
        print("Dark theme applied")
    
    def show_settings(self):
        """Show settings dialog"""
        msg = "Settings dialog - Coming soon!"
        QMessageBox.information(self, "Settings", msg)
    
    def show_help(self):
        """Show help dialog"""
        msg = (
            "MeterLabTools v1.0.0\n\n"
            "A modular launcher for Python converted spreadsheets\n"
            "that are tools for operations.\n\n"
            "Features:\n"
            "• 8 pre-configured modules\n"
            "• Recently used tracking\n"
            "• Light/Dark themes\n"
            "• Database persistence\n\n"
            "Created by: gwchristen"
        )
        QMessageBox.information(self, "Help", msg)
    
    def show_about(self):
        """Show about dialog"""
        msg = (
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "A modular launcher for operational tools\n\n"
            f"Current Time: {current_datetime_utc()}\n"
            f"Current User: gwchristen\n\n"
            "© 2025 - All rights reserved"
        )
        QMessageBox.information(self, "About", msg)
    
    def show_documentation(self):
        """Show documentation"""
        msg = (
            "Documentation\n\n"
            "To launch a module:\n"
            "1. Click on any module card in the main area\n"
            "2. The module will be launched\n\n"
            "Recently used modules appear in the left sidebar\n"
            "for quick access.\n\n"
            "Use View menu to switch themes.\n"
            "Use File menu to refresh or exit."
        )
        QMessageBox.information(self, "Documentation", msg)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    print(f"\n{'='*60}")
    print(f"MeterLabTools Launcher")
    print(f"Version: {APP_VERSION}")
    print(f"Started: {current_datetime_utc()}")
    print(f"User: gwchristen")
    print(f"{'='*60}\n")
    
    launcher = MeterLabToolsLauncher()
    launcher.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()