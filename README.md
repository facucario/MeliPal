# MercadoLibre Watcher Bot

A Telegram bot that monitors MercadoLibre search URLs and notifies you when new listings are published.

## Usage

1. Clone the repo:
   ```bash
   git clone https://github.com/your-user/mercadolibre-watcher-bot.git
   cd mercadolibre-watcher-bot

2.	Create a .env file:
   ```bash
   TELEGRAM_TOKEN=your_token_here
   CHECK_INTERVAL=300

3.	Run it:
   ```bash
   python bot.py
  
Commands
•	/start — Welcome message
•	/help — Usage instructions
•	/list — View tracked links
•	/remove <url> — Stop tracking a link
•	/clear_seen — Remove seen ads

License MIT