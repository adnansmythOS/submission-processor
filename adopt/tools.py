import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import hashlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field, validator
import email_validator


class UserSubmission(BaseModel):
    """Schema for user submission data."""
    name: str = Field(..., min_length=1, description="User's full name")
    email: str = Field(..., description="User's email address")
    address: str = Field(..., min_length=1, description="User's address")
    recipient_email: str = Field(..., description="Email address to send the document to")
    
    @validator('name', 'address')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @validator('email', 'recipient_email')
    def validate_email(cls, v):
        try:
            valid = email_validator.validate_email(v)
            return valid.email
        except email_validator.EmailNotValidError:
            raise ValueError("Invalid email format")


class GoogleAPIManager:
    """Manages Google API authentication and service creation."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self, client_id: str, client_secret: str, token_path: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_path = token_path
        self._creds = None
    
    def get_credentials(self) -> Credentials:
        """Get or refresh OAuth credentials."""
        if self._creds and self._creds.valid:
            return self._creds
            
        creds = None
        print(f"🔍 Checking for existing token at: {self.token_path}")
        
        # Load existing token
        if os.path.exists(self.token_path):
            print("✅ Found existing token file, loading...")
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        else:
            print("❌ No existing token file found")
        
        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            else:
                print("🌐 Starting OAuth flow...")
                print("📱 A browser window will open for authorization")
                print("🔗 If browser doesn't open, copy the URL that appears")
                
                # Create client config for OAuth flow
                client_config = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, self.SCOPES)
                
                try:
                    print("🚀 Starting local server on port 8080...")
                    # Try different approaches for OAuth
                    try:
                        creds = flow.run_local_server(port=8080, open_browser=True, access_type='offline', prompt='consent')
                    except Exception as local_server_error:
                        print(f"⚠️  Local server failed: {local_server_error}")
                        print("🔄 Trying console-based OAuth flow...")
                        creds = flow.run_console(access_type='offline', prompt='consent')
                    print("✅ OAuth flow completed successfully!")
                except Exception as e:
                    print(f"❌ OAuth flow failed: {str(e)}")
                    print("💡 Make sure port 8080 is available and redirect URI is configured correctly")
                    raise
            
            # Save credentials
            print("💾 Saving credentials to token file...")
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            print("✅ Credentials saved successfully")
        
        self._creds = creds
        return creds
    
    def get_service(self, service_name: str, version: str):
        """Get authenticated Google API service."""
        creds = self.get_credentials()
        return build(service_name, version, credentials=creds)


class CreateGoogleDocTool(BaseTool):
    """Tool to create a Google Doc with user submission data."""
    
    name = "create_google_doc"
    description = "Creates a Google Doc with formatted user submission data"
    api_manager: GoogleAPIManager = Field(...)
    drive_folder_id: Optional[str] = Field(default=None)
    
    def __init__(self, api_manager: GoogleAPIManager, drive_folder_id: Optional[str] = None):
        super().__init__(api_manager=api_manager, drive_folder_id=drive_folder_id)
    
    def _run(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Google Doc with submission data."""
        try:
            # Validate submission data
            submission = UserSubmission(**submission_data)
            
            # Create timestamp for unique title
            timestamp = datetime.now().isoformat()
            doc_title = f"Submission - {submission.name} - {timestamp}"
            
            # Create document
            docs_service = self.api_manager.get_service('docs', 'v1')
            
            doc_body = {
                'title': doc_title
            }
            
            # Create the document
            doc = docs_service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')
            
            # Format content
            content = f"""Name: {submission.name}

Email: {submission.email}

Address: {submission.address}"""
            
            # Insert content into document
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]
            
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Move to folder if specified
            if self.drive_folder_id:
                drive_service = self.api_manager.get_service('drive', 'v3')
                drive_service.files().update(
                    fileId=doc_id,
                    addParents=self.drive_folder_id,
                    removeParents='root'
                ).execute()
            
            return {
                'success': True,
                'document_id': doc_id,
                'document_url': f'https://docs.google.com/document/d/{doc_id}',
                'title': doc_title
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class ExportDocxTool(BaseTool):
    """Tool to export Google Doc as DOCX file."""
    
    name = "export_docx"
    description = "Exports a Google Doc as DOCX format"
    api_manager: GoogleAPIManager = Field(...)
    
    def __init__(self, api_manager: GoogleAPIManager):
        super().__init__(api_manager=api_manager)
    
    def _run(self, document_id: str) -> Dict[str, Any]:
        """Export document as DOCX."""
        try:
            drive_service = self.api_manager.get_service('drive', 'v3')
            
            # Export as DOCX
            export_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            request = drive_service.files().export_media(
                fileId=document_id,
                mimeType=export_mime_type
            )
            
            docx_content = request.execute()
            
            return {
                'success': True,
                'docx_content': docx_content,
                'mime_type': export_mime_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class SendEmailTool(BaseTool):
    """Tool to send email with DOCX attachment via Gmail API."""
    
    name = "send_email"
    description = "Sends email with DOCX attachment to specified recipient"
    api_manager: GoogleAPIManager = Field(...)
    
    def __init__(self, api_manager: GoogleAPIManager):
        super().__init__(api_manager=api_manager)
    
    def _run(self, docx_content: bytes, document_title: str, document_url: str, submission_name: str, recipient_email: str) -> Dict[str, Any]:
        """Send email with DOCX attachment."""
        try:
            gmail_service = self.api_manager.get_service('gmail', 'v1')
            
            # Create MIME message
            message = MIMEMultipart()
            message['to'] = recipient_email
            message['subject'] = f'New Submission: {submission_name}'
            
            # Email body
            body_text = f"""New submission received from {submission_name}:

Document: {document_title}
View online: {document_url}

Please find the submission details in the attached DOCX file.
"""
            
            message.attach(MIMEText(body_text, 'plain'))
            
            # Attach DOCX
            attachment = MIMEApplication(
                docx_content,
                _subtype='vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=f'{document_title}.docx'
            )
            message.attach(attachment)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            send_message = gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'message_id': send_message['id'],
                'recipient': recipient_email
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }