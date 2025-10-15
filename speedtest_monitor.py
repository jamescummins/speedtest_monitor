#!/usr/bin/env python3
"""
Raspberry Pi Internet Speed Monitor
Runs speed tests and syncs data to Google Drive
"""

import speedtest
import csv
import datetime
import json
import os
import sys
import logging
from pathlib import Path
import time

# Google Drive API imports (install with: pip install google-api-python-client google-auth)
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.http import MediaFileUpload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("Warning: Google Drive libraries not installed. Cloud sync disabled.")

# Configuration
DATA_DIR = Path(__file__).parent / "speedtest_data"
CSV_FILE = DATA_DIR / "speed_history.csv"
LOG_FILE = DATA_DIR / "speedtest.log"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"
TOKEN_FILE = DATA_DIR / "token.json"

# Google Drive settings
SCOPES = ['https://www.googleapis.com/auth/drive.file']
DRIVE_FOLDER_NAME = "RaspberryPi_SpeedTest"

def setup_logging():
    """Configure logging to file and console"""
    DATA_DIR.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_speed_test():
    """Run internet speed test and return results"""
    try:
        logging.info("Starting speed test...")
        st = speedtest.Speedtest()
        st.get_best_server()
        
        # Run tests
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000      # Convert to Mbps
        ping = st.results.ping
        
        # Get server info
        server = st.results.server
        
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'download_mbps': round(download_speed, 2),
            'upload_mbps': round(upload_speed, 2),
            'ping_ms': round(ping, 2),
            'server_name': server['name'],
            'server_country': server['country'],
            'server_sponsor': server['sponsor']
        }
        
        logging.info(f"Speed test completed: {result['download_mbps']} Mbps down, "
                    f"{result['upload_mbps']} Mbps up, {result['ping_ms']} ms ping")
        
        return result
        
    except Exception as e:
        logging.error(f"Speed test failed: {str(e)}")
        return None

def save_to_csv(data):
    """Save speed test data to CSV file"""
    try:
        file_exists = CSV_FILE.exists()
        
        with open(CSV_FILE, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'download_mbps', 'upload_mbps', 'ping_ms', 
                         'server_name', 'server_country', 'server_sponsor']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
        
        logging.info(f"Data saved to {CSV_FILE}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to save data to CSV: {str(e)}")
        return False

def get_google_drive_service():
    """Authenticate and return Google Drive service object"""
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
        
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logging.info("Refreshed Google Drive credentials")
            except Exception as e:
                logging.error(f"Failed to refresh credentials: {str(e)}")
                creds = None
        
        if not creds:
            if not CREDENTIALS_FILE.exists():
                logging.error(f"Google Drive credentials file not found: {CREDENTIALS_FILE}")
                logging.error("Please download credentials.json from Google Cloud Console")
                return None
            
            # Check if we're running in a headless environment
            is_headless = os.environ.get('DISPLAY') is None or os.environ.get('SSH_CLIENT') is not None
            
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            
            if is_headless:
                # Use console-based authentication for headless systems
                logging.info("Running in headless mode - using console authentication")
                try:
                    creds = flow.run_console()
                except Exception:
                    # Fallback to manual authentication
                    logging.info("Console auth failed, using manual authentication")
                    creds = run_manual_auth_flow(flow)
            else:
                # Use browser-based authentication for desktop systems
                try:
                    creds = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    logging.warning(f"Browser auth failed: {str(e)}, trying console auth")
                    try:
                        creds = flow.run_console()
                    except Exception:
                        logging.info("Console auth failed, using manual authentication")
                        creds = run_manual_auth_flow(flow)
        
        if creds:
            # Save credentials for future use
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            logging.info("Saved new Google Drive credentials")
        else:
            logging.error("Failed to obtain Google Drive credentials")
            return None
    
    try:
        service = build('drive', 'v3', credentials=creds)
        logging.info("Google Drive service created successfully")
        return service
    except Exception as e:
        logging.error(f"Failed to create Google Drive service: {str(e)}")
        return None

def run_manual_auth_flow(flow):
    """Manual authentication flow for headless systems"""
    try:
        # Get authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("\n" + "="*60)
        print("GOOGLE DRIVE AUTHENTICATION REQUIRED")
        print("="*60)
        print("Since this is a headless system, please complete authentication manually:")
        print(f"\n1. Open this URL in a browser on another device:")
        print(f"   {auth_url}")
        print(f"\n2. Complete the authorization process")
        print(f"3. Copy the authorization code from the final URL")
        print(f"4. Enter the code below when prompted")
        print("="*60)
        
        # Get authorization code from user
        code = input("\nEnter the authorization code: ").strip()
        
        if not code:
            logging.error("No authorization code provided")
            return None
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        
        print("Authentication successful!")
        logging.info("Manual authentication completed successfully")
        return flow.credentials
        
    except Exception as e:
        logging.error(f"Manual authentication failed: {str(e)}")
        print(f"Authentication failed: {str(e)}")
        return None

def find_or_create_drive_folder(service):
    """Find or create the speedtest folder in Google Drive"""
    try:
        # Search for existing folder
        results = service.files().list(
            q=f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
            logging.info(f"Found existing Drive folder: {DRIVE_FOLDER_NAME}")
        else:
            # Create new folder
            folder_metadata = {
                'name': DRIVE_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            logging.info(f"Created new Drive folder: {DRIVE_FOLDER_NAME}")
        
        return folder_id
        
    except Exception as e:
        logging.error(f"Failed to find/create Drive folder: {str(e)}")
        return None

def upload_to_drive(service, folder_id):
    """Upload CSV file to Google Drive"""
    try:
        if not CSV_FILE.exists():
            logging.warning("No CSV file to upload")
            return False
        
        # Check if file already exists in folder
        filename = CSV_FILE.name
        results = service.files().list(
            q=f"name='{filename}' and parents in '{folder_id}'",
            fields="files(id, name)"
        ).execute()
        
        existing_files = results.get('files', [])
        
        media = MediaFileUpload(str(CSV_FILE), mimetype='text/csv')
        
        if existing_files:
            # Update existing file
            file_id = existing_files[0]['id']
            service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            logging.info(f"Updated {filename} in Google Drive")
        else:
            # Create new file
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            logging.info(f"Uploaded {filename} to Google Drive")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to upload to Google Drive: {str(e)}")
        return False

def check_google_auth_status():
    """Check if Google Drive authentication is set up"""
    if not GOOGLE_DRIVE_AVAILABLE:
        return False, "Google Drive libraries not installed"
    
    if not CREDENTIALS_FILE.exists():
        return False, f"Credentials file missing: {CREDENTIALS_FILE}"
    
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.valid:
                return True, "Authentication valid"
            elif creds and creds.expired and creds.refresh_token:
                return True, "Authentication expired but can refresh"
        except Exception:
            pass
    
    return False, "Authentication required"

def sync_to_cloud():
    """Sync data to Google Drive"""
    if not GOOGLE_DRIVE_AVAILABLE:
        logging.info("Google Drive sync skipped - libraries not available")
        return False
    
    # Check authentication status first
    auth_ok, auth_msg = check_google_auth_status()
    if not auth_ok and "required" in auth_msg:
        logging.warning(f"Google Drive sync skipped - {auth_msg}")
        logging.info("Run the script manually first to complete authentication")
        return False
    
    try:
        service = get_google_drive_service()
        if not service:
            return False
        
        folder_id = find_or_create_drive_folder(service)
        if not folder_id:
            return False
        
        return upload_to_drive(service, folder_id)
        
    except Exception as e:
        logging.error(f"Cloud sync failed: {str(e)}")
        return False

def main():
    """Main execution function"""
    setup_logging()
    logging.info("=== Speed Test Monitor Started ===")
    
    # Run speed test
    speed_data = run_speed_test()
    if not speed_data:
        logging.error("Speed test failed, exiting")
        sys.exit(1)
    
    # Save to local CSV
    if not save_to_csv(speed_data):
        logging.error("Failed to save data locally")
        sys.exit(1)
    
    # Sync to cloud
    if sync_to_cloud():
        logging.info("Cloud sync successful")
    else:
        logging.warning("Cloud sync failed - data saved locally only")
    
    logging.info("=== Speed Test Monitor Completed ===")

if __name__ == "__main__":
    main()