"""
Theme Manager - Professional color schemes and styling
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorScheme:
    """Color scheme for theming"""
    
    # Primary colors
    primary: str
    primary_hover: str
    primary_pressed: str
    primary_light: str
    
    # Secondary colors
    secondary: str
    secondary_hover: str
    
    # Background colors
    background: str
    background_alt: str
    surface: str
    surface_hover: str
    
    # Text colors
    text: str
    text_secondary: str
    text_disabled: str
    
    # Accent colors
    accent: str
    success: str
    warning: str
    error: str
    info: str
    
    # Border colors
    border: str
    border_light: str
    
    # Grid colors
    grid_header: str
    grid_row_alt: str
    grid_row_hover: str
    grid_selected: str


class ThemeManager:
    """Manages themes and provides consistent styling"""
    
    # WCAG 2.1 AA compliant color schemes
    LIGHT_THEME = ColorScheme(
        # Primary - Professional blue
        primary="#2563eb",
        primary_hover="#1d4ed8",
        primary_pressed="#1e40af",
        primary_light="#dbeafe",
        
        # Secondary - Neutral gray
        secondary="#64748b",
        secondary_hover="#475569",
        
        # Backgrounds
        background="#ffffff",
        background_alt="#f8fafc",
        surface="#ffffff",
        surface_hover="#f1f5f9",
        
        # Text
        text="#0f172a",
        text_secondary="#475569",
        text_disabled="#94a3b8",
        
        # Accents
        accent="#8b5cf6",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        info="#0ea5e9",
        
        # Borders
        border="#e2e8f0",
        border_light="#f1f5f9",
        
        # Grid
        grid_header="#1e293b",
        grid_row_alt="#f8fafc",
        grid_row_hover="#e0f2fe",
        grid_selected="#dbeafe",
    )
    
    DARK_THEME = ColorScheme(
        # Primary - Professional blue
        primary="#3b82f6",
        primary_hover="#2563eb",
        primary_pressed="#1d4ed8",
        primary_light="#1e3a8a",
        
        # Secondary - Neutral gray
        secondary="#94a3b8",
        secondary_hover="#cbd5e1",
        
        # Backgrounds
        background="#0f172a",
        background_alt="#1e293b",
        surface="#1e293b",
        surface_hover="#334155",
        
        # Text
        text="#f8fafc",
        text_secondary="#cbd5e1",
        text_disabled="#64748b",
        
        # Accents
        accent="#a78bfa",
        success="#4ade80",
        warning="#fbbf24",
        error="#f87171",
        info="#38bdf8",
        
        # Borders
        border="#334155",
        border_light="#475569",
        
        # Grid
        grid_header="#0f172a",
        grid_row_alt="#1e293b",
        grid_row_hover="#1e3a8a",
        grid_selected="#1e40af",
    )
    
    @staticmethod
    def get_stylesheet(theme: str = "Light") -> str:
        """Get complete stylesheet for theme"""
        colors = ThemeManager.LIGHT_THEME if theme == "Light" else ThemeManager.DARK_THEME
        
        return f"""
            /* Main Window */
            QMainWindow {{
                background-color: {colors.background};
            }}
            
            /* Base Widget */
            QWidget {{
                background-color: {colors.background};
                color: {colors.text};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-height: 36px;
                transition: all 0.2s ease;
            }}
            
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.primary_pressed};
            }}
            
            QPushButton:disabled {{
                background-color: {colors.border};
                color: {colors.text_disabled};
            }}
            
            QPushButton[class="secondary"] {{
                background-color: {colors.surface};
                color: {colors.text};
                border: 2px solid {colors.border};
            }}
            
            QPushButton[class="secondary"]:hover {{
                background-color: {colors.surface_hover};
                border-color: {colors.primary};
            }}
            
            QPushButton[class="success"] {{
                background-color: {colors.success};
            }}
            
            QPushButton[class="warning"] {{
                background-color: {colors.warning};
            }}
            
            QPushButton[class="error"] {{
                background-color: {colors.error};
            }}
            
            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                border: 2px solid {colors.border};
                padding: 8px 12px;
                border-radius: 6px;
                background-color: {colors.surface};
                color: {colors.text};
                selection-background-color: {colors.primary_light};
                min-height: 36px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {colors.primary};
                outline: none;
            }}
            
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {colors.background_alt};
                color: {colors.text_disabled};
                border-color: {colors.border_light};
            }}
            
            /* Spinboxes and ComboBoxes */
            QSpinBox, QDoubleSpinBox, QComboBox {{
                border: 2px solid {colors.border};
                padding: 8px 12px;
                border-radius: 6px;
                background-color: {colors.surface};
                color: {colors.text};
                min-height: 36px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {colors.primary};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {colors.text};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 2px solid {colors.border};
                background-color: {colors.surface};
                color: {colors.text};
                selection-background-color: {colors.primary};
                selection-color: white;
                padding: 4px;
            }}
            
            /* Labels */
            QLabel {{
                color: {colors.text};
                background: transparent;
            }}
            
            QLabel[class="heading"] {{
                font-size: 24px;
                font-weight: 700;
                color: {colors.text};
            }}
            
            QLabel[class="subheading"] {{
                font-size: 18px;
                font-weight: 600;
                color: {colors.text};
            }}
            
            QLabel[class="caption"] {{
                font-size: 12px;
                color: {colors.text_secondary};
            }}
            
            /* Table Widget */
            QTableWidget {{
                border: 2px solid {colors.border};
                gridline-color: {colors.border_light};
                background-color: {colors.surface};
                color: {colors.text};
                border-radius: 8px;
                alternate-background-color: {colors.grid_row_alt};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            
            QTableWidget::item:hover {{
                background-color: {colors.grid_row_hover};
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors.grid_selected};
                color: {colors.text};
            }}
            
            QHeaderView::section {{
                background-color: {colors.grid_header};
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            QHeaderView::section:hover {{
                background-color: {colors.primary};
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                border: none;
                background: {colors.background_alt};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colors.border};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {colors.secondary};
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {colors.background_alt};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {colors.border};
                border-radius: 6px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {colors.secondary};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                border: none;
                background: none;
            }}
            
            /* Tab Widget */
            QTabWidget::pane {{
                border: 2px solid {colors.border};
                border-radius: 8px;
                background-color: {colors.surface};
                top: -2px;
            }}
            
            QTabBar::tab {{
                background-color: {colors.background_alt};
                color: {colors.text_secondary};
                padding: 12px 24px;
                border: 2px solid {colors.border};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: 600;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors.surface};
                color: {colors.primary};
                border-bottom: 2px solid {colors.surface};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {colors.surface_hover};
                color: {colors.text};
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {colors.grid_header};
                color: white;
                padding: 4px;
                border-bottom: 3px solid {colors.primary};
            }}
            
            QMenuBar::item {{
                padding: 8px 16px;
                background: transparent;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors.primary};
            }}
            
            QMenu {{
                background-color: {colors.surface};
                color: {colors.text};
                border: 2px solid {colors.border};
                border-radius: 8px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 10px 24px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {colors.primary};
                color: white;
            }}
            
            /* Frames */
            QFrame {{
                background-color: {colors.surface};
                border: 2px solid {colors.border};
                border-radius: 8px;
            }}
            
            QFrame[class="card"] {{
                background-color: {colors.surface};
                border: 2px solid {colors.border};
                border-radius: 12px;
                padding: 16px;
            }}
            
            QFrame[class="sidebar"] {{
                background-color: {colors.background_alt};
                border-right: 2px solid {colors.border};
                border-radius: 0px;
            }}
            
            /* Dialogs */
            QDialog {{
                background-color: {colors.background};
            }}
            
            QDialogButtonBox {{
                background: transparent;
            }}
            
            /* Scroll Area */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                border: 2px solid {colors.border};
                border-radius: 6px;
                text-align: center;
                background-color: {colors.surface};
                color: {colors.text};
                min-height: 24px;
            }}
            
            QProgressBar::chunk {{
                background-color: {colors.primary};
                border-radius: 4px;
            }}
            
            /* Tooltips */
            QToolTip {{
                background-color: {colors.grid_header};
                color: white;
                border: 2px solid {colors.primary};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
        """
    
    @staticmethod
    def get_colors(theme: str = "Light") -> ColorScheme:
        """Get color scheme for theme"""
        return ThemeManager.LIGHT_THEME if theme == "Light" else ThemeManager.DARK_THEME
