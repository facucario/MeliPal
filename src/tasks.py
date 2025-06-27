import asyncio
import logging
import time
import random

from database import SessionLocal, SeenAd, Watchlist, BotState
from scraper import get_listings, get_car_details
from config import REQUEST_DELAY_MIN, REQUEST_DELAY_MAX

logger = logging.getLogger(__name__)

def format_car_message(car_details: dict) -> str:
    """Format car details into a readable message."""
    title = car_details.get("title", "Sin título")
    price = car_details.get("price", "Precio no disponible")
    year = car_details.get("year", "Año no disponible")
    kilometers = car_details.get("kilometers", "KM no disponible")
    location = car_details.get("location", "Ubicación no disponible")
    url = car_details.get("url", "")
    
    message = f"🚗 {title}\n"
    message += f"💰 {price}\n"
    message += f"📅 {year} | {kilometers}km\n"
    message += f"📍 {location}\n"
    message += f"🔗 {url}"
    
    return message

async def check_for_new_ads(app, check_interval: int):
    while True:
        session = SessionLocal()
        watchlist = session.query(Watchlist).all()
        
        for entry in watchlist:
            try:
                # Check if bot is running for this user
                bot_state = session.query(BotState).filter_by(chat_id=entry.chat_id).first()
                if bot_state and not bot_state.is_running:
                    logger.debug(f"Bot is stopped for user {entry.chat_id}, skipping notifications")
                    continue
                
                ads = get_listings(entry.url)
                for ad in ads:
                    exists = session.query(SeenAd).filter_by(chat_id=entry.chat_id, url=entry.url, ad_link=ad).first()
                    if not exists:
                        session.add(SeenAd(chat_id=entry.chat_id, url=entry.url, ad_link=ad))
                        
                        # Get detailed car information
                        car_details = get_car_details(ad)
                        message = format_car_message(car_details)
                        
                        await app.bot.send_message(chat_id=int(entry.chat_id), text=message)
                        
                        # Add a delay between processing ads to be respectful
                        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
                        logger.debug(f"Adding delay of {delay:.2f} seconds between ads")
                        await asyncio.sleep(delay)
                    else:
                        logger.debug(f"Ad already seen: {ad}")
                session.commit()
            except Exception as e:
                logger.error(f"[ERROR] URL: {entry.url} — {e}")
        session.close()
        await asyncio.sleep(check_interval)