"""
Gmail connector for MCP integration.
Handles Gmail API authentication and email operations.
"""

# PERMANENTLY DISABLE SSL VERIFICATION (for development/testing)
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import logging
import urllib3
from typing import Dict, Any, Optional, List
from pathlib import Path

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class GmailConnector:
    """Gmail API connector for sending and managing emails."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Gmail connector.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
        """
        self.credentials_path = credentials_path or os.getenv(
            "GMAIL_CREDENTIALS_PATH",
            str(Path.home() / ".orca" / "gmail_credentials.json")
        )
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            True if authentication successful
        """
        # DISABLE SSL VERIFICATION PERMANENTLY (for development/testing)
        import ssl
        import os
        ssl._create_default_https_context = ssl._create_unverified_context
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        try:
            # Check if credentials file exists
            if not Path(self.credentials_path).exists():
                logger.error(f"Gmail credentials not found at: {self.credentials_path}")
                logger.info("Please set up Gmail OAuth2 credentials first")
                return False
            
            # Try to import google libraries
            try:
                import requests
                import urllib3
                # Patch requests to disable SSL verification BEFORE importing Google libraries
                requests.packages.urllib3.disable_warnings()
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                # Monkey patch requests.Session to always disable SSL verification
                original_request = requests.Session.request
                def patched_request(self, *args, **kwargs):
                    kwargs['verify'] = False
                    return original_request(self, *args, **kwargs)
                requests.Session.request = patched_request
                
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                from googleapiclient.discovery import build
                import pickle
                import httplib2
            except ImportError:
                logger.error("Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
                return False
            
            # Patch httplib2 to disable SSL verification
            original_httplib2_init = httplib2.Http.__init__
            def patched_httplib2_init(self, *args, **kwargs):
                kwargs['disable_ssl_certificate_validation'] = True
                return original_httplib2_init(self, *args, **kwargs)
            httplib2.Http.__init__ = patched_httplib2_init
            
            # Load credentials
            creds = None
            token_path = Path.home() / ".orca" / "gmail_token.pickle"
            
            # Check for existing token
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # Refresh with SSL bypass
                    try:
                        # Create session with SSL verification disabled
                        session = requests.Session()
                        session.verify = False
                        request = Request(session)
                        creds.refresh(request)
                    except Exception as e:
                        logger.error(f"Failed to refresh token: {e}")
                        creds = None
                else:
                    # Create flow with SSL bypass
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
                    )
                    # Run OAuth flow - SSL is already disabled globally
                    creds = flow.run_local_server(port=0)
                
                # Save token for future use
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Gmail service - SSL is already disabled via patched httplib2
            # Don't pass http parameter, let it use the patched httplib2
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Restore httplib2 original (optional, but cleaner)
            httplib2.Http.__init__ = original_httplib2_init
            
            self.authenticated = True
            logger.info("Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email via Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
        
        Returns:
            Result dictionary with status and message
        """
        if not self.authenticated or not self.service:
            return {
                "success": False,
                "error": "Not authenticated with Gmail"
            }
        
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import base64
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": send_message.get('id'),
                "thread_id": send_message.get('threadId'),
                "message": f"Email sent successfully to {to}"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_emails(self, max_results: int = 10) -> Dict[str, Any]:
        """
        List recent emails.
        
        Args:
            max_results: Maximum number of emails to return
        
        Returns:
            Dictionary with list of emails
        """
        if not self.authenticated or not self.service:
            return {
                "success": False,
                "error": "Not authenticated with Gmail"
            }
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                email_list.append({
                    "id": msg['id'],
                    "subject": subject,
                    "from": sender
                })
            
            return {
                "success": True,
                "emails": email_list,
                "count": len(email_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to list emails: {e}")
            return {
                "success": False,
                "error": str(e)
            }

