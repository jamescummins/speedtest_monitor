#!/usr/bin/env python3
"""
SMB Share Test for Speed Monitor
Tests SMB mount access and file operations
"""

import os
import sys
import logging
from pathlib import Path
import datetime
import csv

# Configuration
SMB_MOUNT_PATH = Path("/media/test")
SMB_SPEEDTEST_DIR = SMB_MOUNT_PATH / "speedtest"
TEST_CSV = SMB_SPEEDTEST_DIR / "speedtest_test.csv"

def setup_logging():
    """Configure logging"""
    debug_mode = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def test_smb_mount():
    """Test SMB mount functionality"""
    logging.info("=== Testing SMB Mount ===")
    
    # Test 1: Path exists
    logging.info(f"Testing path exists: {SMB_MOUNT_PATH}")
    if not SMB_MOUNT_PATH.exists():
        logging.error(f"SMB path does not exist: {SMB_MOUNT_PATH}")
        return False
    logging.info("✓ SMB path exists")
    
    # Test 2: Is it mounted?
    logging.info("Testing if path is mounted...")
    is_mounted = SMB_MOUNT_PATH.is_mount()
    if is_mounted:
        logging.info("✓ Path is a mount point")
    else:
        logging.warning("⚠ Path exists but may not be mounted")
    
    # Test 3: Create speedtest directory
    logging.info("Creating/checking speedtest directory...")
    try:
        SMB_SPEEDTEST_DIR.mkdir(exist_ok=True)
        logging.info(f"✓ Speedtest directory ready: {SMB_SPEEDTEST_DIR}")
    except Exception as e:
        logging.error(f"✗ Failed to create speedtest directory: {str(e)}")
        return False
    
    # Test 4: Directory listing
    logging.info("Testing directory listing...")
    try:
        files = list(SMB_MOUNT_PATH.iterdir())
        logging.info(f"✓ Found {len(files)} items in mount directory")
        
        speedtest_files = list(SMB_SPEEDTEST_DIR.iterdir()) if SMB_SPEEDTEST_DIR.exists() else []
        logging.info(f"✓ Found {len(speedtest_files)} items in speedtest directory")
        
        for file in files[:3]:  # Show first 3 items
            logging.info(f"  - {file.name}")
        if len(files) > 3:
            logging.info(f"  ... and {len(files) - 3} more")
    except Exception as e:
        logging.error(f"✗ Failed to list directory: {str(e)}")
        return False
    
    # Test 5: Write access in speedtest directory
    logging.info("Testing write access in speedtest directory...")
    test_file = SMB_SPEEDTEST_DIR / ".speedtest_write_test"
    try:
        test_content = f"Speedtest write test - {datetime.datetime.now().isoformat()}"
        test_file.write_text(test_content)
        logging.info("✓ Write test successful in speedtest directory")
        
        # Test read back
        read_content = test_file.read_text()
        if read_content == test_content:
            logging.info("✓ Read test successful")
        else:
            logging.warning("⚠ Read content doesn't match written content")
        
        # Clean up
        test_file.unlink()
        logging.info("✓ File cleanup successful")
        
    except Exception as e:
        logging.error(f"✗ Write test failed: {str(e)}")
        return False
    
    # Test 6: Free space
    logging.info("Testing disk space...")
    try:
        statvfs = os.statvfs(SMB_MOUNT_PATH)
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        free_gb = free_bytes / (1024**3)
        logging.info(f"✓ Free space: {free_gb:.2f} GB")
    except Exception as e:
        logging.warning(f"⚠ Could not get disk space: {str(e)}")
        test_file.unlink()
        logging.info("✓ File cleanup successful")
        
    except Exception as e:
        logging.error(f"✗ Write test failed: {str(e)}")
        return False
    
    # Test 5: Free space
    logging.info("Testing disk space...")
    try:
        statvfs = os.statvfs(SMB_MOUNT_PATH)
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        free_gb = free_bytes / (1024**3)
        logging.info(f"✓ Free space: {free_gb:.2f} GB")
    except Exception as e:
        logging.warning(f"⚠ Could not get disk space: {str(e)}")
    
    return True

def test_csv_operations():
    """Test CSV file operations on SMB share"""
    logging.info("=== Testing CSV Operations ===")
    
    # Create test CSV data
    test_data = [
        {
            'timestamp': datetime.datetime.now().isoformat(),
            'download_mbps': 50.25,
            'upload_mbps': 10.75,
            'ping_ms': 15.3,
            'server_name': 'Test Server',
            'server_country': 'Test Country',
            'server_sponsor': 'Test ISP'
        },
        {
            'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
            'download_mbps': 48.90,
            'upload_mbps': 11.20,
            'ping_ms': 16.1,
            'server_name': 'Test Server',
            'server_country': 'Test Country',
            'server_sponsor': 'Test ISP'
        }
    ]
    
    # Test CSV writing
    logging.info(f"Testing CSV write to: {TEST_CSV}")
    try:
        with open(TEST_CSV, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'download_mbps', 'upload_mbps', 'ping_ms', 
                         'server_name', 'server_country', 'server_sponsor']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_data)
        
        logging.info("✓ CSV write successful")
        
        # Test CSV reading
        logging.info("Testing CSV read...")
        with open(TEST_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            logging.info(f"✓ CSV read successful - {len(rows)} rows")
            for i, row in enumerate(rows):
                logging.info(f"  Row {i+1}: {row['download_mbps']} Mbps down, {row['upload_mbps']} Mbps up")
        
        # Test append operation
        logging.info("Testing CSV append...")
        new_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'download_mbps': 55.0,
            'upload_mbps': 12.0,
            'ping_ms': 14.5,
            'server_name': 'Append Test Server',
            'server_country': 'Test Country',
            'server_sponsor': 'Test ISP'
        }
        
        with open(TEST_CSV, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'download_mbps', 'upload_mbps', 'ping_ms', 
                         'server_name', 'server_country', 'server_sponsor']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(new_data)
        
        logging.info("✓ CSV append successful")
        
        # Verify append worked
        with open(TEST_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            logging.info(f"✓ CSV verification successful - now {len(rows)} rows")
        
        return True
        
    except Exception as e:
        logging.error(f"✗ CSV operations failed: {str(e)}")
        return False

def test_file_sync():
    """Test file synchronization operations"""
    logging.info("=== Testing File Sync ===")
    
    # Create a local test file
    local_test_file = Path("./test_sync_file.txt")
    smb_test_file = SMB_MOUNT_PATH / "test_sync_file.txt"
    
    try:
        # Create local file
        local_content = f"Sync test content - {datetime.datetime.now().isoformat()}"
        local_test_file.write_text(local_content)
        logging.info("✓ Created local test file")
        
        # Copy to SMB
        import shutil
        shutil.copy2(local_test_file, smb_test_file)
        logging.info("✓ Copied file to SMB share")
        
        # Verify copy
        smb_content = smb_test_file.read_text()
        if smb_content == local_content:
            logging.info("✓ File content verified on SMB share")
        else:
            logging.error("✗ File content mismatch")
            return False
        
        # Test modification time preservation
        local_mtime = local_test_file.stat().st_mtime
        smb_mtime = smb_test_file.stat().st_mtime
        if abs(local_mtime - smb_mtime) < 2:  # Allow 2 second difference
            logging.info("✓ Modification time preserved")
        else:
            logging.warning("⚠ Modification time not preserved")
        
        return True
        
    except Exception as e:
        logging.error(f"✗ File sync test failed: {str(e)}")
        return False
    
    finally:
        # Cleanup
        try:
            if local_test_file.exists():
                local_test_file.unlink()
            if smb_test_file.exists():
                smb_test_file.unlink()
            logging.info("✓ Test files cleaned up")
        except Exception as e:
            logging.warning(f"⚠ Cleanup failed: {str(e)}")

def cleanup_test_files():
    """Clean up any test files"""
    logging.info("=== Cleaning Up Test Files ===")
    
    test_files = [
        TEST_CSV,
        SMB_MOUNT_PATH / "test_sync_file.txt",
        SMB_MOUNT_PATH / ".speedtest_write_test",
        Path("./test_sync_file.txt")
    ]
    
    for test_file in test_files:
        try:
            if test_file.exists():
                test_file.unlink()
                logging.info(f"✓ Removed {test_file}")
        except Exception as e:
            logging.warning(f"⚠ Could not remove {test_file}: {str(e)}")

def main():
    """Main test function"""
    setup_logging()
    logging.info("=== SMB Share Test Started ===")
    
    all_tests_passed = True
    
    # Run tests
    if not test_smb_mount():
        all_tests_passed = False
    
    if not test_csv_operations():
        all_tests_passed = False
    
    if not test_file_sync():
        all_tests_passed = False
    
    # Cleanup
    cleanup_test_files()
    
    # Results
    if all_tests_passed:
        logging.info("=== All SMB Tests Passed! ===")
        logging.info("Your SMB share is ready for speedtest monitoring")
        logging.info(f"Data will be synced to: {SMB_MOUNT_PATH}")
    else:
        logging.error("=== Some SMB Tests Failed ===")
        logging.error("Please check your SMB mount configuration")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)