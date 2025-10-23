"""
Main application logic for the Speedtest Monitor application
"""

import sys
from config import EXIT_SUCCESS, EXIT_FAILURE, EXIT_INTERRUPT
from logging_config import setup_logging, get_logger
from speedtest_runner import run_speed_test
from csv_handler import save_to_csv, save_failure_to_csv
from smb_sync import sync_to_smb, get_smb_status

# Initialize logger (will be configured after setup_logging is called)
logger = None


def main():
    """
    Main execution function that orchestrates the speedtest monitoring process
    
    Returns:
        int: Exit code (EXIT_SUCCESS, EXIT_FAILURE, or EXIT_INTERRUPT)
    """
    global logger
    
    try:
        # Setup logging system
        logger = setup_logging()
        logger.info("=== Speed Test Monitor Started (SMB Version) ===")
        
        # Log SMB status for diagnostics
        try:
            smb_status = get_smb_status()
            logger.info(f"SMB Status: {smb_status}")
        except Exception as e:
            logger.warning(f"Failed to get SMB status: {str(e)}")
        
        # Run the speed test
        logger.info("Executing speed test...")
        speed_data = run_speed_test()
        
        if not speed_data:
            logger.error("Speed test failed - check previous error messages for details")
            save_failure_to_csv("SpeedTestFailed", "Complete speedtest execution failed", "main_execution")
            return EXIT_FAILURE
        
        # Save results to local CSV
        logger.info("Saving results to local CSV...")
        try:
            if not save_to_csv(speed_data):
                logger.error("Failed to save data locally")
                save_failure_to_csv("CSVSaveError", "Failed to save results to local CSV file", "local_save")
                return EXIT_FAILURE
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Exception during CSV save: {error_msg}")
            save_failure_to_csv("CSVSaveException", error_msg, "local_save")
            return EXIT_FAILURE
        
        # Sync to SMB share
        logger.info("Syncing to SMB share...")
        try:
            if sync_to_smb():
                logger.info("SMB sync successful")
            else:
                logger.warning("SMB sync failed - data saved locally only")
                save_failure_to_csv("SMBSyncFailed", "SMB synchronization failed", "smb_sync")
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"SMB sync exception: {error_msg}")
            save_failure_to_csv("SMBSyncException", error_msg, "smb_sync")
        
        logger.info("=== Speed Test Monitor Completed Successfully ===")
        return EXIT_SUCCESS
        
    except KeyboardInterrupt:
        if logger:
            logger.info("Speed test monitor interrupted by user")
            print("SPEEDTEST INFO - Speed test monitor interrupted by user (Ctrl+C)", file=sys.stderr)
            save_failure_to_csv("UserInterrupt", "Process interrupted by user (Ctrl+C)", "main_execution")
        else:
            print("SPEEDTEST INFO - Speed test monitor interrupted by user (Ctrl+C)", file=sys.stderr)
        return EXIT_INTERRUPT
        
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        if logger:
            import traceback
            full_traceback = traceback.format_exc()
            logger.error(f"Unexpected error in main execution: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            # Also print to stderr for cron.log capture
            print(f"SPEEDTEST MAIN ERROR - {error_type}: {error_msg}", file=sys.stderr)
            print(f"Full traceback: {full_traceback}", file=sys.stderr)
            save_failure_to_csv("MainExecutionError", error_msg, "main_execution")
        else:
            # Fallback logging if logger not initialized
            import traceback
            full_traceback = traceback.format_exc()
            print(f"CRITICAL ERROR: {error_type}: {error_msg}", file=sys.stderr)
            print(f"Full traceback: {full_traceback}", file=sys.stderr)
            
        return EXIT_FAILURE


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)