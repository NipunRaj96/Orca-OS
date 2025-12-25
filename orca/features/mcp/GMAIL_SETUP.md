# Gmail MCP Setup Guide

## Quick Setup

1. **Get Gmail OAuth2 Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API (APIs & Services > Library > Gmail API > Enable)
   - Create OAuth2 credentials:
     - Go to APIs & Services > Credentials
     - Click "Create Credentials" > "OAuth client ID"
     - Choose "Desktop app" as application type
     - Download the JSON file

2. **Save Credentials:**
   - Copy the downloaded JSON file
   - Save it as `~/.orca/gmail_credentials.json`
   - OR set environment variable: `export GMAIL_CREDENTIALS_PATH=/path/to/your/credentials.json`

3. **First-Time Authentication:**
   - Run any email command: `orca "write an email to test@example.com with body test"`
   - A browser window will open for OAuth authorization
   - Sign in and grant permissions
   - Token will be saved automatically at `~/.orca/gmail_token.pickle`

## Credentials File Format

The `gmail_credentials.json` file should have this structure (see `gmail_credentials.json.example`):

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

## Usage Examples

```bash
# Send an email
orca "write an email to user@example.com with body Hello, this is a test email"

# Send with subject
orca "write an email to user@example.com about meeting tomorrow that we need to discuss the project"

# Natural language parsing
orca "email john.doe@company.com that I will be on leave today"
```

## Troubleshooting

- **SSL Certificate Errors:** Already handled - SSL verification is disabled for development
- **Authentication Failed:** Make sure credentials file is at `~/.orca/gmail_credentials.json`
- **Token Expired:** Delete `~/.orca/gmail_token.pickle` and re-authenticate

