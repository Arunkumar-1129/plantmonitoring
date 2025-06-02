#!/usr/bin/env python3
"""
🌱 Plant Monitoring System - Website Launcher
==============================================

This script starts the website and automatically opens it in your browser.
"""

import sys
import time
import webbrowser
import threading
import subprocess
from pymongo import MongoClient

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        client.close()
        return True
    except Exception:
        return False

def open_browser_delayed():
    """Open browser after a short delay"""
    time.sleep(3)  # Wait 3 seconds for server to start
    print("🌐 Opening website in your browser...")
    webbrowser.open('http://127.0.0.1:5000')

def main():
    print("🌱 Plant Monitoring System - Website Launcher")
    print("=" * 50)
    
    # Check MongoDB
    if not check_mongodb():
        print("❌ MongoDB is not running!")
        print("Please start MongoDB first:")
        print("  - Windows: net start MongoDB")
        print("  - Or start MongoDB Compass")
        input("\nPress Enter to exit...")
        return
    
    print("✅ MongoDB is running")
    print("🚀 Starting website server...")
    print("📱 Website will open at: http://127.0.0.1:5000")
    print("🔑 Demo login: admin / admin123")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app
    try:
        from app import app, init_db
        init_db()
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Website stopped by user")
    except Exception as e:
        print(f"❌ Error starting website: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
