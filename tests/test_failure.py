#!/usr/bin/env python3
"""
Test script to simulate speedtest failures for testing failure logging
"""

import speedtest
import sys
import os

# Add the current directory to the path to import from speedtest_monitor
sys.path.append(os.path.dirname(__file__))
from speedtest_monitor import setup_logging, save_failure_to_csv

def test_network_failure():
    """Simulate a network connectivity failure"""
    setup_logging()
    print("🧪 Testing network failure simulation...")
    
    try:
        # Try to connect to a non-existent speedtest server to trigger an error
        st = speedtest.Speedtest()
        st.get_servers(['999999'])  # Non-existent server ID
    except Exception as e:
        print(f"✅ Successfully caught error: {type(e).__name__}: {str(e)}")
        save_failure_to_csv("NetworkTestError", str(e), "test_simulation")
        return True
    
    print("❌ No error was triggered")
    return False

def test_manual_failure():
    """Manually log a test failure"""
    setup_logging()
    print("🧪 Testing manual failure logging...")
    
    save_failure_to_csv("TestFailure", "This is a simulated failure for testing", "manual_test")
    print("✅ Manual failure logged successfully")
    return True

if __name__ == "__main__":
    print("🔬 Speedtest Failure Testing")
    print("=" * 40)
    
    # Test manual failure logging
    test_manual_failure()
    
    print("\nTesting complete. Check view_data.py to see the failure logged.")