#!/usr/bin/env python3
"""
Test script to verify proxy integration with MercadoLibre scraper.
"""

import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from proxy_manager import proxy_manager
from scraper import get_listings, get_car_details

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_proxy_connection():
    """Test if proxy connection is working."""
    print("Testing proxy connection...")
    
    # Test with a simple URL
    test_url = "https://httpbin.org/ip"
    response = proxy_manager.make_request_with_proxy(test_url)
    
    if response:
        print(f"✅ Proxy connection successful!")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        return True
    else:
        print("❌ Proxy connection failed")
        return False

def test_mercadolibre_scraping():
    """Test MercadoLibre scraping with proxy."""
    print("\nTesting MercadoLibre scraping with proxy...")
    
    # Test URL (you can change this to any MercadoLibre search URL)
    test_url = "https://autos.mercadolibre.com.ar/volkswagen-gol/_PublishedToday_YES"
    
    try:
        # Test getting listings
        print("Testing get_listings...")
        listings = get_listings(test_url)
        print(f"✅ Found {len(listings)} listings")
        
        if listings:
            # Test getting details for the first listing
            print(f"Testing get_car_details for: {listings[0]}")
            details = get_car_details(listings[0])
            print(f"✅ Car details: {details}")
        
        return True
        
    except Exception as e:
        print(f"❌ MercadoLibre scraping failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting proxy integration test...")
    
    # Test 1: Basic proxy connection
    proxy_ok = test_proxy_connection()
    
    # Test 2: MercadoLibre scraping
    scraping_ok = test_mercadolibre_scraping()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Proxy Connection: {'✅ PASS' if proxy_ok else '❌ FAIL'}")
    print(f"MercadoLibre Scraping: {'✅ PASS' if scraping_ok else '❌ FAIL'}")
    
    if proxy_ok and scraping_ok:
        print("\n🎉 All tests passed! Proxy integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 