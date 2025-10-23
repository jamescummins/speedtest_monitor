#!/usr/bin/env python3
"""
Script to update existing speed_history.csv file to convert empty values to 0
for failed speed tests to maintain consistency.
"""

import csv
import shutil
from pathlib import Path

def update_csv_empty_to_zero(csv_file_path):
    """
    Update CSV file to convert empty speed values to 0 for failed tests
    
    Args:
        csv_file_path (Path): Path to the CSV file to update
    """
    if not csv_file_path.exists():
        print(f"❌ CSV file not found: {csv_file_path}")
        return False
    
    # Create backup
    backup_path = csv_file_path.with_suffix('.csv.backup')
    shutil.copy2(csv_file_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Read existing data
    rows = []
    updated_count = 0
    
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        original_fieldnames = reader.fieldnames
        
        # Define expected fieldnames (new format)
        expected_fieldnames = [
            'timestamp', 'download_mbps', 'upload_mbps', 'ping_ms',
            'server_name', 'server_country', 'server_sponsor', 
            'status', 'error_type', 'error_details'
        ]
        
        for row in reader:
            original_row = dict(row)
            
            # Add missing columns if they don't exist
            for field in expected_fieldnames:
                if field not in row:
                    if field == 'status':
                        # Determine status based on data
                        if (row.get('download_mbps') in ['', None] and 
                            row.get('upload_mbps') in ['', None]):
                            row[field] = 'FAILED'
                        else:
                            row[field] = 'SUCCESS'
                    else:
                        row[field] = None
            
            # Update empty values to 0 for failed tests or missing data
            if (row.get('status') == 'FAILED' or 
                row.get('error_type') or
                (row.get('download_mbps') in ['', None] and row.get('upload_mbps') in ['', None])):
                
                # Convert empty speed values to 0
                if row.get('download_mbps') in ['', None]:
                    row['download_mbps'] = '0'
                if row.get('upload_mbps') in ['', None]:
                    row['upload_mbps'] = '0'
                if row.get('ping_ms') in ['', None]:
                    row['ping_ms'] = '0'
                
                # Ensure status is set to FAILED
                if not row.get('status'):
                    row['status'] = 'FAILED'
                
                # Check if any changes were made
                if row != original_row:
                    updated_count += 1
            
            # Ensure all fields are present
            cleaned_row = {}
            for field in expected_fieldnames:
                cleaned_row[field] = row.get(field, '')
            
            rows.append(cleaned_row)
    
    # Write updated data back with new format
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=expected_fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Updated {updated_count} rows with 0 values for failed tests")
    print(f"✅ Total rows processed: {len(rows)}")
    print(f"✅ CSV format updated to include status, error_type, and error_details columns")
    
    return True

def main():
    """Main function to update the CSV file"""
    print("🔄 Updating speed_history.csv to set failed test values to 0")
    print("")
    
    # Get paths
    project_root = Path(__file__).parent
    data_dir = project_root / "speedtest_data"
    csv_file = data_dir / "speed_history.csv"
    
    # Update local CSV
    print("📁 Updating local CSV file...")
    if update_csv_empty_to_zero(csv_file):
        print("✅ Local CSV updated successfully")
    else:
        print("❌ Failed to update local CSV")
        return
    
    # Check for SMB CSV and update if exists
    smb_csv = Path("/media/test/speedtest/speed_history.csv")
    if smb_csv.exists():
        print("\n📁 Updating SMB CSV file...")
        if update_csv_empty_to_zero(smb_csv):
            print("✅ SMB CSV updated successfully")
        else:
            print("❌ Failed to update SMB CSV")
    else:
        print("\n📁 SMB CSV file not found, skipping...")
    
    print("\n🎉 CSV update completed!")
    print("💡 Backups were created with .backup extension")

if __name__ == "__main__":
    main()