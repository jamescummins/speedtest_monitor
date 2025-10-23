# Internet Speed Monitor - Web UI

A modern, interactive web dashboard for viewing internet speed test data with beautiful charts and real-time updates.

## Features

### 📊 Interactive Dashboard
- **Real-time charts** showing download/upload speeds over time
- **Ping latency visualization** with trend analysis
- **Time range selection** (24 hours, 3 days, 1 week, 30 days)
- **Responsive design** that works on desktop, tablet, and mobile

### 📈 Statistics & Analytics
- **Average speeds** with min/max values
- **Success rate tracking** with failure analysis
- **Recent test history** with detailed results
- **System status monitoring** (local vs SMB data)

### 🔄 Live Updates
- **Auto-refresh** every 5 minutes for stats and recent tests
- **Chart updates** every 15 minutes for performance
- **Manual refresh** button for immediate updates
- **Connection status** indicator

### 🎨 Modern Interface
- **Bootstrap 5** responsive design
- **Chart.js** interactive visualizations
- **Color-coded status** indicators
- **Loading animations** and smooth transitions

## Quick Start

### 1. Install Dependencies
```bash
# Make sure you're in the speedtest_monitor directory
cd /home/james/workspace/speedtest_monitor

# Install web UI dependencies (if not already installed)
pip install flask flask-cors
```

### 2. Start the Web Server
```bash
# Option 1: Use the startup script
python3 web_ui/start_web_ui.py

# Option 2: Direct Flask app
cd web_ui
python3 app.py
```

### 3. Access the Dashboard
Open your web browser and go to:
- **Local access**: http://localhost:5000
- **Network access**: http://YOUR_PI_IP:5000

Replace `YOUR_PI_IP` with your Raspberry Pi's actual IP address.

## API Endpoints

The web UI provides several REST API endpoints:

- `GET /api/data` - Raw speed test data with optional filtering
- `GET /api/stats` - Statistical summary (averages, success rate)
- `GET /api/recent` - Recent test results
- `GET /api/status` - System status (local/SMB data availability)
- `GET /api/chart-data` - Optimized data for chart rendering

### API Parameters
- `hours` - Limit data to last N hours (e.g., `?hours=24`)
- `limit` - Limit number of results (e.g., `?limit=50`)

### Example API Usage
```bash
# Get statistics for last 24 hours
curl http://localhost:5000/api/stats?hours=24

# Get last 10 test results
curl http://localhost:5000/api/recent?limit=10

# Get chart data for last week
curl http://localhost:5000/api/chart-data?hours=168
```

## Configuration

### Data Sources
The web UI automatically detects and uses available data sources:
1. **SMB data** (preferred) - `/media/test/speedtest/speed_history.csv`
2. **Local data** (fallback) - `../speedtest_data/speed_history.csv`

### Auto-Refresh Settings
- **Statistics**: Updates every 5 minutes
- **Charts**: Updates every 15 minutes
- **Recent tests**: Updates every 5 minutes

You can modify these intervals in `static/js/dashboard.js`.

### Port Configuration
By default, the web server runs on port 5000. To change this:

1. Edit `web_ui/app.py` or `web_ui/start_web_ui.py`
2. Change the `port` parameter in `app.run()`

## Network Access

To access the dashboard from other devices on your network:

1. **Find your Pi's IP address**:
   ```bash
   hostname -I
   ```

2. **Open firewall port** (if needed):
   ```bash
   sudo ufw allow 5000/tcp
   ```

3. **Access from any device**:
   Open a browser and go to `http://YOUR_PI_IP:5000`

## Production Deployment

For production use, consider:

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up as a systemd service**:
   ```bash
   sudo cp speedtest-web-ui.service /etc/systemd/system/
   sudo systemctl enable speedtest-web-ui.service
   sudo systemctl start speedtest-web-ui.service
   ```

3. **Use a reverse proxy** (nginx/apache) for HTTPS and better performance

## Troubleshooting

### Common Issues

**"No data found"**
- Check that speedtest data exists in `speedtest_data/speed_history.csv`
- Verify the speedtest monitor is running and collecting data

**"Connection failed"**
- Ensure the Flask server is running
- Check that port 5000 is not blocked by firewall
- Verify network connectivity between devices

**Charts not loading**
- Check browser console for JavaScript errors
- Ensure internet connection for CDN resources (Chart.js, Bootstrap)
- Verify API endpoints are responding: `curl http://localhost:5000/api/status`

**SMB data not showing**
- Verify SMB mount is working: `ls /media/test/speedtest/`
- Check SMB permissions for read access
- Ensure speedtest monitor is syncing to SMB properly

### Debug Mode
To enable debug mode, edit `web_ui/app.py` and set:
```python
app.run(debug=True)
```

This provides detailed error messages and auto-reloading during development.

## File Structure
```
web_ui/
├── app.py                 # Flask application and API endpoints
├── start_web_ui.py        # Startup script
├── templates/
│   └── dashboard.html     # Main dashboard template
└── static/
    ├── css/
    │   └── dashboard.css  # Custom styles
    └── js/
        └── dashboard.js   # Dashboard JavaScript logic
```

## Browser Compatibility
- Chrome/Chromium 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance Notes
- Dashboard optimized for datasets up to 10,000 speed test records
- Charts use time-based sampling to maintain smooth performance
- API responses are cached briefly to reduce database load
- Auto-refresh intervals are staggered to minimize resource usage