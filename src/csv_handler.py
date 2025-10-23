"""
CSV data handling for the Speedtest Monitor application
"""

import csv
import datetime
from config import CSV_FILE, CSV_FIELDNAMES, MAX_ERROR_DETAILS_LENGTH
from logging_config import get_logger

logger = get_logger(__name__)


def save_to_csv(data):
    """
    Save speed test data to CSV file
    
    Args:
        data (dict): Speed test data dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        file_exists = CSV_FILE.exists()
        
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
        
        logger.info(f"Data saved to {CSV_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save data to CSV: {str(e)}")
        return False


def save_failure_to_csv(error_type, error_details, stage="unknown"):
    """
    Save speed test failure information to CSV
    
    Args:
        error_type (str): Type of error that occurred
        error_details (str): Detailed error message
        stage (str): Stage where error occurred (default: "unknown")
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        failure_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'download_mbps': 0,  # Set to 0 instead of None for failed tests
            'upload_mbps': 0,    # Set to 0 instead of None for failed tests
            'ping_ms': 0,        # Set to 0 instead of None for failed tests
            'server_name': None,
            'server_country': None,
            'server_sponsor': None,
            'status': 'FAILED',
            'error_type': error_type,
            'error_details': f"{stage}: {error_details}"[:MAX_ERROR_DETAILS_LENGTH]
        }
        
        save_to_csv(failure_data)
        logger.info(f"Failure logged to CSV: {error_type} during {stage}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log failure to CSV: {str(e)}")
        return False


def get_csv_stats():
    """
    Get basic statistics about the CSV file
    
    Returns:
        dict: Statistics including file size, record count, etc.
    """
    stats = {
        'file_exists': False,
        'file_size': 0,
        'record_count': 0,
        'success_count': 0,
        'failure_count': 0
    }
    
    try:
        if CSV_FILE.exists():
            stats['file_exists'] = True
            stats['file_size'] = CSV_FILE.stat().st_size
            
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stats['record_count'] += 1
                    if row.get('status') == 'SUCCESS':
                        stats['success_count'] += 1
                    else:
                        stats['failure_count'] += 1
                        
    except Exception as e:
        logger.error(f"Failed to get CSV stats: {str(e)}")
    
    return stats