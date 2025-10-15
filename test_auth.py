#!/usr/bin/env python3
"""
Test Google Drive Authentication
Simple script to test and fix Google Drive authentication issues
"""

import os
import sys
from pathlib import Path

# Add the main directory to path to import from speedtest_monitor
sys.path.append(str(Path(__file__).parent))

try:
    from speedtest_monitor import (
        check_google_auth_status, 
        get_google_drive_service,
        CREDENTIALS_FILE,
        TOKEN_FILE,
        DATA_DIR,
        GOOGLE_DRIVE_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing speedtest_monitor: {e}")
    print("Make sure you're running this from the speedtest_monitor directory")
    sys.exit(1)

def test_authentication():
    """Test Google Drive authentication setup"""
    print("=" * 60)
    print("GOOGLE DRIVE AUTHENTICATION TEST")
    print("=" * 60)
    
    # Check if libraries are available
    if not GOOGLE_DRIVE_AVAILABLE:
        print("❌ Google Drive libraries not installed")
        print("Run: pip install google-api-python-client google-auth google-auth-oauthlib")
        return False
    
    print("✅ Google Drive libraries available")
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"📁 Creating data directory: {DATA_DIR}")
        DATA_DIR.mkdir(exist_ok=True)
    
    # Check credentials file
    if not CREDENTIALS_FILE.exists():
        print(f"❌ Credentials file missing: {CREDENTIALS_FILE}")
        print("\nTo fix this:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 for Desktop)")
        print("5. Download as 'credentials.json'")
        print(f"6. Place in: {CREDENTIALS_FILE}")
        return False
    
    print(f"✅ Credentials file found: {CREDENTIALS_FILE}")
    
    # Check authentication status
    auth_ok, auth_msg = check_google_auth_status()
    print(f"🔐 Authentication status: {auth_msg}")
    
    if not auth_ok and "required" in auth_msg:
        print("\n🔄 Starting authentication process...")
        service = get_google_drive_service()
        if service:
            print("✅ Authentication successful!")
            
            # Test API access
            try:
                about = service.about().get(fields="user").execute()
                user = about.get('user', {})
                print(f"✅ Connected as: {user.get('displayName', 'Unknown')} ({user.get('emailAddress', 'Unknown')})")
                return True
            except Exception as e:
                print(f"❌ API test failed: {e}")
                return False
        else:
            print("❌ Authentication failed")
            return False
    
    elif auth_ok:
        print("✅ Authentication is valid")
        
        # Test API access
        try:
            service = get_google_drive_service()
            if service:
                about = service.about().get(fields="user").execute()
                user = about.get('user', {})
                print(f"✅ Connected as: {user.get('displayName', 'Unknown')} ({user.get('emailAddress', 'Unknown')})")
                return True
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    return False

def reset_authentication():
    """Reset authentication by removing token file"""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print(f"🗑️  Removed token file: {TOKEN_FILE}")
        print("Run this script again to re-authenticate")
    else:
        print("No token file to remove")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_authentication()
        return
    
    success = test_authentication()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Google Drive authentication is working!")
        print("You can now run the main speedtest_monitor.py script")
    else:
        print("❌ Authentication needs to be fixed")
        print("Follow the instructions above, then run this test again")
        print("Or use --reset flag to start over: python test_auth.py --reset")
    print("=" * 60)

if __name__ == "__main__":
    main()