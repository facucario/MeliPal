import re
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

MELI_REGEX = re.compile(r"^https?://(autos\.)?mercadolibre\.com\.ar/.*(_PublishedToday_YES)?")

def get_listings(url: str) -> list[str]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return []

    soup = BeautifulSoup(res.text, "lxml")
    published_today = len(soup.find_all(string="Publicados hoy")) > 0
    if published_today:
        anchors = soup.select("a.poly-component__title")
        return [a["href"].split("#")[0] for a in anchors if a.get("href")]
    return []

def ensure_published_today_filter(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    if "_PublishedToday_YES" in path:
        return url
    match = re.search(r"(_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)$", path)
    if match:
        idx = match.start()
        new_path = path[:idx] + "_PublishedToday_YES" + path[idx:]
    else:
        new_path = path + "_PublishedToday_YES"
    return urlunparse((parsed.scheme, parsed.netloc, new_path, parsed.params, parsed.query, parsed.fragment))

def get_title_from_url(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "es-AR,es;q=0.9",
        }
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "lxml")

        title_tag = soup.find("title")
        if not title_tag:
            return url

        title = title_tag.text.strip().replace(" | MercadoLibre", "")
        return title if title else url
    except Exception as e:
        logger.warning(f"Failed to fetch title for {url}: {e}")
        return url