# Raspberry Pi Internet Speed Monitor

A headless Raspberry Pi solution that automatically monitors internet speed every 15 minutes and syncs data to Google Drive.

## Features

- ✅ Automatic speed tests every 15 minutes
- ✅ Local CSV data storage with timestamps
- ✅ Google Drive cloud sync for remote access
- ✅ Comprehensive logging and error handling
- ✅ Headless operation (no GUI required)
- ✅ Minimal setup and maintenance

## Quick Start

### 1. Setup on Raspberry Pi

```bash
# Clone or download the files to your Pi
# Make setup script executable
chmod +x setup_raspberry_pi.sh

# Run setup (installs dependencies, creates cron job)
./setup_raspberry_pi.sh
```

### 2. Google Drive Setup (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Select **Desktop Application**
6. Download the `credentials.json` file
7. Place it in: `/home/pi/speedtest_monitor/speedtest_data/credentials.json`

### 3. First Run Authentication

```bash
cd /home/pi/speedtest_monitor
python3 speedtest_monitor.py
```

This will open a browser for Google authentication (only needed once).

## Data Access

### View Data Locally
```bash
# View recent speed tests
tail speedtest_data/speed_history.csv

# View logs
tail -f speedtest_data/speedtest.log
```

### Access from Cloud
- Your data syncs to Google Drive in folder: `RaspberryPi_SpeedTest`
- Download CSV file to analyze with Excel, Google Sheets, etc.
- Data includes: timestamp, download/upload speeds, ping, server info

## Data Format

CSV columns:
- `timestamp`: ISO format date/time
- `download_mbps`: Download speed in Mbps
- `upload_mbps`: Upload speed in Mbps  
- `ping_ms`: Ping latency in milliseconds
- `server_name`: Speed test server name
- `server_country`: Server country
- `server_sponsor`: Server provider

## Monitoring & Maintenance

### Check if Running
```bash
# View cron jobs
crontab -l

# Check recent activity
tail speedtest_data/cron.log
```

### Manual Test
```bash
cd /home/pi/speedtest_monitor
python3 speedtest_monitor.py
```

### Troubleshooting
```bash
# Check system logs
sudo journalctl -u speedtest-monitor.service

# Test internet connectivity
ping google.com

# Test speedtest CLI
speedtest-cli
```

## Alternative Cloud Options

### Option 1: Dropbox (easier but smaller storage)
Replace Google Drive code with Dropbox API - 2GB free storage

### Option 2: Simple FTP Upload
```python
# Add to script for basic FTP upload
import ftplib
def upload_to_ftp():
    with ftplib.FTP('your-server.com') as ftp:
        ftp.login('username', 'password')
        with open(CSV_FILE, 'rb') as f:
            ftp.storbinary('STOR speed_history.csv', f)
```

### Option 3: Email Reports
```python
# Add email functionality for daily summaries
import smtplib
from email.mime.text import MIMEText
```

## Customization

### Change Test Interval
Edit cron job:
```bash
crontab -e
# Change */15 to */30 for 30 minutes, etc.
```

### Add More Metrics
Extend the `run_speed_test()` function to capture:
- Multiple server tests
- Network interface info
- System temperature
- Bandwidth usage

### Data Visualization
Create a simple web dashboard by adding Flask:
```python
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def dashboard():
    df = pd.read_csv(CSV_FILE)
    return render_template('dashboard.html', data=df.to_dict('records'))
```

## Cost & Storage

- **Free**: Google Drive (15GB), Raspberry Pi electricity (~$2/year)
- **Estimated data usage**: ~50MB per year (1 test every 15 min)
- **Bandwidth impact**: Minimal (~100MB/month for speed tests)

## Security Notes

- Google credentials stored locally on Pi only
- OAuth tokens auto-refresh
- No plain-text passwords required
- Local data encrypted if Pi has full disk encryption

---

**Total setup time: ~15 minutes**  
**Maintenance required: Near zero**  
**Remote access: Full data available via Google Drive**