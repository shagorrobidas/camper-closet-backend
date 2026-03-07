import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env to detect DEBUG
# This ensures that we can toggle settings by changing DEBUG in the .env file.
if os.path.exists(BASE_DIR / '.env'):
    load_dotenv(BASE_DIR / '.env')

# Check DEBUG value (defaults to True for safety in development)
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

if DEBUG:
    from .development import *
else:
    from .production import *
