#!/bin/bash
# Setup script for Raspberry Pi Speed Test Monitor (SMB Version)
# This script is rerunnable - it will skip steps that are already completed

set -e  # Exit on any error

echo "🚀 Setting up Raspberry Pi Speed Test Monitor (SMB Version)..."

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
PROJECT_DIR=$(pwd)
VENV_PATH="$HOME_DIR/.venv/speedtest_monitor"

echo "Setting up for user: $CURRENT_USER"
echo "Home directory: $HOME_DIR"
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $VENV_PATH"
echo ""

# Update system
echo "📦 Checking system packages..."
if ! dpkg -l | grep -q cifs-utils; then
    echo "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    
    # Install system packages
    echo "Installing required system packages..."
    sudo apt install -y python3-pip python3-venv cifs-utils
else
    echo "✅ Required system packages already installed"
fi
echo ""

# Install Python dependencies in virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv "$VENV_PATH"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo "Activating virtual environment and installing/updating packages..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install speedtest-cli
echo "✅ Python packages installed/updated"
echo ""

# Create data directory
echo "📁 Setting up data directory..."
if [ ! -d "$PROJECT_DIR/speedtest_data" ]; then
    mkdir -p "$PROJECT_DIR/speedtest_data"
    echo "✅ Data directory created"
else
    echo "✅ Data directory already exists"
fi
echo ""

# Create systemd service for better process management (optional)
echo "⚙️  Setting up systemd service..."
SERVICE_FILE="/etc/systemd/system/speedtest-monitor.service"

# Always create/update the service file to ensure correct paths
echo "Creating/updating systemd service..."
cat > /tmp/speedtest-monitor.service << EOF
[Unit]
Description=Internet Speed Test Monitor (SMB)
After=network.target

[Service]
Type=oneshot
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PATH/bin/python $PROJECT_DIR/speedtest_monitor.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/speedtest-monitor.service "$SERVICE_FILE"
sudo systemctl daemon-reload
echo "✅ Systemd service created/updated"

# Enable service if not already enabled
if ! systemctl is-enabled speedtest-monitor.service >/dev/null 2>&1; then
    sudo systemctl enable speedtest-monitor.service
    echo "✅ Systemd service enabled"
else
    echo "✅ Systemd service already enabled"
fi
echo ""

# Setup cron job for every 15 minutes
echo "⏰ Setting up cron job..."
CRON_JOB="*/15 * * * * cd $PROJECT_DIR && $VENV_PATH/bin/python speedtest_monitor.py >> speedtest_data/cron.log 2>&1"

# Check current crontab
echo "Checking current crontab..."
CURRENT_CRONTAB=$(crontab -l 2>/dev/null || echo "")

# Check if cron job already exists
if echo "$CURRENT_CRONTAB" | grep -q "speedtest_monitor.py"; then
    echo "✅ Cron job already exists"
    echo "Current cron job:"
    echo "$CURRENT_CRONTAB" | grep "speedtest_monitor.py"
else
    echo "Adding cron job for every 15 minutes..."
    echo "Cron job to add: $CRON_JOB"
    
    # Add to crontab
    if echo "$CURRENT_CRONTAB" | grep -v '^$' > /dev/null; then
        # Existing crontab has content
        (echo "$CURRENT_CRONTAB"; echo "$CRON_JOB") | crontab -
    else
        # Empty crontab
        echo "$CRON_JOB" | crontab -
    fi
    
    # Verify it was added
    if crontab -l 2>/dev/null | grep -q "speedtest_monitor.py"; then
        echo "✅ Cron job added successfully"
        echo "Current cron jobs:"
        crontab -l 2>/dev/null | grep "speedtest_monitor.py"
    else
        echo "❌ Failed to add cron job"
    fi
fi
echo ""

echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Set up your SMB share mount:"
echo "   - Edit /etc/fstab to add your SMB share"
echo "   - Example: //server/share /media/test cifs username=user,password=pass,uid=$CURRENT_USER,gid=$CURRENT_USER 0 0"
echo "   - Or mount manually: sudo mount -t cifs //server/share /media/test -o username=user,password=pass"
echo ""
echo "2. Test your SMB setup:"
echo "   source $VENV_PATH/bin/activate"
echo "   python test_setup.py"
echo ""
echo "3. Run a test speed test:"
echo "   source $VENV_PATH/bin/activate"
echo "   python speedtest_monitor.py"
echo ""
echo "4. View your data:"
echo "   source $VENV_PATH/bin/activate"
echo "   python view_data.py"
echo ""
echo "📊 Monitoring Information:"
echo "- The script will run automatically every 15 minutes via cron"
echo "- View logs: tail -f $PROJECT_DIR/speedtest_data/speedtest.log"
echo "- View cron logs: tail -f $PROJECT_DIR/speedtest_data/cron.log"
echo "- Manual run: systemctl start speedtest-monitor.service"
echo ""
echo "💡 Benefits of SMB approach:"
echo "- No cloud authentication required"
echo "- Works entirely on your local network"
echo "- Data accessible from any device on your network"
echo "- No internet dependency for data access"
echo "- Simple file copying - very reliable"
echo ""
echo "🔄 This script is rerunnable - you can run it again safely!"