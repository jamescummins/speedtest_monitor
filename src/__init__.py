"""
Speedtest Monitor - A modular internet speed monitoring application

This package provides a clean, modular architecture for monitoring internet speed
and syncing results to SMB shares.

Modules:
- config: Application configuration and constants
- logging_config: Logging setup and configuration
- speedtest_runner: Speed test execution logic
- csv_handler: CSV data persistence
- smb_sync: SMB share synchronization
- main: Main application orchestration
"""

from main import main
from speedtest_runner import run_speed_test
from csv_handler import save_to_csv, save_failure_to_csv, get_csv_stats
from smb_sync import sync_to_smb, get_smb_status
from logging_config import setup_logging, get_logger

__version__ = "2.0.0"
__author__ = "Speedtest Monitor"

__all__ = [
    'main',
    'run_speed_test',
    'save_to_csv',
    'save_failure_to_csv', 
    'get_csv_stats',
    'sync_to_smb',
    'get_smb_status',
    'setup_logging',
    'get_logger'
]