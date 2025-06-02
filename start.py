#!/usr/bin/env python3
"""
🌱 Plant Monitoring System - Startup Script
==============================================

This script helps you start the Plant Health Management System easily.
It checks dependencies, MongoDB connection, and starts the Flask application.
"""

import sys
import subprocess
import importlib
import os
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required")
        logger.error(f"Current version: {sys.version}")
        return False
    logger.info(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'flask_login',
        'pymongo',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is missing")
    
    if missing_packages:
        logger.error("\n📦 Missing packages detected!")
        logger.error("Please install them using:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        logger.error("\nOr install all dependencies:")
        logger.error("pip install -r requirements.txt")
        return False
    
    return True

def check_mongodb():
    """Check MongoDB connection"""
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        logger.info("✅ MongoDB is running and accessible")
        client.close()
        return True
    except Exception as e:
        logger.error("❌ MongoDB connection failed")
        logger.error(f"Error: {e}")
        logger.error("\n🔧 MongoDB Setup Instructions:")
        logger.error("1. Install MongoDB Community Edition")
        logger.error("2. Start MongoDB service:")
        logger.error("   - Windows: net start MongoDB")
        logger.error("   - macOS: brew services start mongodb-community")
        logger.error("   - Linux: sudo systemctl start mongod")
        logger.error("3. Ensure MongoDB is running on localhost:27017")
        return False

def start_application():
    """Start the Flask application"""
    try:
        logger.info("🚀 Starting Plant Monitoring System...")
        logger.info("📱 Application will be available at: http://127.0.0.1:5000")
        logger.info("🔑 Demo login - Username: admin, Password: admin123")
        logger.info("⏹️  Press Ctrl+C to stop the application")
        logger.info("-" * 60)
        
        # Import and run the Flask app
        from app import app, init_db
        
        # Initialize database
        init_db()
        
        # Start the Flask development server
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except KeyboardInterrupt:
        logger.info("\n👋 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🌱 Plant Monitoring System - Startup Check")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check MongoDB
    if not check_mongodb():
        sys.exit(1)
    
    print("\n✅ All checks passed! Starting application...")
    print("-" * 50)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
