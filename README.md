# Raspberry Pi Internet Speed Monitor

A robust, headless Raspberry Pi solution that automatically monitors internet speed every 15 minutes with comprehensive failure logging and syncs data to a local SMB network share.

## ✨ Features

- 🚀 **Automated Testing**: Speed tests every 15 minutes via cron
- 📊 **Rich Data Logging**: Download/upload speeds, ping, server info, and failure tracking
- 🔍 **Comprehensive Error Logging**: Detailed failure analysis and categorization
- 🌐 **SMB Network Sync**: Automatic sync to network share for remote access
- 📈 **Data Visualization**: Clean display of successes, failures, and statistics
- ⚙️ **Headless Operation**: No GUI required, perfect for Raspberry Pi
- 🔒 **No Cloud Dependencies**: All data stays on your local network
- 📁 **Organized Storage**: Dedicated speedtest directory structure
- 🛠️ **Easy Setup**: One-command installation with rerunnable setup script

## 🚀 Quick Start

### 1. Install on Raspberry Pi

```bash
# Clone the repository
git clone https://github.com/jamescummins/speedtest_monitor.git
cd speedtest_monitor

# Run the automated setup (rerunnable)
chmod +x setup.sh
./setup.sh
```

The setup script automatically:
- ✅ Installs system dependencies (python3-venv, cifs-utils)
- ✅ Creates isolated Python virtual environment
- ✅ Installs speedtest-cli package
- ✅ Sets up systemd service
- ✅ Configures cron job for 15-minute intervals
- ✅ Creates data directories

### 2. Configure SMB Network Share

**Option A: Use included mount script**
```bash
# Edit mount.sh with your SMB details
nano mount.sh

# Run the mount script
./mount.sh
```

**Option B: Manual mount**
```bash
sudo mkdir -p /media/test
sudo mount -t cifs //your-server/share /media/test -o username=user,password=pass,uid=$(id -u),gid=$(id -g)
```

**Option C: Persistent mount (recommended)**
```bash
sudo nano /etc/fstab
# Add: //server/share /media/test cifs username=user,password=pass,uid=1000,gid=1000 0 0
sudo mount -a
```

### 3. Test & Verify

```bash
# Test SMB setup and connectivity
python test_setup.py

# Run manual speed test
python speedtest_monitor.py

# View results with failure analysis
python view_data.py
```

## 📊 Data & Monitoring

### Enhanced Data Format

Your speed test data includes comprehensive failure tracking:

**CSV Columns:**
- `timestamp`: ISO format date/time
- `download_mbps`: Download speed in Mbps
- `upload_mbps`: Upload speed in Mbps  
- `ping_ms`: Ping latency in milliseconds
- `server_name`: Speed test server name
- `server_country`: Server country
- `server_sponsor`: Server provider
- `status`: SUCCESS or FAILED
- `error_type`: Type of error if failed
- `error_details`: Detailed error information

### View Your Data

```bash
# Comprehensive data view with failure analysis
python view_data.py

# Monitor live logs
tail -f speedtest_data/speedtest.log

# Check cron execution
tail -f speedtest_data/cron.log
```

### Failure Analysis

The system tracks and categorizes failures:
- 🔧 **ConfigRetrievalError**: Network/ISP blocking issues
- 🌐 **NoMatchedServers**: Regional restrictions  
- 📡 **SpeedtestHTTPError**: Server/rate limiting issues
- 🎯 **BestServerError**: Server selection failures
- ⬇️ **DownloadTestError**: Download test failures
- ⬆️ **UploadTestError**: Upload test failures
- 💾 **CSVSaveError**: Local file save issues
- 🔄 **SMBSyncFailed**: Network share sync problems

### Network Access

Your data automatically syncs to `/media/test/speedtest/`:
- 📁 `speed_history.csv` - All test results with failure data
- 📋 `speedtest.log` - Detailed application logs
- 📊 Access from any device on your network
- 📈 Import CSV into Excel, Google Sheets, etc.

## 🔧 Management & Troubleshooting

### Check System Status

```bash
# View cron jobs
crontab -l

# Check if running automatically
tail speedtest_data/cron.log

# Manual speed test
python speedtest_monitor.py

# Test with debug output
DEBUG=1 python speedtest_monitor.py
```

### Systemd Service (Optional)

```bash
# Manual run via systemd
sudo systemctl start speedtest-monitor.service

# Check service status
sudo systemctl status speedtest-monitor.service

# View service logs
sudo journalctl -u speedtest-monitor.service
```

### Common Issues & Solutions

#### SMB Mount Problems
```bash
# Check if mounted
mount | grep /media/test

# Test SMB access and permissions
python test_setup.py

# Remount if needed
sudo umount /media/test
sudo mount -a

# Check mount script
./mount.sh
```

#### Cron Job Not Running
```bash
# Check cron job exists with correct paths
crontab -l

# Check cron service is running
sudo systemctl status cron

# Check for cron errors
grep CRON /var/log/syslog
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment if needed
rm -rf ~/.venv/speedtest_monitor
./setup.sh

# Manual activation
source ~/.venv/speedtest_monitor/bin/activate
```

#### Network Connectivity
```bash
# Test basic connectivity
ping google.com

# Test speedtest CLI directly
source ~/.venv/speedtest_monitor/bin/activate
speedtest-cli

# Check if servers are accessible
speedtest-cli --list
```

## 🎯 Project Structure

```
speedtest_monitor/
├── speedtest_monitor.py    # Main monitoring script with failure logging
├── test_setup.py          # SMB connectivity and permission testing
├── view_data.py           # Data viewer with failure analysis
├── test_failure.py        # Failure simulation for testing
├── setup.sh               # Automated setup script (rerunnable)
├── mount.sh               # SMB mounting helper script
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
└── speedtest_data/       # Local data storage
    ├── speed_history.csv # Speed test results with failure data
    ├── speedtest.log     # Detailed application logs
    └── cron.log         # Cron execution logs
```

## 🌟 Why Choose SMB Over Cloud?

- 🔒 **Privacy**: Your data never leaves your network
- 🚀 **Reliability**: No cloud outages or API rate limits
- 💰 **Cost**: No monthly cloud storage fees
- 🔧 **Simplicity**: No OAuth flows or API keys to manage
- 📶 **Offline Access**: View data even without internet
- 🏠 **Network Integration**: Works with existing SMB/NAS setup

## 🛠️ Customization Options

### Change Test Frequency
```bash
# Edit cron job (currently every 15 minutes)
crontab -e
# Change */15 to */30 for 30 minutes, */5 for 5 minutes, etc.
```

### Add Custom Metrics
Extend `speedtest_monitor.py` to capture:
- Multiple server comparisons
- Network interface information  
- System temperature monitoring
- Historical trend analysis

### Create Web Dashboard
```python
# Simple Flask dashboard example
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def dashboard():
    df = pd.read_csv('speedtest_data/speed_history.csv')
    return render_template('dashboard.html', 
                         successful=df[df['status']=='SUCCESS'],
                         failed=df[df['status']=='FAILED'])
```

## 📈 Performance & Storage

- **System Impact**: Minimal CPU/RAM usage
- **Storage Growth**: ~50-100MB per year
- **Bandwidth Usage**: ~100MB/month for tests
- **Power Consumption**: ~$2/year on Raspberry Pi
- **Reliability**: 99%+ uptime with proper setup

## 🔍 Advanced Features

### Debug Mode
```bash
# Enable detailed logging
DEBUG=1 python speedtest_monitor.py
```

### Failure Testing
```bash
# Test failure logging system
python test_failure.py
```

### Manual SMB Operations
```bash
# Test SMB connectivity
python test_setup.py

# Mount SMB with custom options
./mount.sh
```

---

**⏱️ Setup Time**: ~5-10 minutes  
**🔧 Maintenance**: Near zero  
**📊 Data Access**: Full network availability via SMB  
**🛡️ Reliability**: Comprehensive error handling and logging