#!/usr/bin/env python3
"""
Production deployment helper script for the Submission Processor.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_environment():
    """Check if all required files and environment variables are present."""
    required_files = [
        'streamlit_app.py',
        'requirements.txt',
        'adopt/agent.py',
        'adopt/tools.py'
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    required_env_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("These will need to be configured in your deployment platform.")
    
    return True

def create_deployment_guide():
    """Create a deployment guide."""
    guide = """
# 🚀 Deployment Guide

## Quick Deploy Options:

### 1. Streamlit Community Cloud (Recommended)
```bash
# Push to GitHub first
git add .
git commit -m "Deploy submission processor"
git push origin main

# Then go to: https://share.streamlit.io
# Connect your GitHub repo and deploy!
```

### 2. Railway
```bash
# Install Railway CLI: https://railway.app/cli
railway login
railway init
railway up
```

### 3. Heroku
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
heroku create your-app-name
heroku config:set GOOGLE_CLIENT_ID="your_value"
heroku config:set GOOGLE_CLIENT_SECRET="your_value"
git push heroku main
```

### 4. Docker (Any Cloud Provider)
```bash
# Build and run locally first
docker build -t submission-processor .
docker run -p 8501:8501 submission-processor

# Then deploy to your preferred cloud provider
```

## Environment Variables Needed:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_TOKEN_PATH (optional, defaults to token.json)

## Important Notes:
- OAuth token will need to be regenerated in production
- Make sure to set up proper secrets management
- Consider using environment-specific configurations
"""
    
    with open('DEPLOYMENT.md', 'w') as f:
        f.write(guide)
    
    print("📝 Created DEPLOYMENT.md with detailed instructions")

def main():
    """Main deployment preparation function."""
    print("🚀 Preparing Submission Processor for deployment...")
    
    if not check_environment():
        print("❌ Environment check failed")
        return False
    
    print("✅ Environment check passed")
    
    # Create deployment guide
    create_deployment_guide()
    
    print("\n🎯 Deployment files created:")
    deployment_files = [
        'Procfile', 'Dockerfile', 'railway.json', 
        'runtime.txt', '.dockerignore', 'DEPLOYMENT.md'
    ]
    
    for file in deployment_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
    
    print("\n🌟 Ready for deployment!")
    print("\nChoose your deployment method:")
    print("1. Streamlit Community Cloud (easiest)")
    print("2. Railway (modern)")
    print("3. Heroku (classic)")
    print("4. Docker + Cloud Run/AWS")
    
    print("\n📖 See DEPLOYMENT.md for detailed instructions")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
