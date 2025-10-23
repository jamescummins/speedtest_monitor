"""
Configuration settings for the Speedtest Monitor application
"""

from pathlib import Path
import os

# Base project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "speedtest_data"
CSV_FILE = DATA_DIR / "speed_history.csv"
LOG_FILE = DATA_DIR / "speedtest.log"

# SMB Share settings
SMB_MOUNT_PATH = Path("/media/test")
SMB_SPEEDTEST_DIR = SMB_MOUNT_PATH / "speedtest"
SMB_BACKUP_CSV = SMB_SPEEDTEST_DIR / "speed_history.csv"
SMB_BACKUP_LOG = SMB_SPEEDTEST_DIR / "speedtest.log"

# CSV fieldnames for data consistency
CSV_FIELDNAMES = [
    'timestamp', 'download_mbps', 'upload_mbps', 'ping_ms',
    'server_name', 'server_country', 'server_sponsor', 
    'status', 'error_type', 'error_details'
]

# Logging configuration
DEBUG_MODE = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

# Error details truncation length
MAX_ERROR_DETAILS_LENGTH = 500

# Standard exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_INTERRUPT = 130  # Standard exit code for SIGINT (Ctrl+C)