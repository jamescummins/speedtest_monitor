#!/bin/bash
# Script to start the Speedtest Monitor Web UI
# This script activates the virtual environment and starts the web server

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
PROJECT_DIR="/home/james/workspace/speedtest_monitor"
VENV_PATH="$HOME_DIR/.venv/speedtest_monitor"

echo -e "${BLUE}🌐 Speedtest Monitor Web UI Launcher${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "speedtest_monitor.py" ]; then
    echo -e "${YELLOW}📁 Changing to project directory...${NC}"
    cd "$PROJECT_DIR" || {
        echo -e "${RED}❌ Could not find project directory: $PROJECT_DIR${NC}"
        exit 1
    }
fi

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
    echo -e "${YELLOW}💡 Please run ./setup.sh first to create the virtual environment${NC}"
    exit 1
fi

# Check if data directory exists and has data
if [ ! -f "speedtest_data/speed_history.csv" ]; then
    echo -e "${YELLOW}⚠️  Warning: No speedtest data found!${NC}"
    echo -e "${YELLOW}   Run 'python speedtest_monitor.py' first to collect some data${NC}"
    echo ""
fi

# Activate virtual environment and start web UI
echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate" || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}

echo -e "${GREEN}🚀 Starting Web UI...${NC}"
echo -e "${BLUE}📊 Dashboard URL: http://localhost:5000${NC}"
echo -e "${BLUE}🌐 Network URL: http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo ""

# Change to web_ui directory and start the server
cd web_ui || {
    echo -e "${RED}❌ Could not find web_ui directory${NC}"
    exit 1
}

python start_web_ui.py