import asyncio
import logging

from database import SessionLocal, SeenAd, Watchlist
from scraper import get_listings

logger = logging.getLogger(__name__)

async def check_for_new_ads(app, check_interval: int):
    while True:
        session = SessionLocal()
        watchlist = session.query(Watchlist).all()
        for entry in watchlist:
            try:
                ads = get_listings(entry.url)
                for ad in ads:
                    exists = session.query(SeenAd).filter_by(url=entry.url, ad_link=ad).first()
                    if not exists:
                        session.add(SeenAd(url=entry.url, ad_link=ad))
                        await app.bot.send_message(chat_id=int(entry.chat_id), text=f"🚗 Nuevo aviso:\n{ad}")
                    else:
                        logger.debug(f"Ad already seen: {ad}")
                session.commit()
            except Exception as e:
                logger.error(f"[ERROR] URL: {entry.url} — {e}")
        session.close()
        await asyncio.sleep(check_interval)