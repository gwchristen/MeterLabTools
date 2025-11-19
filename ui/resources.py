from PyQt6.QtGui import QColor, QFont

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
        }
        return icon_map.get(icon_name, '📱')
    
    @staticmethod
    def get_color_from_hex(hex_color: str) -> QColor:
        """Convert hex color string to QColor"""
        return QColor(hex_color)
    
    @staticmethod
    def get_font(size: int = 10, bold: bool = False, family: str = "Arial") -> QFont:
        """Create a font with specified properties"""
        font = QFont(family)
        font.setPointSize(size)
        font.setBold(bold)
        return font


class Colors:
    """Color constants"""
    PRIMARY_COLOR = "#3498db"
    SECONDARY_COLOR = "#2ecc71"
    ACCENT_COLOR = "#e74c3c"
    BACKGROUND_COLOR = "#ecf0f1"
    TEXT_COLOR = "#2c3e50"
    LIGHT_BG = "#ffffff"
    DARK_BG = "#2c3e50"
    DARK_TEXT = "#ecf0f1"


class Fonts:
    """Font constants"""
    DEFAULT_FONT = "Arial"
    HEADER_FONT = "Helvetica"
    MONO_FONT = "Courier New"