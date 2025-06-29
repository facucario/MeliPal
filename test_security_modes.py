#!/usr/bin/env python3
"""
Test script to demonstrate different security modes with proxy configuration.
"""

import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_security_mode(use_proxy, proxy_fallback, mode_name):
    """Test a specific security mode configuration."""
    print(f"\n🔒 Testing {mode_name}")
    print("=" * 40)
    
    # Set environment variables for this test
    os.environ['USE_PROXY'] = str(use_proxy).lower()
    os.environ['PROXY_FALLBACK'] = str(proxy_fallback).lower()
    
    # Re-import to get fresh configuration
    import importlib
    import config
    import proxy_manager
    
    # Reload modules to pick up new config
    importlib.reload(config)
    importlib.reload(proxy_manager)
    
    # Create new proxy manager instance
    pm = proxy_manager.ProxyManager()
    
    # Test configuration
    print(f"USE_PROXY: {pm.use_proxy}")
    print(f"PROXY_FALLBACK: {pm.proxy_fallback}")
    
    # Test request
    test_url = "https://httpbin.org/ip"
    print(f"Testing request to: {test_url}")
    
    response = pm.make_request_with_proxy(test_url)
    
    if response:
        print(f"✅ Request successful!")
        print(f"Response: {response.text}")
        return True
    else:
        print(f"❌ Request failed")
        if not proxy_fallback and use_proxy:
            print("   (Expected - no proxies available and fallback disabled)")
        return False

def main():
    """Test all security modes."""
    print("🚀 Testing Different Security Modes")
    print("=" * 50)
    
    # Test 1: Strict Mode (Proxies only, no fallback)
    strict_success = test_security_mode(True, False, "Strict Mode")
    
    # Test 2: Flexible Mode (Proxies with fallback)
    flexible_success = test_security_mode(True, True, "Flexible Mode")
    
    # Test 3: Direct Mode (No proxies)
    direct_success = test_security_mode(False, False, "Direct Mode")
    
    # Summary
    print("\n" + "=" * 50)
    print("SECURITY MODES SUMMARY:")
    print(f"Strict Mode (Proxies only): {'✅ PASS' if strict_success else '❌ FAIL'}")
    print(f"Flexible Mode (Proxies + fallback): {'✅ PASS' if flexible_success else '❌ FAIL'}")
    print(f"Direct Mode (No proxies): {'✅ PASS' if direct_success else '❌ FAIL'}")
    
    print("\n📋 Security Mode Descriptions:")
    print("• Strict Mode: Maximum anonymity, fails if no proxies available")
    print("• Flexible Mode: Good balance between anonymity and reliability")
    print("• Direct Mode: No proxy overhead, exposes real IP")

if __name__ == "__main__":
    main() 