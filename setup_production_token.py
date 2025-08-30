#!/usr/bin/env python3
"""
Production token setup for Streamlit Cloud deployment.
Run this locally to generate a token that can be used in production.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/gmail.send'
]

def create_production_token():
    """Create a token suitable for production deployment."""
    
    # Get credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET environment variables")
        print("Please set up your .env file first")
        return False
    
    print("🚀 Setting up production OAuth token...")
    
    # Create client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    try:
        print("🌐 Starting OAuth flow...")
        print("📱 A browser window will open for authorization")
        
        # Run OAuth flow with offline access to get refresh token
        creds = flow.run_local_server(
            port=8080, 
            open_browser=True, 
            access_type='offline', 
            prompt='consent'
        )
        
        print("✅ OAuth flow completed successfully!")
        
        # Save the token
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        
        # Save to local file
        with open('production_token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("💾 Token saved to 'production_token.json'")
        print("\n🎯 Next steps for Streamlit Cloud deployment:")
        print("1. Copy the contents of 'production_token.json'")
        print("2. In Streamlit Cloud, go to your app settings")
        print("3. Add a new secret: GOOGLE_TOKEN_JSON")
        print("4. Paste the entire JSON content as the value")
        print("\nAlternatively, you can copy-paste this token data:")
        print("=" * 50)
        print(json.dumps(token_data, indent=2))
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth flow failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = create_production_token()
    if success:
        print("\n🌟 Production token setup complete!")
    else:
        print("\n❌ Production token setup failed!")
