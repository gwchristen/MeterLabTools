import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings and Preferences')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel('Enter your preference:')
        self.layout.addWidget(self.label)

        self.preference_input = QLineEdit()
        self.layout.addWidget(self.preference_input)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_preferences)

        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_preferences(self):
        preference = self.preference_input.text()
        print(f'Saved preference: {preference}')  # Here you might want to save to a file or settings store.
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())