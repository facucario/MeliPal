#!/usr/bin/env python3
"""
MercadoLibre Watcher Bot - Entry Point
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import start_bot
import asyncio
import nest_asyncio

if __name__ == "__main__":
    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped manually.") 