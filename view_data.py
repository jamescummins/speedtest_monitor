#!/usr/bin/env python3
"""
View Speed Test Data from SMB Share
Displays recent speed test results from both local and SMB locations
"""

import csv
import sys
from pathlib import Path
import datetime

# Configuration
LOCAL_DATA_DIR = Path(__file__).parent / "speedtest_data"
LOCAL_CSV = LOCAL_DATA_DIR / "speed_history.csv"
SMB_MOUNT_PATH = Path("/media/test")
SMB_SPEEDTEST_DIR = SMB_MOUNT_PATH / "speedtest"
SMB_CSV = SMB_SPEEDTEST_DIR / "speed_history.csv"

def format_timestamp(iso_string):
    """Format ISO timestamp for display"""
    try:
        dt = datetime.datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return iso_string

def view_csv_data(csv_file, location_name):
    """View data from a CSV file"""
    if not csv_file.exists():
        print(f"❌ {location_name} CSV not found: {csv_file}")
        return False
    
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        if not rows:
            print(f"📄 {location_name} CSV is empty")
            return True
        
        print(f"\n📊 {location_name} Data ({len(rows)} records)")
        print("=" * 80)
        
        # Count successes vs failures - check multiple possible failure indicators
        failed_rows = []
        successful_rows = []
        
        for row in rows:
            # Check for various failure indicators
            is_failed = (
                row.get('status') == 'FAILED' or
                row.get('error_type') or
                row.get('error_details') or
                (not row.get('download_mbps') or row.get('download_mbps') == '')
            )
            
            if is_failed:
                failed_rows.append(row)
            else:
                successful_rows.append(row)
        
        if failed_rows:
            print(f"⚠️  {len(failed_rows)} failures out of {len(rows)} total tests")
            print("\n❌ Recent Failures:")
            for failure in failed_rows[-5:]:  # Show last 5 failures
                timestamp = format_timestamp(failure['timestamp'])
                error_type = failure.get('error_type', 'Unknown')
                error_details = failure.get('error_details', 'No details')
                
                # Truncate long error messages but show meaningful info
                if error_details and len(error_details) > 50:
                    error_details = error_details[:47] + "..."
                
                if not error_type or error_type == 'Unknown':
                    error_type = 'NetworkError' if not failure.get('download_mbps') else 'DataError'
                
                print(f"   {timestamp} - {error_type}: {error_details}")
        
        if successful_rows:
            # Show header for successful tests
            print(f"\n✅ Successful Tests ({len(successful_rows)} records):")
            print(f"{'Time':<19} {'Down (Mbps)':<12} {'Up (Mbps)':<10} {'Ping (ms)':<10} {'Server':<25}")
            print("-" * 80)
            
            # Show last 10 successful records
            recent_successful = successful_rows[-10:]
            for row in recent_successful:
                try:
                    timestamp = format_timestamp(row['timestamp'])
                    download = f"{float(row['download_mbps']):.1f}" if row['download_mbps'] else "N/A"
                    upload = f"{float(row['upload_mbps']):.1f}" if row['upload_mbps'] else "N/A"
                    ping = f"{float(row['ping_ms']):.1f}" if row['ping_ms'] else "N/A"
                    server = f"{row['server_sponsor']} ({row['server_name']})" if row['server_sponsor'] and row['server_name'] else "N/A"
                    
                    print(f"{timestamp:<19} {download:<12} {upload:<10} {ping:<10} {server:<25}")
                except (ValueError, TypeError) as e:
                    # Skip malformed records
                    continue
            
            if len(successful_rows) > 10:
                print(f"\n... and {len(successful_rows) - 10} more successful records")
            
            # Show summary stats for successful tests only - filter out invalid values
            try:
                downloads = [float(row['download_mbps']) for row in successful_rows if row['download_mbps'] and row['download_mbps'] != '']
                uploads = [float(row['upload_mbps']) for row in successful_rows if row['upload_mbps'] and row['upload_mbps'] != '']
                pings = [float(row['ping_ms']) for row in successful_rows if row['ping_ms'] and row['ping_ms'] != '']
            except (ValueError, TypeError):
                downloads = uploads = pings = []
            
            if downloads and uploads and pings:
                print(f"\n📈 Summary Statistics (Successful Tests Only):")
                print(f"Download: Avg {sum(downloads)/len(downloads):.1f} Mbps, Min {min(downloads):.1f}, Max {max(downloads):.1f}")
                print(f"Upload:   Avg {sum(uploads)/len(uploads):.1f} Mbps, Min {min(uploads):.1f}, Max {max(uploads):.1f}")
                print(f"Ping:     Avg {sum(pings)/len(pings):.1f} ms, Min {min(pings):.1f}, Max {max(pings):.1f}")
            else:
                print(f"\n⚠️  Unable to calculate statistics - invalid data in successful records")
        else:
            print(f"\n❌ No successful tests found in {len(rows)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading {location_name} CSV: {str(e)}")
        return False

def check_smb_status():
    """Check SMB mount status"""
    print("\n🔍 SMB Mount Status:")
    print("-" * 40)
    
    if not SMB_MOUNT_PATH.exists():
        print(f"❌ SMB path does not exist: {SMB_MOUNT_PATH}")
        return False
    
    print(f"✅ SMB path exists: {SMB_MOUNT_PATH}")
    
    if SMB_MOUNT_PATH.is_mount():
        print("✅ Path is mounted")
    else:
        print("⚠️  Path exists but may not be mounted")
    
    # Check speedtest directory
    if SMB_SPEEDTEST_DIR.exists():
        print(f"✅ Speedtest directory exists: {SMB_SPEEDTEST_DIR}")
    else:
        print(f"⚠️  Speedtest directory missing: {SMB_SPEEDTEST_DIR}")
    
    try:
        # Check main mount directory
        files = list(SMB_MOUNT_PATH.iterdir())
        print(f"✅ Mount directory accessible ({len(files)} items)")
        
        # Check speedtest directory specifically
        if SMB_SPEEDTEST_DIR.exists():
            speedtest_files = list(SMB_SPEEDTEST_DIR.iterdir())
            print(f"✅ Speedtest directory accessible ({len(speedtest_files)} items)")
            
            if speedtest_files:
                print("📁 Speedtest files found:")
                for file in speedtest_files:
                    size = file.stat().st_size if file.is_file() else 0
                    print(f"   - {file.name} ({size} bytes)")
        else:
            print("📁 No speedtest directory found")
        
    except Exception as e:
        print(f"❌ Cannot access SMB directory: {str(e)}")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 Speed Test Data Viewer (SMB Version)")
    print("=" * 50)
    
    # Check SMB status
    smb_ok = check_smb_status()
    
    # View local data
    print("\n" + "=" * 50)
    local_ok = view_csv_data(LOCAL_CSV, "Local")
    
    # View SMB data if available
    if smb_ok:
        print("\n" + "=" * 50)
        smb_data_ok = view_csv_data(SMB_CSV, "SMB Share")
        
        # Compare file sizes/dates if both exist
        if LOCAL_CSV.exists() and SMB_CSV.exists():
            local_size = LOCAL_CSV.stat().st_size
            smb_size = SMB_CSV.stat().st_size
            local_mtime = LOCAL_CSV.stat().st_mtime
            smb_mtime = SMB_CSV.stat().st_mtime
            
            print(f"\n🔄 Sync Status:")
            print(f"Local:  {local_size} bytes, modified {datetime.datetime.fromtimestamp(local_mtime)}")
            print(f"SMB:    {smb_size} bytes, modified {datetime.datetime.fromtimestamp(smb_mtime)}")
            
            if abs(local_mtime - smb_mtime) < 60:  # Within 1 minute
                print("✅ Files appear to be in sync")
            else:
                print("⚠️  Files may be out of sync")
    
    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("- Local data is stored regardless of SMB status")
    print("- SMB sync happens after each speed test")
    print("- Use 'tail -f speedtest_data/speedtest.log' to monitor real-time")
    
    if not smb_ok:
        print("- Fix SMB mount to enable network backup")

if __name__ == "__main__":
    main()