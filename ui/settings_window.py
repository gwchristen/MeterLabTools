from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QSpinBox

class SettingsWindow(QDialog):
    """Settings and preferences dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(400, 300, 400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout()
        
        # Theme selection
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        
        # Font size
        font_label = QLabel("Font Size:")
        self.font_spinbox = QSpinBox()
        self.font_spinbox.setMinimum(8)
        self.font_spinbox.setMaximum(20)
        self.font_spinbox.setValue(10)
        
        # Apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.accept)
        
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)
        layout.addWidget(font_label)
        layout.addWidget(self.font_spinbox)
        layout.addStretch()
        layout.addWidget(apply_button)
        
        self.setLayout(layout)