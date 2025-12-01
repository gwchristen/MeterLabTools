"""
Theme management for MeterLabTools
Works with Flet's native theming system
"""

from typing import Dict, Optional


class Theme:
    """Theme class for managing application themes"""
    
    # Theme modes
    LIGHT = "light"
    DARK = "dark"
    
    def __init__(self, name: str, styles: Optional[Dict[str, str]] = None):
        self.name = name
        self.styles = styles or {}
    
    def apply(self):
        """Apply theme styles - handled by Flet's native theming"""
        pass
    
    def get_style(self, key: str, default: str = "") -> str:
        """Get a style value"""
        return self.styles.get(key, default)
    
    def is_dark(self) -> bool:
        """Check if this is a dark theme"""
        return self.name.lower() == self.DARK


class ThemeManager:
    """Manage application themes - simplified for Flet"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {
            "Light": Theme("Light"),
            "Dark": Theme("Dark"),
        }
        self.current_theme: Optional[Theme] = self.themes.get("Light")
    
    def add_theme(self, theme: Theme) -> None:
        """Add a theme"""
        self.themes[theme.name] = theme
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            return True
        return False
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get current theme"""
        return self.current_theme
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name, None)
    
    def list_themes(self) -> list:
        """List all themes"""
        return list(self.themes.keys())
    
    def toggle_theme(self) -> str:
        """Toggle between light and dark theme"""
        if self.current_theme and self.current_theme.name == "Light":
            self.set_theme("Dark")
            return "Dark"
        else:
            self.set_theme("Light")
            return "Light"