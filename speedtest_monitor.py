#!/usr/bin/env python3
"""
Raspberry Pi Internet Speed Monitor (SMB Version)
Runs speed tests and saves data to local SMB share

This is the main entry point that uses the modular architecture in the src/ folder.
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the main function from our modular architecture
from main import main


if __name__ == "__main__":
    # Execute the main function and exit with the appropriate code
    exit_code = main()
    sys.exit(exit_code)