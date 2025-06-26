# test_scraper.py

from bs4 import BeautifulSoup
import requests
import sys

def get_listings(url: str) -> list[str]:
    headers = {}
    links = []
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "lxml")

    published_today = len(soup.find_all(string="Publicados hoy")) > 0

    if (published_today):
      anchors = soup.select("a.poly-component__title")
      links = [a["href"].split("#")[0] for a in anchors if a.get("href")]

    return links

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_scraper.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    links = get_listings(url)
    print(f"Total found: {len(links)}")

    for link in links:
        print(link)