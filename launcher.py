import sys
import json
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Meter Lab Tools')
        self.resize(800, 600)
        # Additional UI setup can be added here

def load_config(config_file='config.json'):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        QMessageBox.critical(None, 'Error', f'Config file {config_file} not found.')
        sys.exit(1)
    except json.JSONDecodeError:
        QMessageBox.critical(None, 'Error', 'Error reading the config file.')
        sys.exit(1)

def init_database(db_name='database.db'):
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        QMessageBox.critical(None, 'Error', f'Database error: {e}')
        sys.exit(1)

def main():
    app = QApplication(sys.argv)
    config = load_config()
    db_connection = init_database(config.get('database_name', 'database.db'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()