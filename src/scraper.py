import re
import time
import random
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import logging

from config import REQUEST_DELAY_MIN, REQUEST_DELAY_MAX
from proxy_manager import proxy_manager

logger = logging.getLogger(__name__)

MELI_REGEX = re.compile(r"^https?://(listado|autos)\.mercadolibre\.com\.ar/.*")

def transform_listado_to_autos(url: str) -> str:
    """Transform listado.mercadolibre.com.ar URLs to autos.mercadolibre.com.ar"""
    return url.replace("listado.mercadolibre.com.ar", "autos.mercadolibre.com.ar")

def _add_request_delay():
    """Add a random delay between requests to be respectful to MercadoLibre servers."""
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    logger.debug(f"Adding delay of {delay:.2f} seconds between requests")
    time.sleep(delay)

def get_listings(url: str) -> list[str]:
    # Transform listado URLs to autos URLs
    url = transform_listado_to_autos(url)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Use proxy manager for the request
        res = proxy_manager.make_request_with_proxy(url, headers=headers, timeout=15)
        if res is None:
            logger.error(f"Failed to fetch URL {url} with proxy")
            return []
    except Exception as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return []

    soup = BeautifulSoup(res.text, "lxml")
    published_today = len(soup.find_all(string="Publicados hoy")) > 0
    if published_today:
        anchors = soup.select("a.poly-component__title")
        return [a["href"].split("#")[0] for a in anchors if a.get("href")]
    return []

def ensure_published_today_filter(url: str) -> str:
    # Transform listado URLs to autos URLs first
    url = transform_listado_to_autos(url)
    
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
    # Transform listado URLs to autos URLs
    url = transform_listado_to_autos(url)
    
    # Add delay before making request
    _add_request_delay()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Use proxy manager for the request
        res = proxy_manager.make_request_with_proxy(url, headers=headers, timeout=10)
        if res is None:
            logger.warning(f"Failed to fetch title for {url} with proxy")
            return url
            
        soup = BeautifulSoup(res.text, "lxml")

        title_tag = soup.find("title")
        if not title_tag:
            return url

        title = title_tag.text.strip().replace(" | MercadoLibre", "")
        return title if title else url
    except Exception as e:
        logger.warning(f"Failed to fetch title for {url}: {e}")
        return url

def get_car_details(url: str) -> dict:
    """Extract detailed car information from a MercadoLibre car listing page."""
    # Transform listado URLs to autos URLs
    url = transform_listado_to_autos(url)
    
    # Add delay before making request
    _add_request_delay()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Use proxy manager for the request
        res = proxy_manager.make_request_with_proxy(url, headers=headers, timeout=15)
        if res is None:
            logger.error(f"Failed to fetch car details from {url} with proxy")
            return {"title": "Error al cargar", "price": "N/A", "year": "N/A", "kilometers": "N/A", "location": "N/A", "url": url}
    except Exception as e:
        logger.error(f"Failed to fetch car details from {url}: {e}")
        return {"title": "Error al cargar", "price": "N/A", "year": "N/A", "kilometers": "N/A", "location": "N/A", "url": url}

    soup = BeautifulSoup(res.text, "lxml")
    
    # Extract title
    title = "Sin título"
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.text.strip().replace(" | MercadoLibre", "")
    
    # Extract price
    price = "Precio no disponible"
    price_elements = soup.select(".andes-money-amount__fraction")
    if price_elements:
        price = price_elements[0].text.strip()
        # Check for currency symbol
        currency_elements = soup.select(".andes-money-amount__currency-symbol")
        if currency_elements:
            currency = currency_elements[0].text.strip()
            price = f"{currency} {price}"
    
    # Extract year and kilometers from "Publicado hace" string
    year = "Año no disponible"
    kilometers = "KM no disponible"
    
    page_text = soup.get_text()
    
    # Look for the "Publicado hace" pattern
    publicado_pattern = r"(\d{4})\s*\|\s*([\d.,]+)\s*km\s*·\s*Publicado"
    match = re.search(publicado_pattern, page_text)
    if match:
        year = match.group(1)
        kilometers = match.group(2)
    
    # Extract location from JSON data
    location = "Ubicación no disponible"
    
    # Look for location in JSON format from the actual page content
    json_location_pattern = r'"city":"([^"]+)","neighborhood":"([^"]+)","state":"([^"]+)"'
    match = re.search(json_location_pattern, page_text)
    if match:
        city = match.group(1)
        state = match.group(3)
        location = f"{city}, {state}"
    
    return {
        "title": title,
        "price": price,
        "year": year,
        "kilometers": kilometers,
        "location": location,
        "url": url
    }