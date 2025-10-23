#!/bin/bash
# Script to activate the speedtest monitor virtual environment
# Usage: source ./activate_venv.sh

# Get current user and home directory
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
VENV_PATH="$HOME_DIR/.venv/speedtest_monitor"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🐍 Speedtest Monitor Virtual Environment Activation${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
    echo ""
    echo -e "${YELLOW}💡 To create the virtual environment, run:${NC}"
    echo "   ./setup.sh"
    echo ""
    return 1 2>/dev/null || exit 1
fi

# Check if already activated
if [ "$VIRTUAL_ENV" = "$VENV_PATH" ]; then
    echo -e "${GREEN}✅ Virtual environment already activated!${NC}"
    echo -e "   Path: $VIRTUAL_ENV"
    echo ""
    return 0 2>/dev/null || exit 0
fi

# Activate the virtual environment
echo -e "${GREEN}🔄 Activating virtual environment...${NC}"
echo "   Path: $VENV_PATH"
source "$VENV_PATH/bin/activate"

# Verify activation
if [ "$VIRTUAL_ENV" = "$VENV_PATH" ]; then
    echo -e "${GREEN}✅ Virtual environment activated successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Available commands:${NC}"
    echo "   python speedtest_monitor.py    # Run speed test"
    echo "   python view_data.py           # View collected data"
    echo "   python tests/test_setup.py    # Test SMB setup"
    echo "   python web_ui/start_web_ui.py # Start web UI"
    echo ""
    echo -e "${YELLOW}💡 To deactivate later, simply run:${NC}"
    echo "   deactivate"
    echo ""
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    return 1 2>/dev/null || exit 1
fi