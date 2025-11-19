# Application Constants

from datetime import datetime

# Current Date and Time (UTC)
CURRENT_DATE_TIME = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# Application Settings
APP_NAME = "MeterLabTools"
APP_VERSION = "1.0.0"
APP_AUTHOR = "gwchristen"

# Database
DEFAULT_DB_PATH = "meter_lab_tools.db"

# UI Settings
DEFAULT_THEME = "Light"
DEFAULT_FONT_SIZE = 10
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# Module Settings
MODULES_CONFIG_FILE = "config.json"
RECENT_MODULES_LIMIT = 5