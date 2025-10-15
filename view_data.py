#!/usr/bin/env python3
"""
Simple data viewer for speed test results
Run this to view your speed test history locally
"""

import csv
import sys
from pathlib import Path
import datetime

def load_speed_data(csv_file):
    """Load speed test data from CSV"""
    data = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"No data file found: {csv_file}")
        return []
    except Exception as e:
        print(f"Error reading data: {e}")
        return []

def print_summary(data):
    """Print summary statistics"""
    if not data:
        print("No data available")
        return
    
    downloads = [float(row['download_mbps']) for row in data]
    uploads = [float(row['upload_mbps']) for row in data]
    pings = [float(row['ping_ms']) for row in data]
    
    print(f"\n📊 Speed Test Summary ({len(data)} tests)")
    print("=" * 50)
    print(f"Download Speed:")
    print(f"  Average: {sum(downloads)/len(downloads):.1f} Mbps")
    print(f"  Min:     {min(downloads):.1f} Mbps")
    print(f"  Max:     {max(downloads):.1f} Mbps")
    
    print(f"\nUpload Speed:")
    print(f"  Average: {sum(uploads)/len(uploads):.1f} Mbps") 
    print(f"  Min:     {min(uploads):.1f} Mbps")
    print(f"  Max:     {max(uploads):.1f} Mbps")
    
    print(f"\nPing:")
    print(f"  Average: {sum(pings)/len(pings):.1f} ms")
    print(f"  Min:     {min(pings):.1f} ms")
    print(f"  Max:     {max(pings):.1f} ms")

def print_recent(data, count=10):
    """Print recent test results"""
    if not data:
        return
    
    print(f"\n📈 Last {min(count, len(data))} Speed Tests")
    print("=" * 80)
    print(f"{'Date/Time':<20} {'Download':<12} {'Upload':<10} {'Ping':<8} {'Server'}")
    print("-" * 80)
    
    for row in data[-count:]:
        timestamp = datetime.datetime.fromisoformat(row['timestamp'])
        date_str = timestamp.strftime('%m/%d %H:%M')
        
        print(f"{date_str:<20} "
              f"{row['download_mbps']:>8}Mbps "
              f"{row['upload_mbps']:>6}Mbps "
              f"{row['ping_ms']:>6}ms "
              f"{row['server_name']}")

def main():
    # Find data file
    data_dir = Path(__file__).parent / "speedtest_data"
    csv_file = data_dir / "speed_history.csv"
    
    if not csv_file.exists():
        # Try current directory
        csv_file = Path("speed_history.csv")
    
    print("🔍 Loading speed test data...")
    data = load_speed_data(csv_file)
    
    if not data:
        print("No speed test data found. Run speedtest_monitor.py first.")
        sys.exit(1)
    
    print_summary(data)
    print_recent(data, 15)
    
    print(f"\n💾 Data file: {csv_file}")
    print(f"📅 First test: {data[0]['timestamp'][:16]}")
    print(f"📅 Last test:  {data[-1]['timestamp'][:16]}")

if __name__ == "__main__":
    main()