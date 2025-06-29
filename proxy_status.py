#!/usr/bin/env python3
"""
Script to show current proxy status and configuration.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from proxy_manager import proxy_manager
from config import USE_PROXY, PROXY_UPDATE_INTERVAL, PROXY_MAX_RETRIES, PROXY_TIMEOUT, PROXY_FALLBACK

def main():
    """Show proxy status and configuration."""
    print("🔍 Proxy Status and Configuration")
    print("=" * 40)
    
    # Configuration
    print(f"Proxy Enabled: {'✅ Yes' if USE_PROXY else '❌ No'}")
    print(f"Fallback Enabled: {'✅ Yes' if PROXY_FALLBACK else '❌ No'}")
    print(f"Update Interval: {PROXY_UPDATE_INTERVAL} seconds")
    print(f"Max Retries: {PROXY_MAX_RETRIES}")
    print(f"Timeout: {PROXY_TIMEOUT} seconds")
    
    print("\n📊 Current Proxy Status:")
    print(f"Total Proxies: {len(proxy_manager.proxies)}")
    print(f"Current Index: {proxy_manager.current_proxy_index}")
    
    if proxy_manager.proxies:
        print("\n🌐 Available Proxies:")
        for i, proxy in enumerate(proxy_manager.proxies[:5]):  # Show first 5
            print(f"  {i+1}. {proxy['http']}")
        if len(proxy_manager.proxies) > 5:
            print(f"  ... and {len(proxy_manager.proxies) - 5} more")
    else:
        print("  No proxies available")
    
    # Test current proxy
    print("\n🧪 Testing Current Proxy:")
    test_url = "https://httpbin.org/ip"
    response = proxy_manager.make_request_with_proxy(test_url)
    
    if response:
        print(f"✅ Proxy test successful!")
        print(f"Response: {response.text}")
    else:
        print("❌ Proxy test failed")
        if not PROXY_FALLBACK:
            print("   Note: Fallback is disabled - this is expected if no proxies are available")

if __name__ == "__main__":
    main() 