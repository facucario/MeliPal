import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# Rate limiting configuration for MercadoLibre requests
REQUEST_DELAY_MIN = int(os.getenv("REQUEST_DELAY_MIN", "3"))  # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = int(os.getenv("REQUEST_DELAY_MAX", "8"))  # Maximum delay between requests (seconds)