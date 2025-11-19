# theme_management.py

class Theme:
    def __init__(self, name, styles):
        self.name = name
        self.styles = styles

    def apply(self):
        # Logic to apply styles
        pass

class ThemeManager:
    def __init__(self):
        self.themes = {}
        self.current_theme = None

    def add_theme(self, theme):
        self.themes[theme.name] = theme

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            self.current_theme.apply()
        else:
            raise ValueError(f'No theme named {theme_name}')

# Example usage:

if __name__ == '__main__':
    light_theme = Theme('Light', styles={'background': 'white', 'text': 'black'})
    dark_theme = Theme('Dark', styles={'background': 'black', 'text': 'white'})
    manager = ThemeManager()
    manager.add_theme(light_theme)
    manager.add_theme(dark_theme)
    manager.set_theme('Light')
