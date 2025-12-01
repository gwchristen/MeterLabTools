"""
UI Resources and helper functions for MeterLabTools
Framework-agnostic color and font constants
"""


class UIResources:
    """UI Resources and helper functions"""
    
    @staticmethod
    def get_icon_emoji(icon_name: str) -> str:
        """Get emoji representation for icon name"""
        icon_map = {
            'calculator': '🧮',
            'database': '🗄️',
            'users': '👥',
            'chart': '📊',
            'tasks': '✓',
            'clock': '⏰',
            'wallet': '💼',
            'layers': '📦',
            'history': '📜',
            'settings': '⚙️',
            'help': '❓',
        }
        return icon_map.get(icon_name, '📱')
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class Colors:
    """Color constants - compatible with Flet"""
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2ecc71"
    ACCENT_COLOR = "#e74c3c"
    BACKGROUND_COLOR = "#ecf0f1"
    TEXT_COLOR = "#2c3e50"
    LIGHT_BG = "#ffffff"
    DARK_BG = "#2c3e50"
    DARK_TEXT = "#ecf0f1"
    
    # Additional colors for Flet
    SURFACE_LIGHT = "#f8f9fa"
    SURFACE_DARK = "#1e1e1e"
    ON_SURFACE_LIGHT = "#000000"
    ON_SURFACE_DARK = "#ffffff"
    DIVIDER_LIGHT = "#e9ecef"
    DIVIDER_DARK = "#3d3d3d"


class Fonts:
    """Font constants"""
    DEFAULT_FONT = "Arial"
    HEADER_FONT = "Helvetica"
    MONO_FONT = "Courier New"
    
    # Font sizes
    SIZE_SMALL = 12
    SIZE_NORMAL = 14
    SIZE_LARGE = 18
    SIZE_TITLE = 24
    SIZE_HEADER = 32