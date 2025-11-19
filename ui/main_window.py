from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeterLabTools - Main Window")
        self.setGeometry(100, 100, 1000, 700)
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main window UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("MeterLabTools")
        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        layout.addWidget(title)
        layout.addStretch()
        
        central_widget.setLayout(layout)