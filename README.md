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

**Note**: This setup uses Python virtual environments to resolve the "Externally-managed-environment" error in modern Raspberry Pi OS.

```bash
# Clone or download the files to your Pi
# Make setup script executable
chmod +x setup_raspberry_pi.sh

# Run setup (installs dependencies in virtual environment, creates cron job)
./setup_raspberry_pi.sh
```

### 2. Google Drive Setup (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. search for and enable **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Select **Desktop Application**
6. Download the `credentials.json` file
7. Place it in: `/home/pi/speedtest_monitor/speedtest_data/credentials.json`

### 3. First Run Authentication

**Important**: The first run requires manual authentication. The script now handles headless environments properly.

```bash
cd /home/pi/speedtest_monitor
source /home/pi/.venv/speedtest_monitor/bin/activate
python speedtest_monitor.py
```

**Authentication Options:**
1. **Headless/SSH Mode**: Script will provide a URL to open on another device
2. **Desktop Mode**: Opens browser automatically
3. **Manual Mode**: Copy authorization code from browser

**For Headless Raspberry Pi (most common):**
1. Run the command above
2. Copy the provided URL 
3. Open URL on your phone/computer
4. Complete Google authorization
5. Copy the authorization code
6. Paste it back in the Pi terminal

After first authentication, the script runs automatically without user interaction.

### 4. Test Authentication (Optional)

Use the included test script to verify your setup:

```bash
cd /home/pi/speedtest_monitor
source /home/pi/.venv/speedtest_monitor/bin/activate
python test_auth.py
```

This will check your authentication and provide detailed status information.

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
source /home/pi/.venv/speedtest_monitor/bin/activate
python speedtest_monitor.py
```

### Troubleshooting

#### "Externally-managed-environment" Error
This error occurs with newer Python installations. Our setup script creates a virtual environment to resolve this:

```bash
# If you encounter this error, activate the virtual environment:
source /home/pi/.venv/speedtest_monitor/bin/activate
pip install [package_name]
```

#### Google Auth UI Loop / Browser Issues
If you're stuck in an authentication loop or browser won't open:

```bash
# 1. Remove existing token and try again
rm /home/pi/speedtest_monitor/speedtest_data/token.json

# 2. Run with virtual environment
cd /home/pi/speedtest_monitor
source /home/pi/.venv/speedtest_monitor/bin/activate
python speedtest_monitor.py

# 3. Follow the manual authentication prompts
# The script will provide a URL to open on another device
```

**Common auth issues:**
- **No display/browser**: Script automatically detects headless mode
- **SSH connection**: Uses console-based authentication
- **Permission errors**: Check file permissions in speedtest_data folder
- **Network issues**: Ensure internet connectivity for Google services

#### Other Issues
```bash
# Check system logs
sudo journalctl -u speedtest-monitor.service

# Test internet connectivity
ping google.com

# Test speedtest CLI (in virtual environment)
source /home/pi/.venv/speedtest_monitor/bin/activate
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

- ✅ **Virtual Environment**: Isolated Python environment prevents system conflicts and resolves "Externally-managed-environment" error
- ✅ **OAuth Security**: Google credentials stored locally with auto-refresh tokens
- ✅ **No Plain-text Passwords**: All authentication uses secure OAuth flow
- ✅ **Local Data Storage**: Speed test data stored locally on Pi with optional cloud sync

## Python Environment Management

### Working with Virtual Environments

Our setup uses virtual environments to avoid the "Externally-managed-environment" error:

```bash
# Activate the virtual environment
source /home/pi/.venv/speedtest_monitor/bin/activate

# Install additional packages (if needed)
pip install package_name

# Deactivate when done
deactivate
```

### Manual Virtual Environment Setup

If you need to recreate the virtual environment:

```bash
# Remove existing environment
rm -rf /home/pi/.venv/speedtest_monitor

# Create new virtual environment
python3 -m venv /home/pi/.venv/speedtest_monitor

# Activate and install packages
source /home/pi/.venv/speedtest_monitor/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Alternative: Using pipx (System-wide Tool Installation)

For system-wide tool installation without conflicts:

```bash
# Install pipx
sudo apt install pipx

# Install tools globally
pipx install speedtest-cli
```

---

**Total setup time: ~15 minutes**  
**Maintenance required: Near zero**  
**Remote access: Full data available via Google Drive**