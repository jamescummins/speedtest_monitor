#!/usr/bin/env python3
"""
Start the Speedtest Monitor Web UI
Production-ready Flask server with proper configuration
"""

import os
import sys
from pathlib import Path

# Add the web_ui directory to the Python path
web_ui_dir = Path(__file__).parent
sys.path.insert(0, str(web_ui_dir))

from app import app

def main():
    """Start the web server"""
    print("🚀 Starting Internet Speed Monitor Web UI...")
    print(f"📁 Web UI directory: {web_ui_dir}")
    print(f"📊 Dashboard will be available at: http://localhost:5000")
    print(f"🌐 Or from any device on your network at: http://YOUR_PI_IP:5000")
    print("")
    print("💡 Tips:")
    print("   - Use Ctrl+C to stop the server")
    print("   - Dashboard auto-refreshes every 5 minutes")
    print("   - Charts update every 15 minutes")
    print("   - Click time range buttons to view different periods")
    print("")
    
    try:
        # Run Flask development server
        # For production, consider using gunicorn or waitress
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=5000,
            debug=False,     # Set to False for production
            threaded=True    # Handle multiple requests
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down web server...")
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()