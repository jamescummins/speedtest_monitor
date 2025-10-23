#!/bin/bash
# Script to start the Speedtest Monitor Web UI in background
# This script runs the web server as a background process

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
PID_FILE="$PROJECT_DIR/web_ui.pid"
LOG_FILE="$PROJECT_DIR/speedtest_data/web_ui.log"

echo -e "${BLUE}🌐 Speedtest Monitor Web UI Background Launcher${NC}"
echo ""

# Function to check if web UI is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"  # Clean up stale PID file
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to start the web UI
start_webui() {
    if check_running; then
        echo -e "${YELLOW}⚠️  Web UI is already running (PID: $(cat $PID_FILE))${NC}"
        echo -e "${BLUE}📊 Dashboard URL: http://localhost:5000${NC}"
        return 0
    fi

    # Check if we're in the right directory
    if [ ! -f "$PROJECT_DIR/speedtest_monitor.py" ]; then
        echo -e "${RED}❌ Could not find project directory: $PROJECT_DIR${NC}"
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
        echo -e "${YELLOW}💡 Please run ./setup.sh first to create the virtual environment${NC}"
        exit 1
    fi

    echo -e "${GREEN}🚀 Starting Web UI in background...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_PATH/bin/activate"
    
    # Start the web UI in background and capture PID
    nohup python web_ui/start_web_ui.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if check_running; then
        echo -e "${GREEN}✅ Web UI started successfully!${NC}"
        echo -e "${BLUE}📊 Dashboard URL: http://localhost:5000${NC}"
        echo -e "${BLUE}🌐 Network URL: http://$(hostname -I | awk '{print $1}'):5000${NC}"
        echo -e "${YELLOW}📋 PID: $(cat $PID_FILE)${NC}"
        echo -e "${YELLOW}📋 Logs: $LOG_FILE${NC}"
        echo ""
        echo -e "${YELLOW}💡 Commands:${NC}"
        echo -e "   ./stop_web_ui.sh     - Stop the web UI"
        echo -e "   tail -f $LOG_FILE    - View logs"
    else
        echo -e "${RED}❌ Failed to start Web UI${NC}"
        echo -e "${YELLOW}📋 Check logs: $LOG_FILE${NC}"
        exit 1
    fi
}

# Function to stop the web UI
stop_webui() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}🛑 Stopping Web UI (PID: $PID)...${NC}"
        kill "$PID"
        rm -f "$PID_FILE"
        echo -e "${GREEN}✅ Web UI stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Web UI is not running${NC}"
    fi
}

# Function to show status
status_webui() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ Web UI is running (PID: $PID)${NC}"
        echo -e "${BLUE}📊 Dashboard URL: http://localhost:5000${NC}"
        echo -e "${BLUE}🌐 Network URL: http://$(hostname -I | awk '{print $1}'):5000${NC}"
    else
        echo -e "${YELLOW}⚠️  Web UI is not running${NC}"
    fi
}

# Handle command line arguments
case "${1:-start}" in
    start)
        start_webui
        ;;
    stop)
        stop_webui
        ;;
    restart)
        stop_webui
        sleep 1
        start_webui
        ;;
    status)
        status_webui
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the web UI in background (default)"
        echo "  stop    - Stop the web UI"
        echo "  restart - Restart the web UI"
        echo "  status  - Show web UI status"
        exit 1
        ;;
esac