"""
SMB share mounting and file synchronization for the Speedtest Monitor application
"""

import os
import shutil
import subprocess
from pathlib import Path
from config import (
    SMB_MOUNT_PATH, SMB_SPEEDTEST_DIR, SMB_BACKUP_CSV, SMB_BACKUP_LOG,
    CSV_FILE, LOG_FILE
)
from logging_config import get_logger
from csv_handler import save_failure_to_csv

logger = get_logger(__name__)


def create_smb_speedtest_dir():
    """
    Create speedtest directory in SMB share if it doesn't exist
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not SMB_SPEEDTEST_DIR.exists():
            SMB_SPEEDTEST_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created speedtest directory: {SMB_SPEEDTEST_DIR}")
        else:
            logger.debug(f"Speedtest directory already exists: {SMB_SPEEDTEST_DIR}")
        return True
    except Exception as e:
        logger.error(f"Failed to create speedtest directory: {str(e)}")
        return False


def check_smb_mount():
    """
    Check if SMB share is mounted and accessible
    
    Returns:
        tuple: (success: bool, access_type: str)
    """
    try:
        if not SMB_MOUNT_PATH.exists():
            logger.error(f"SMB mount path does not exist: {SMB_MOUNT_PATH}")
            return False, "path_not_exists"
        
        if not SMB_MOUNT_PATH.is_mount():
            logger.warning(f"Path exists but may not be mounted: {SMB_MOUNT_PATH}")
        
        # Create speedtest directory if needed
        if not create_smb_speedtest_dir():
            return False, "dir_creation_failed"
        
        # Test write access in the speedtest directory
        test_file = SMB_SPEEDTEST_DIR / ".speedtest_write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"SMB speedtest directory is accessible and writable: {SMB_SPEEDTEST_DIR}")
            return True, "direct_access"
        except PermissionError:
            logger.info("Direct write failed due to permissions, will try sudo approach")
            return True, "sudo_required"
        except Exception as e:
            logger.error(f"SMB speedtest directory access failed: {str(e)}")
            return False, f"error: {str(e)}"
            
    except Exception as e:
        logger.error(f"Failed to check SMB mount: {str(e)}")
        return False, f"check_failed: {str(e)}"


def copy_file_with_sudo(src_file, dest_file):
    """
    Copy file using sudo if needed
    
    Args:
        src_file (Path): Source file path
        dest_file (Path): Destination file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Try direct copy first
        shutil.copy2(src_file, dest_file)
        logger.info(f"Direct copy successful: {dest_file}")
        return True
    except PermissionError:
        try:
            # Use sudo to copy
            cmd = ['sudo', 'cp', str(src_file), str(dest_file)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Sudo copy successful: {dest_file}")
            
            # Try to fix permissions so we can overwrite next time
            try:
                subprocess.run(['sudo', 'chown', f'{os.getuid()}:{os.getgid()}', str(dest_file)], 
                             check=False, capture_output=True)
            except:
                pass  # Don't fail if we can't change ownership
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Sudo copy failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Sudo copy error: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Copy failed: {str(e)}")
        return False


def sync_to_smb():
    """
    Sync data files to SMB share
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if SMB is accessible
        smb_ok, access_type = check_smb_mount()
        if not smb_ok:
            logger.warning(f"SMB share not accessible ({access_type}) - skipping sync")
            return False
        
        logger.info(f"SMB access type: {access_type}")
        
        # Copy CSV file
        if CSV_FILE.exists():
            if copy_file_with_sudo(CSV_FILE, SMB_BACKUP_CSV):
                logger.info(f"Successfully synced CSV to SMB: {SMB_BACKUP_CSV}")
            else:
                logger.error("Failed to sync CSV to SMB")
                return False
        else:
            logger.warning("Local CSV file does not exist - nothing to sync")
        
        # Copy log file (optional, don't fail if this doesn't work)
        if LOG_FILE.exists():
            if copy_file_with_sudo(LOG_FILE, SMB_BACKUP_LOG):
                logger.info(f"Successfully synced log to SMB: {SMB_BACKUP_LOG}")
            else:
                logger.warning("Failed to sync log to SMB (continuing anyway)")
        
        logger.info("SMB sync completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"SMB sync failed: {str(e)}")
        return False


def get_smb_status():
    """
    Get detailed status of SMB mount
    
    Returns:
        dict: Status information about the SMB mount
    """
    status = {
        'mount_exists': SMB_MOUNT_PATH.exists(),
        'is_mounted': False,
        'is_writable': False,
        'speedtest_dir_exists': SMB_SPEEDTEST_DIR.exists() if SMB_MOUNT_PATH.exists() else False,
        'free_space': None,
        'files_count': None
    }
    
    try:
        if status['mount_exists']:
            status['is_mounted'] = SMB_MOUNT_PATH.is_mount()
            
            # Test write access in speedtest directory
            if status['speedtest_dir_exists'] or create_smb_speedtest_dir():
                status['speedtest_dir_exists'] = True
                test_file = SMB_SPEEDTEST_DIR / ".speedtest_write_test"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    status['is_writable'] = True
                except:
                    status['is_writable'] = False
            
            # Get free space
            try:
                statvfs = os.statvfs(SMB_MOUNT_PATH)
                status['free_space'] = statvfs.f_frsize * statvfs.f_bavail
            except:
                pass
            
            # Count files in speedtest directory
            try:
                if status['speedtest_dir_exists']:
                    status['files_count'] = len(list(SMB_SPEEDTEST_DIR.iterdir()))
                else:
                    status['files_count'] = 0
            except:
                status['files_count'] = 0
    
    except Exception as e:
        logger.debug(f"Error getting SMB status: {str(e)}")
    
    return status