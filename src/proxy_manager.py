import requests
import random
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
import json

from config import USE_PROXY, PROXY_UPDATE_INTERVAL, PROXY_MAX_RETRIES, PROXY_TIMEOUT, PROXY_FALLBACK

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages free proxy services and proxy rotation for web scraping."""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.last_proxy_update = 0
        self.proxy_update_interval = PROXY_UPDATE_INTERVAL
        self.max_retries = PROXY_MAX_RETRIES
        self.use_proxy = USE_PROXY
        self.proxy_fallback = PROXY_FALLBACK
        
        if not self.use_proxy:
            logger.info("Proxy usage is disabled - using direct connections")
        elif not self.proxy_fallback:
            logger.info("Proxy fallback is disabled - will fail if no proxies are available")
        
    def get_free_proxies(self) -> List[Dict[str, str]]:
        """Fetch free proxies from multiple sources."""
        if not self.use_proxy:
            return []
            
        proxy_list = []
        
        try:
            # Source 1: FreeProxyList API
            response = requests.get('https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all', timeout=10)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        proxy_list.append({
                            'http': f'http://{ip}:{port}',
                            'https': f'http://{ip}:{port}'
                        })
            
            # Source 2: ProxyNova (fallback)
            if not proxy_list:
                response = requests.get('https://api.proxynova.com/proxy', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'proxies' in data:
                        for proxy in data['proxies'][:10]:  # Limit to 10 proxies
                            proxy_list.append({
                                'http': f"http://{proxy['ip']}:{proxy['port']}",
                                'https': f"http://{proxy['ip']}:{proxy['port']}"
                            })
            
            # Source 3: Manual fallback proxies (some known free proxies)
            if not proxy_list:
                fallback_proxies = [
                    '103.149.162.194:80',
                    '103.149.162.195:80',
                    '103.149.162.196:80',
                    '103.149.162.197:80',
                    '103.149.162.198:80'
                ]
                for proxy in fallback_proxies:
                    proxy_list.append({
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    })
                    
        except Exception as e:
            logger.warning(f"Failed to fetch proxies: {e}")
            
        logger.info(f"Fetched {len(proxy_list)} proxies")
        return proxy_list
    
    def update_proxies(self):
        """Update the proxy list if enough time has passed."""
        if not self.use_proxy:
            return
            
        current_time = time.time()
        if current_time - self.last_proxy_update > self.proxy_update_interval:
            logger.info("Updating proxy list...")
            self.proxies = self.get_free_proxies()
            self.last_proxy_update = current_time
            self.current_proxy_index = 0
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in rotation."""
        if not self.use_proxy:
            return None
            
        self.update_proxies()
        
        if not self.proxies:
            if self.proxy_fallback:
                logger.warning("No proxies available, using direct connection")
            else:
                logger.error("No proxies available and fallback is disabled")
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return proxy
    
    def test_proxy(self, proxy: Dict[str, str], test_url: str = "https://httpbin.org/ip") -> bool:
        """Test if a proxy is working."""
        if not self.use_proxy:
            return False
            
        try:
            response = requests.get(
                test_url, 
                proxies=proxy, 
                timeout=PROXY_TIMEOUT,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy test failed: {e}")
            return False
    
    def get_working_proxy(self) -> Optional[Dict[str, str]]:
        """Get a working proxy by testing multiple proxies."""
        if not self.use_proxy:
            return None
            
        self.update_proxies()
        
        if not self.proxies:
            if self.proxy_fallback:
                logger.warning("No proxies available, will use direct connection")
            else:
                logger.error("No proxies available and fallback is disabled")
            return None
        
        # Test up to 5 proxies to find a working one
        for _ in range(min(5, len(self.proxies))):
            proxy = self.get_next_proxy()
            if proxy and self.test_proxy(proxy):
                logger.info(f"Found working proxy: {proxy}")
                return proxy
        
        logger.warning("No working proxies found")
        return None
    
    def make_request_with_proxy(self, url: str, headers: Dict[str, str] = None, timeout: int = None) -> Optional[requests.Response]:
        """Make a request using a working proxy with retry logic."""
        if timeout is None:
            timeout = PROXY_TIMEOUT
            
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        
        for attempt in range(self.max_retries):
            try:
                if self.use_proxy:
                    proxy = self.get_working_proxy()
                    
                    if proxy:
                        logger.debug(f"Making request with proxy (attempt {attempt + 1})")
                        response = requests.get(
                            url, 
                            headers=headers, 
                            proxies=proxy, 
                            timeout=timeout
                        )
                        response.raise_for_status()
                        return response
                    elif self.proxy_fallback:
                        # Fallback to direct connection only if enabled
                        logger.debug(f"Making direct request (attempt {attempt + 1})")
                        response = requests.get(
                            url, 
                            headers=headers, 
                            timeout=timeout
                        )
                        response.raise_for_status()
                        return response
                    else:
                        # No proxy available and fallback is disabled
                        logger.error(f"No working proxies available and fallback is disabled for {url}")
                        return None
                else:
                    # Proxy usage is disabled, use direct connection
                    logger.debug(f"Making direct request (attempt {attempt + 1})")
                    response = requests.get(
                        url, 
                        headers=headers, 
                        timeout=timeout
                    )
                    response.raise_for_status()
                    return response
                    
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(1, 3))  # Random delay between retries
                else:
                    logger.error(f"All request attempts failed for {url}")
                    return None
        
        return None

# Global proxy manager instance
proxy_manager = ProxyManager() 