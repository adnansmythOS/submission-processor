#!/usr/bin/env python3
"""
Streamlit App Runner

This script helps run the Streamlit app with proper environment setup.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import streamlit
        import adopt.agent
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is properly configured."""
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with Google OAuth credentials.")
        return False
    
    print("✅ Environment variables configured")
    return True

def run_streamlit():
    """Run the Streamlit app."""
    if not check_requirements():
        return False
    
    if not check_environment():
        return False
    
    print("🚀 Starting Streamlit app...")
    print("📱 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8501")
    print("\n" + "="*50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_streamlit()
    if not success:
        sys.exit(1)
