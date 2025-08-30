#!/usr/bin/env python3
"""
Simple OAuth test script to verify Google API authentication works.
"""

import os
from dotenv import load_dotenv
from adopt.tools import GoogleAPIManager

def test_oauth():
    """Test OAuth flow and basic API access."""
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
    
    if not client_id or not client_secret:
        print("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env file")
        return False
    
    print("🧪 Testing OAuth flow...")
    print(f"Client ID: {client_id[:20]}...")
    print(f"Token path: {token_path}")
    
    try:
        # Initialize API manager
        api_manager = GoogleAPIManager(client_id, client_secret, token_path)
        
        # Test getting credentials
        creds = api_manager.get_credentials()
        
        if creds and creds.valid:
            print("✅ OAuth successful! Credentials are valid.")
            
            # Test basic API access
            print("🔍 Testing Google APIs access...")
            
            # Test Docs API
            try:
                docs_service = api_manager.get_service('docs', 'v1')
                print("✅ Google Docs API access: OK")
            except Exception as e:
                print(f"❌ Google Docs API access failed: {e}")
                return False
            
            # Test Drive API
            try:
                drive_service = api_manager.get_service('drive', 'v3')
                print("✅ Google Drive API access: OK")
            except Exception as e:
                print(f"❌ Google Drive API access failed: {e}")
                return False
            
            # Test Gmail API
            try:
                gmail_service = api_manager.get_service('gmail', 'v1')
                profile = gmail_service.users().getProfile(userId='me').execute()
                print(f"✅ Gmail API access: OK (Email: {profile.get('emailAddress', 'Unknown')})")
            except Exception as e:
                print(f"❌ Gmail API access failed: {e}")
                return False
            
            print("\n🎉 All tests passed! OAuth and API access working correctly.")
            return True
            
        else:
            print("❌ OAuth failed: Invalid credentials")
            return False
            
    except Exception as e:
        print(f"❌ OAuth test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_oauth()
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your .env file has correct GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        print("2. Verify redirect URI is set to: http://localhost:8080")
        print("3. Check that APIs are enabled in Google Cloud Console")
        print("4. Make sure port 8080 is not blocked by firewall")
        exit(1)
    else:
        print("\n🚀 Ready to run the full agent!")
