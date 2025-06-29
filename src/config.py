import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# Rate limiting configuration for MercadoLibre requests
REQUEST_DELAY_MIN = int(os.getenv("REQUEST_DELAY_MIN", "3"))  # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = int(os.getenv("REQUEST_DELAY_MAX", "8"))  # Maximum delay between requests (seconds)

# Proxy configuration
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"  # Enable/disable proxy usage
PROXY_UPDATE_INTERVAL = int(os.getenv("PROXY_UPDATE_INTERVAL", "300"))  # Proxy list update interval (seconds)
PROXY_MAX_RETRIES = int(os.getenv("PROXY_MAX_RETRIES", "3"))  # Maximum retries for proxy requests
PROXY_TIMEOUT = int(os.getenv("PROXY_TIMEOUT", "10"))  # Proxy request timeout (seconds)
PROXY_FALLBACK = os.getenv("PROXY_FALLBACK", "true").lower() == "true"  # Enable/disable fallback to direct connection