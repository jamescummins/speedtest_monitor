"""
Speedtest execution logic for the Speedtest Monitor application
"""

import speedtest
import datetime
import traceback
import sys
from logging_config import get_logger
from csv_handler import save_failure_to_csv

logger = get_logger(__name__)


def run_speed_test():
    """
    Run internet speed test and return results
    
    Returns:
        dict or None: Speed test results dictionary if successful, None if failed
    """
    try:
        logger.info("Starting speed test...")
        
        # Initialize speedtest client
        logger.info("Initializing Speedtest client...")
        st = speedtest.Speedtest()
        
        # Get configuration and server list
        logger.info("Retrieving speedtest configuration...")
        try:
            config = st.get_config()
            logger.info("Speedtest config retrieved successfully")
            logger.debug(f"Client config: {config.get('client', {})}")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            logger.error(f"Failed to get config: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            print(f"SPEEDTEST ERROR - Config retrieval failed ({error_type}): {error_msg}", file=sys.stderr)
            save_failure_to_csv("ConfigError", error_msg, "get_config")
            raise
        
        # Get server list and find best server
        logger.info("Getting server list and finding best server...")
        try:
            servers = st.get_servers()
            logger.info(f"Found {len(servers)} total servers")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            logger.error(f"Failed to get server list: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            print(f"SPEEDTEST ERROR - Server list retrieval failed ({error_type}): {error_msg}", file=sys.stderr)
            save_failure_to_csv("ServerListError", error_msg, "get_servers")
            raise
        
        try:
            best_server = st.get_best_server()
            logger.info(f"Best server selected: {best_server['sponsor']} in {best_server['name']}, {best_server['country']}")
            logger.info(f"Server ID: {best_server['id']}, Distance: {best_server.get('d', 'unknown')} km")
            logger.info(f"Server URL: {best_server['url']}")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            logger.error(f"Failed to select best server: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            print(f"SPEEDTEST ERROR - Best server selection failed ({error_type}): {error_msg}", file=sys.stderr)
            save_failure_to_csv("BestServerError", error_msg, "get_best_server")
            raise
        
        # Run download test
        logger.info("Starting download speed test...")
        try:
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            logger.info(f"Download test completed: {round(download_speed, 2)} Mbps")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            logger.error(f"Download test failed: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            print(f"SPEEDTEST ERROR - Download test failed ({error_type}): {error_msg}", file=sys.stderr)
            save_failure_to_csv("DownloadTestError", error_msg, "download_test")
            raise
        
        # Run upload test
        logger.info("Starting upload speed test...")
        try:
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            logger.info(f"Upload test completed: {round(upload_speed, 2)} Mbps")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            full_traceback = traceback.format_exc()
            logger.error(f"Upload test failed: {error_msg}")
            logger.error(f"Error type: {error_type}")
            logger.error(f"Full traceback: {full_traceback}")
            print(f"SPEEDTEST ERROR - Upload test failed ({error_type}): {error_msg}", file=sys.stderr)
            save_failure_to_csv("UploadTestError", error_msg, "upload_test")
            raise
        
        # Get ping and server information
        ping = st.results.ping
        logger.info(f"Ping: {round(ping, 2)} ms")
        
        server = st.results.server
        
        # Compile results
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'download_mbps': round(download_speed, 2),
            'upload_mbps': round(upload_speed, 2),
            'ping_ms': round(ping, 2),
            'server_name': server['name'],
            'server_country': server['country'],
            'server_sponsor': server['sponsor'],
            'status': 'SUCCESS',
            'error_type': None,
            'error_details': None
        }
        
        logger.info(f"Speed test completed successfully: {result['download_mbps']} Mbps down, "
                   f"{result['upload_mbps']} Mbps up, {result['ping_ms']} ms ping")
        
        return result
        
    except speedtest.ConfigRetrievalError as e:
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        logger.error(f"Speed test configuration error: {error_msg}")
        logger.error("This may indicate network connectivity issues or ISP blocking")
        logger.error(f"Full traceback: {full_traceback}")
        # Also print to stdout for cron.log capture
        print(f"SPEEDTEST ERROR - ConfigRetrievalError: {error_msg}", file=sys.stderr)
        print(f"Full traceback: {full_traceback}", file=sys.stderr)
        save_failure_to_csv("ConfigRetrievalError", error_msg, "configuration")
        return None
        
    except speedtest.NoMatchedServers as e:
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        logger.error(f"No speedtest servers available: {error_msg}")
        logger.error("This may indicate regional restrictions or server unavailability")
        logger.error(f"Full traceback: {full_traceback}")
        # Also print to stdout for cron.log capture
        print(f"SPEEDTEST ERROR - NoMatchedServers: {error_msg}", file=sys.stderr)
        print(f"Full traceback: {full_traceback}", file=sys.stderr)
        save_failure_to_csv("NoMatchedServers", error_msg, "server_selection")
        return None
        
    except speedtest.SpeedtestHTTPError as e:
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        logger.error(f"HTTP error during speed test: {error_msg}")
        logger.error("This may indicate server issues or rate limiting")
        logger.error(f"Full traceback: {full_traceback}")
        # Also print to stdout for cron.log capture
        print(f"SPEEDTEST ERROR - SpeedtestHTTPError: {error_msg}", file=sys.stderr)
        print(f"Full traceback: {full_traceback}", file=sys.stderr)
        save_failure_to_csv("SpeedtestHTTPError", error_msg, "network_communication")
        return None
        
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        full_traceback = traceback.format_exc()
        logger.error(f"Speed test failed with unexpected error: {error_msg}")
        logger.error(f"Error type: {error_type}")
        logger.error(f"Full traceback: {full_traceback}")
        # Also print to stdout for cron.log capture
        print(f"SPEEDTEST ERROR - {error_type}: {error_msg}", file=sys.stderr)
        print(f"Full traceback: {full_traceback}", file=sys.stderr)
        save_failure_to_csv(error_type, error_msg, "unexpected_error")
        return None