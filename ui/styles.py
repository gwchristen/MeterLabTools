from typing import Dict, Optional

class Theme:
    """Theme class for managing application themes"""
    
    def __init__(self, name: str, styles: Dict[str, str]):
        self.name = name
        self.styles = styles
    
    def apply(self):
        """Apply theme styles"""
        pass
    
    def get_style(self, key: str, default: str = "") -> str:
        """Get a style value"""
        return self.styles.get(key, default)


class ThemeManager:
    """Manage application themes"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
    
    def add_theme(self, theme: Theme) -> None:
        """Add a theme"""
        self.themes[theme.name] = theme
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self.current_theme.apply()
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