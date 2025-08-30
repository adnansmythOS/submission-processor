# Submission Processing Agent

A LangChain + LangGraph agent that processes user submissions by creating Google Docs and sending them via email.

## Features

- ✅ Validates user input (name, email, address)
- 📄 Creates Google Doc with formatted submission data
- 💾 Exports Google Doc as DOCX format
- 📧 Sends email with DOCX attachment to fixed recipient
- 🔄 Error handling with retry logic
- 📊 Comprehensive logging and status tracking

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Create a Google Cloud project
2. Enable the following APIs:
   - Google Docs API
   - Google Drive API
   - Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download the client secret JSON file

### 3. Environment Configuration

Create a `.env` file with your credentials:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_TOKEN_PATH=token.json

# Note: Recipient email is now provided by user input, not environment variable

# Optional: Drive folder ID to organize docs
DRIVE_FOLDER_ID=your_folder_id_here
```

### 4. OAuth Setup

On first run, the agent will open a browser window for OAuth consent. This creates a `token.json` file for subsequent runs.

## Usage

### Web Interface (Recommended)

Launch the Streamlit web app for a user-friendly interface:

```bash
# Run the Streamlit app
python3 -m streamlit run streamlit_app.py

# Or use the helper script
python3 run_streamlit.py
```

The web interface provides:
- ✅ Clean, intuitive form fields
- ✅ Real-time validation
- ✅ Progress indicators
- ✅ Success/error messages with details
- ✅ Direct links to created documents

### Command Line

```bash
# Interactive mode
python main.py --interactive

# Direct arguments
python main.py --name "John Doe" --email "john@example.com" --address "123 Main St, City, State" --recipient "admin@company.com"
```

### Programmatic Usage

```python
from adopt.agent import create_agent

# Create agent
agent = create_agent()

# Process submission
result = agent.process_submission(
    name="Jane Smith",
    email="jane.smith@example.com", 
    address="456 Oak Avenue, Springfield, IL 62701",
    recipient_email="admin@company.com"
)

if result["success"]:
    print(f"Document created: {result['document_url']}")
    print(f"Email sent: {result['email_message_id']}")
else:
    print(f"Error: {result['message']}")
```

### Example Usage

```bash
python example_usage.py
```

## Architecture

### LangGraph Workflow

```
validate_input → create_document → export_docx → send_email → finalize
       ↓              ↓              ↓            ↓
   handle_error ← handle_error ← handle_error ← handle_error
```

### Components

- **UserSubmission**: Pydantic model for input validation
- **GoogleAPIManager**: Handles OAuth and API service creation
- **CreateGoogleDocTool**: Creates and populates Google Docs
- **ExportDocxTool**: Exports docs to DOCX format
- **SendEmailTool**: Sends emails with attachments via Gmail API
- **SubmissionAgent**: LangGraph orchestrator

### Google API Scopes

- `https://www.googleapis.com/auth/documents` - Create and edit Google Docs
- `https://www.googleapis.com/auth/drive.file` - Export docs and manage created files
- `https://www.googleapis.com/auth/gmail.send` - Send emails

## Document Format

Each submission creates a Google Doc with:

```
Title: Submission - [Name] - [ISO Timestamp]

Content:
Name: [User Name]

Email: [User Email]

Address: [User Address]
```

## Email Format

- **Subject**: `New Submission: [Name]`
- **Body**: Summary with document link
- **Attachment**: DOCX file with submission data

## Error Handling

- Input validation with clear error messages
- Retry logic for transient API errors
- Comprehensive logging at each step
- Graceful failure handling

## Security

- OAuth 2.0 with least-privilege scopes
- Secure token storage and refresh
- Input sanitization and validation
- No hardcoded credentials

## Troubleshooting

### Common Issues

1. **OAuth Errors**: Ensure APIs are enabled and credentials are correct
2. **Permission Denied**: Check Gmail account has necessary permissions
3. **Token Expired**: Delete `token.json` to re-authenticate
4. **API Quotas**: Check Google Cloud Console for quota limits

### Logging

The agent provides detailed logging at INFO level. Enable DEBUG for more verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Testing

```bash
# Run example with validation tests
python example_usage.py

# Manual testing
python main.py --interactive
```

### Project Structure

```
adopt/
├── adopt/
│   ├── __init__.py
│   ├── agent.py          # LangGraph workflow
│   └── tools.py          # Google API tools
├── main.py               # CLI interface
├── example_usage.py      # Usage examples
├── requirements.txt      # Dependencies
└── README.md            # This file
```
