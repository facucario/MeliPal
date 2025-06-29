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
- **Proxy Support**: Uses free proxy services to avoid IP detection and blocking
- **Proxy Rotation**: Automatically rotates through multiple proxies for better anonymity
- **Configurable Fallback**: Option to disable fallback to direct connection when proxies are unavailable

## Project Structure

```
mercadolibre-watcher-bot/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # Bot application entry point
│   ├── handlers.py        # Telegram command handlers
│   ├── tasks.py           # Background monitoring tasks
│   ├── scraper.py         # MercadoLibre scraping logic
│   ├── proxy_manager.py   # Proxy management and rotation
│   ├── database.py        # Database models and session
│   └── config.py          # Configuration settings
├── main.py                # Root entry point
├── requirements.txt       # Python dependencies
├── env.example            # Environment variables example
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
   # Copy the example file
   cp env.example .env
   
   # Edit the .env file with your configuration
   nano .env
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

Copy `env.example` to `.env` and configure the following variables:

- `TELEGRAM_TOKEN`: Your Telegram bot token from @BotFather (required)
- `CHECK_INTERVAL`: How often to check for new listings (in seconds, default: 300)
- `REQUEST_DELAY_MIN`: Minimum delay between requests in seconds (default: 3)
- `REQUEST_DELAY_MAX`: Maximum delay between requests in seconds (default: 8)
- `DATABASE_URL`: Database connection string (default: sqlite:///bot.db)

### Proxy Configuration

The bot includes proxy support to avoid IP detection and blocking:

- `USE_PROXY`: Enable/disable proxy usage (default: true)
- `PROXY_FALLBACK`: Enable/disable fallback to direct connection when proxies are unavailable (default: true)
- `PROXY_UPDATE_INTERVAL`: How often to refresh the proxy list in seconds (default: 300)
- `PROXY_MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
- `PROXY_TIMEOUT`: Timeout for proxy requests in seconds (default: 10)

#### Proxy Features

- **Multiple Sources**: Fetches proxies from multiple free proxy services
- **Automatic Testing**: Tests proxies before use to ensure they work
- **Rotation**: Automatically rotates through working proxies
- **Configurable Fallback**: Can be disabled to ensure only proxy connections are used
- **Configurable**: Can be completely disabled by setting `USE_PROXY=false`

#### Security Modes

**Strict Mode** (`USE_PROXY=true`, `PROXY_FALLBACK=false`):
- Only uses proxy connections
- Fails gracefully if no proxies are available
- Maximum anonymity - never exposes your real IP

**Flexible Mode** (`USE_PROXY=true`, `PROXY_FALLBACK=true`):
- Uses proxies when available
- Falls back to direct connection if proxies fail
- Good balance between anonymity and reliability

**Direct Mode** (`USE_PROXY=false`):
- Uses direct connections only
- No proxy overhead
- Exposes your real IP

### Rate Limiting

The bot includes built-in rate limiting to be respectful to MercadoLibre servers:

- **Random delays**: Between 3-8 seconds (configurable) between requests
- **Multiple request types**: Delays apply to title extraction, car details, and listing searches
- **Configurable**: Adjust `REQUEST_DELAY_MIN` and `REQUEST_DELAY_MAX` in your `.env` file

## Testing

Run the proxy integration test:

```bash
python test_proxy.py
```

This will test both proxy connectivity and MercadoLibre scraping functionality.

Check proxy status:

```bash
python proxy_status.py
```

This will show current proxy configuration and test connectivity.

Test different security modes:

```bash
python test_security_modes.py
```

This will demonstrate the three different security configurations.

## License

MIT