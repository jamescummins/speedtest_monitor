#!/bin/bash
# Setup script for Raspberry Pi Speed Test Monitor

echo "Setting up Raspberry Pi Speed Test Monitor..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system packages needed for virtual environment
echo "Installing required system packages..."
sudo apt install -y python3-pip python3-venv

# Install Python dependencies in virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv /home/pi/.venv/speedtest_monitor
source /home/pi/.venv/speedtest_monitor/bin/activate
pip install --upgrade pip
pip install speedtest-cli google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

# Create service directory
INSTALL_DIR="/home/pi/speedtest_monitor"
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/speedtest_data"

# Copy script
cp speedtest_monitor.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/speedtest_monitor.py"

# Create systemd service for better process management (optional)
cat > /tmp/speedtest-monitor.service << EOF
[Unit]
Description=Internet Speed Test Monitor
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=$INSTALL_DIR
ExecStart=/home/pi/.venv/speedtest_monitor/bin/python $INSTALL_DIR/speedtest_monitor.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Creating systemd service..."
sudo mv /tmp/speedtest-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable speedtest-monitor.service

# Setup cron job for every 15 minutes
echo "Setting up cron job for every 15 minutes..."
CRON_JOB="*/15 * * * * cd $INSTALL_DIR && /home/pi/.venv/speedtest_monitor/bin/python speedtest_monitor.py >> speedtest_data/cron.log 2>&1"

# Add to crontab if not already present
(crontab -l 2>/dev/null | grep -v "speedtest_monitor.py"; echo "$CRON_JOB") | crontab -

echo ""
echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Go to https://console.cloud.google.com/"
echo "2. Create a new project or select existing"
echo "3. Enable Google Drive API"
echo "4. Create credentials (OAuth 2.0 Client ID for Desktop application)"
echo "5. Download credentials.json and place it in: $INSTALL_DIR/speedtest_data/"
echo ""
echo "Then run the first test manually to authenticate:"
echo "cd $INSTALL_DIR && source /home/pi/.venv/speedtest_monitor/bin/activate && python speedtest_monitor.py"
echo ""
echo "The script will run automatically every 15 minutes via cron."
echo "View logs: tail -f $INSTALL_DIR/speedtest_data/speedtest.log"
echo "View cron logs: tail -f $INSTALL_DIR/speedtest_data/cron.log"