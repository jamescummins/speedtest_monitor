#!/usr/bin/env python3
"""
Speedtest Monitor Web UI
Flask application for viewing speedtest data with interactive charts
"""

import os
import csv
import json
import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "speedtest_data"
CSV_FILE = DATA_DIR / "speed_history.csv"
SMB_MOUNT_PATH = Path("/media/test")
SMB_SPEEDTEST_DIR = SMB_MOUNT_PATH / "speedtest"
SMB_CSV = SMB_SPEEDTEST_DIR / "speed_history.csv"

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config['SECRET_KEY'] = 'speedtest-monitor-key-change-in-production'

def load_speed_data(limit=None, hours=None):
    """Load speed test data from CSV file"""
    # Try to load from SMB first, then local
    csv_paths = [SMB_CSV, CSV_FILE]
    data = []
    
    for csv_path in csv_paths:
        if csv_path.exists():
            try:
                with open(csv_path, 'r') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)
                break
            except Exception as e:
                print(f"Failed to read {csv_path}: {e}")
                continue
    
    if not data:
        return []
    
    # Filter by time if specified
    if hours:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        filtered_data = []
        for row in data:
            try:
                row_time = datetime.datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                if row_time >= cutoff_time:
                    filtered_data.append(row)
            except:
                continue
        data = filtered_data
    
    # Apply limit
    if limit:
        data = data[-limit:]
    
    return data

def calculate_statistics(data):
    """Calculate summary statistics from speed test data"""
    if not data:
        return {}
    
    # Separate successful and failed tests
    successful_tests = []
    failed_tests = []
    
    for row in data:
        # Check status first, then fallback to data validation for older entries
        is_failed = (
            row.get('status') == 'FAILED' or
            row.get('error_type') or
            (row.get('download_mbps') in [None, ''] and row.get('upload_mbps') in [None, ''])
        )
        
        if is_failed:
            failed_tests.append(row)
        else:
            successful_tests.append(row)
    
    stats = {
        'total_tests': len(data),
        'successful_tests': len(successful_tests),
        'failed_tests': len(failed_tests),
        'success_rate': round((len(successful_tests) / len(data)) * 100, 1) if data else 0
    }
    
    if successful_tests:
        try:
            downloads = [float(row['download_mbps']) for row in successful_tests if row['download_mbps']]
            uploads = [float(row['upload_mbps']) for row in successful_tests if row['upload_mbps']]
            pings = [float(row['ping_ms']) for row in successful_tests if row['ping_ms']]
            
            if downloads:
                stats['download'] = {
                    'avg': round(sum(downloads) / len(downloads), 2),
                    'min': round(min(downloads), 2),
                    'max': round(max(downloads), 2)
                }
            
            if uploads:
                stats['upload'] = {
                    'avg': round(sum(uploads) / len(uploads), 2),
                    'min': round(min(uploads), 2),
                    'max': round(max(uploads), 2)
                }
            
            if pings:
                stats['ping'] = {
                    'avg': round(sum(pings) / len(pings), 2),
                    'min': round(min(pings), 2),
                    'max': round(max(pings), 2)
                }
                
        except Exception as e:
            print(f"Error calculating statistics: {e}")
    
    return stats

def get_system_status():
    """Get system and SMB status information"""
    status = {
        'local_data': CSV_FILE.exists(),
        'local_data_size': CSV_FILE.stat().st_size if CSV_FILE.exists() else 0,
        'smb_mounted': SMB_MOUNT_PATH.exists() and SMB_MOUNT_PATH.is_mount(),
        'smb_data': SMB_CSV.exists(),
        'smb_data_size': SMB_CSV.stat().st_size if SMB_CSV.exists() else 0,
        'data_source': 'SMB' if SMB_CSV.exists() else 'Local' if CSV_FILE.exists() else 'None'
    }
    
    if CSV_FILE.exists():
        status['local_modified'] = datetime.datetime.fromtimestamp(
            CSV_FILE.stat().st_mtime
        ).isoformat()
    
    if SMB_CSV.exists():
        status['smb_modified'] = datetime.datetime.fromtimestamp(
            SMB_CSV.stat().st_mtime
        ).isoformat()
    
    return status

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    """API endpoint to get speed test data"""
    limit = request.args.get('limit', type=int)
    hours = request.args.get('hours', type=int)
    
    data = load_speed_data(limit=limit, hours=hours)
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    """API endpoint to get statistics"""
    hours = request.args.get('hours', type=int, default=24)
    
    data = load_speed_data(hours=hours)
    stats = calculate_statistics(data)
    return jsonify(stats)

@app.route('/api/recent')
def api_recent():
    """API endpoint to get recent test results"""
    limit = request.args.get('limit', type=int, default=10)
    
    data = load_speed_data(limit=limit)
    return jsonify(data)

@app.route('/api/status')
def api_status():
    """API endpoint to get system status"""
    status = get_system_status()
    return jsonify(status)

@app.route('/api/chart-data')
def api_chart_data():
    """API endpoint optimized for chart display"""
    hours = request.args.get('hours', type=int, default=24)
    
    data = load_speed_data(hours=hours)
    
    # Prepare separate arrays for successful and failed tests
    successful_data = []
    failed_data = []
    
    for row in data:
        try:
            # Parse timestamp
            timestamp = datetime.datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
            
            # Check if this is a failed test
            is_failed = (
                row.get('status') == 'FAILED' or
                row.get('error_type') or
                (row.get('download_mbps') in [None, ''] and row.get('upload_mbps') in [None, ''])
            )
            
            if is_failed:
                # Set failed tests to 0 values instead of excluding them
                successful_data.append({
                    'timestamp': timestamp.isoformat(),
                    'download_speed': 0,
                    'upload_speed': 0,
                    'ping_time': 0,
                    'is_failed': True,
                    'error_type': row.get('error_type', 'Unknown'),
                    'error_details': row.get('error_details', 'No details')
                })
                failed_data.append({
                    'timestamp': timestamp.isoformat(),
                    'error_type': row.get('error_type', 'Unknown'),
                    'error_details': row.get('error_details', 'No details')
                })
            else:
                # Include successful tests with actual data
                try:
                    download_speed = float(row['download_mbps']) if row['download_mbps'] else 0
                    upload_speed = float(row['upload_mbps']) if row['upload_mbps'] else 0
                    ping_time = float(row['ping_ms']) if row['ping_ms'] else 0
                    
                    successful_data.append({
                        'timestamp': timestamp.isoformat(),
                        'download_speed': download_speed,
                        'upload_speed': upload_speed,
                        'ping_time': ping_time,
                        'is_failed': False
                    })
                except (ValueError, TypeError):
                    # If data is invalid, set to 0
                    successful_data.append({
                        'timestamp': timestamp.isoformat(),
                        'download_speed': 0,
                        'upload_speed': 0,
                        'ping_time': 0,
                        'is_failed': True,
                        'error_type': 'Invalid Data',
                        'error_details': 'Could not parse speed test values'
                    })
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    # Prepare data for charts - only include points where data exists
    chart_data = {
        'successful_tests': successful_data,
        'failed_tests': failed_data
    }
    
    return jsonify(chart_data)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)