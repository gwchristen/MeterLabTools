from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class LoginWindow(QDialog):
    """Login/Authentication dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setGeometry(400, 300, 300, 200)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        layout = QVBoxLayout()
        
        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.accept)
        
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        
        self.setLayout(layout)