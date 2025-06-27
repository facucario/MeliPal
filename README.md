# MercadoLibre Watcher Bot

A Telegram bot that monitors MercadoLibre search URLs and notifies you when new listings are published.

## Features

- **Multiple URL Support**: Add multiple MercadoLibre URLs in a single message (one per line)
- **URL Normalization**: Automatically converts `listado.mercadolibre.com.ar` URLs to `autos.mercadolibre.com.ar` for consistent processing
- **Title Caching**: Stores article titles in the database for faster `/list` command responses
- **Published Today Filter**: Automatically adds `_PublishedToday_YES` filter to URLs to only show recent listings
- **Enhanced Notifications**: Shows title, price, year, kilometers, and location for each new listing
- **Real-time Monitoring**: Checks for new listings at configurable intervals
- **Rate Limiting**: Built-in delays between requests to be respectful to MercadoLibre servers

## Project Structure

```
mercadolibre-watcher-bot/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # Bot application entry point
│   ├── handlers.py        # Telegram command handlers
│   ├── tasks.py           # Background monitoring tasks
│   ├── scraper.py         # MercadoLibre scraping logic
│   ├── database.py        # Database models and session
│   └── config.py          # Configuration settings
├── main.py                # Root entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── fly.toml              # Fly.io deployment config
├── test_*.py             # Test files
└── README.md             # This file
```

## Usage

1. Clone the repo:
   ```bash
   git clone https://github.com/your-user/mercadolibre-watcher-bot.git
   cd mercadolibre-watcher-bot

2. Create a .env file:
   ```bash
   TELEGRAM_TOKEN=your_token_here
   CHECK_INTERVAL=300
   REQUEST_DELAY_MIN=3
   REQUEST_DELAY_MAX=8
   ```

3. Run it:
   ```bash
   python main.py

## Commands

- `/start` — Welcome message
- `/help` — Usage instructions
- `/list` — View tracked links with cached titles
- `/remove <url>` — Stop tracking a link
- `/clear_seen` — Remove seen ads
- `/stop` — Pause monitoring (no more notifications)
- `/resume` — Resume monitoring (start receiving notifications again)

## Configuration

### Environment Variables

- `TELEGRAM_TOKEN`: Your Telegram bot token from @BotFather (required)
- `CHECK_INTERVAL`: How often to check for new listings (in seconds, default: 300)
- `REQUEST_DELAY_MIN`: Minimum delay between requests in seconds (default: 3)
- `REQUEST_DELAY_MAX`: Maximum delay between requests in seconds (default: 8)
- `DATABASE_URL`: Database connection string (default: sqlite:///bot.db)

### Rate Limiting

The bot includes built-in rate limiting to be respectful to MercadoLibre servers:

- **Random delays**: Between 3-8 seconds (configurable) between requests
- **Multiple request types**: Delays apply to title extraction, car details, and listing searches
- **Configurable**: Adjust `REQUEST_DELAY_MIN` and `REQUEST_DELAY_MAX` in your `.env` file

## License

MIT