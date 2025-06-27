# test_scraper.py

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import get_listings

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_scraper.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    links = get_listings(url)
    print(f"Total found: {len(links)}")

    for link in links:
        print(link)