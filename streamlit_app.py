import streamlit as st
import os
from datetime import datetime
import traceback
from adopt.agent import create_agent

# Configure Streamlit page
st.set_page_config(
    page_title="Submission Processor",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dark theme will be applied via config.toml and CSS

# Custom CSS for better styling with dark theme support
st.markdown("""
<style>
    /* Force dark theme */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #58a6ff;
        margin-bottom: 30px;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
    }
    
    /* Success box - dark theme */
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #0d1117;
        border: 2px solid #238636;
        margin: 20px 0;
        color: #7dd3fc;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.2);
    }
    
    .success-box h3 {
        color: #3fb950;
        margin-top: 0;
    }
    
    .success-box a {
        color: #58a6ff !important;
        text-decoration: none;
        font-weight: bold;
    }
    
    .success-box a:hover {
        color: #79c0ff !important;
        text-decoration: underline;
    }
    
    /* Error box - dark theme */
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #0d1117;
        border: 2px solid #da3633;
        margin: 20px 0;
        color: #ffa198;
        box-shadow: 0 4px 12px rgba(218, 54, 51, 0.2);
    }
    
    .error-box h3 {
        color: #f85149;
        margin-top: 0;
    }
    
    /* Info box - dark theme */
    .info-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #0d1117;
        border: 2px solid #1f6feb;
        margin: 15px 0;
        color: #b1bac4;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.15);
    }
    
    .info-box h4 {
        color: #58a6ff;
        margin-top: 0;
    }
    
    .info-box ol {
        color: #e6edf3;
    }
    
    /* Button styling - enhanced for dark theme */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb 0%, #0969da 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0969da 0%, #0550ae 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(31, 111, 235, 0.4);
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        background-color: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
    }
    
    .stTextArea > div > div > textarea {
        background-color: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3);
    }
    
    /* Labels */
    .stTextInput > label, .stTextArea > label {
        color: #f0f6fc !important;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #161b22;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #238636;
    }
    
    /* Code blocks */
    code {
        background-color: #21262d !important;
        color: #79c0ff !important;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    }
    
    pre {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    
    /* Fix white sections */
    .element-container, .stMarkdown, .stText {
        color: #e6edf3 !important;
    }
    
    /* Ensure all text is visible */
    p, span, div {
        color: #e6edf3 !important;
    }
    
    /* Form container */
    .stForm {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Columns */
    .stColumns > div {
        background-color: transparent;
    }
    
    /* Additional fixes for white sections */
    .stApp > div:first-child {
        background-color: #0e1117 !important;
    }
    
    .main .block-container {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Fix any remaining white text issues */
    .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #e6edf3 !important;
    }
    
    /* Form section headers */
    .stForm h3 {
        color: #58a6ff !important;
        border-bottom: 2px solid #30363d;
        padding-bottom: 10px;
    }
    
    /* Help text */
    .stTextInput small, .stTextArea small {
        color: #8b949e !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    return missing_vars

def validate_email(email):
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Submission Processor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 18px;">Create Google Docs and send them via email automatically</p>', unsafe_allow_html=True)
    
    # Check environment setup
    missing_vars = check_environment()
    if missing_vars:
        st.markdown(f"""
        <div class="error-box">
            <h3>⚠️ Configuration Error</h3>
            <p>Missing required environment variables: <code>{', '.join(missing_vars)}</code></p>
            <p>Please set up your <code>.env</code> file with your Google OAuth credentials.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Information box
    st.markdown("""
    <div class="info-box">
        <h4>🔄 How it works:</h4>
        <ol>
            <li><strong>Fill out the form</strong> with submission details</li>
            <li><strong>Click Submit</strong> to process the submission</li>
            <li><strong>Google Doc is created</strong> with the information</li>
            <li><strong>Doc is exported</strong> to DOCX format</li>
            <li><strong>Email is sent</strong> to the recipient with the DOCX attachment</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Create form
    with st.form("submission_form", clear_on_submit=False):
        st.markdown("### 📝 Submission Details")
        
        # Input fields
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="Enter full name",
                help="The name of the person submitting"
            )
            
            email = st.text_input(
                "Email Address *",
                placeholder="user@example.com",
                help="Email address of the submitter"
            )
        
        with col2:
            recipient_email = st.text_input(
                "Recipient Email *",
                placeholder="admin@company.com",
                help="Email address to send the document to"
            )
            
            # Empty space for alignment
            st.write("")
        
        address = st.text_area(
            "Address *",
            placeholder="Enter full address",
            help="Complete address of the submitter",
            height=100
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Process Submission")
        
        if submitted:
            # Validation
            errors = []
            
            if not name or not name.strip():
                errors.append("Full Name is required")
            
            if not email or not email.strip():
                errors.append("Email Address is required")
            elif not validate_email(email.strip()):
                errors.append("Invalid email format for Email Address")
            
            if not recipient_email or not recipient_email.strip():
                errors.append("Recipient Email is required")
            elif not validate_email(recipient_email.strip()):
                errors.append("Invalid email format for Recipient Email")
            
            if not address or not address.strip():
                errors.append("Address is required")
            
            if errors:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Validation Errors:</h4>
                    <ul>
                        {''.join(f'<li>{error}</li>' for error in errors)}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Process submission
                process_submission(name.strip(), email.strip(), address.strip(), recipient_email.strip())

def process_submission(name, email, address, recipient_email):
    """Process the submission using the agent."""
    
    # Show processing message
    with st.spinner("🔄 Processing submission..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress
            status_text.text("🔧 Initializing agent...")
            progress_bar.progress(10)
            
            # Create agent
            agent = create_agent()
            
            # Update progress
            status_text.text("📝 Validating input...")
            progress_bar.progress(25)
            
            # Process submission
            status_text.text("📄 Creating Google Doc...")
            progress_bar.progress(50)
            
            result = agent.process_submission(name, email, address, recipient_email)
            
            # Update progress
            status_text.text("📧 Sending email...")
            progress_bar.progress(75)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if result["success"]:
                # Success message
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ Submission Processed Successfully!</h3>
                    <p><strong>Submitter:</strong> {name}</p>
                    <p><strong>Recipient:</strong> {recipient_email}</p>
                    <hr>
                    <p><strong>📄 Document Created:</strong></p>
                    <p><a href="{result['document_url']}" target="_blank" style="color: #1f77b4; text-decoration: none;">
                        🔗 View Google Doc
                    </a></p>
                    <p><strong>📧 Email Sent:</strong> Message ID <code>{result['email_message_id']}</code></p>
                    <p><em>The recipient will receive an email with the DOCX attachment.</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Success balloons
                st.balloons()
                
            else:
                # Error message
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ Submission Failed</h3>
                    <p><strong>Error:</strong> {result['message']}</p>
                    <p>Please try again or contact support if the issue persists.</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            # Handle unexpected errors
            progress_bar.empty()
            status_text.empty()
            
            error_details = str(e)
            
            st.markdown(f"""
            <div class="error-box">
                <h3>💥 Unexpected Error</h3>
                <p><strong>Error:</strong> {error_details}</p>
                <details>
                    <summary>Technical Details</summary>
                    <pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 12px;">
{traceback.format_exc()}
                    </pre>
                </details>
            </div>
            """, unsafe_allow_html=True)

# Sidebar with additional info
def show_sidebar():
    with st.sidebar:
        st.markdown("### 📋 About")
        st.markdown("""
        This app processes submissions by:
        1. Creating Google Docs
        2. Exporting to DOCX
        3. Sending via Gmail
        
        Built with:
        - 🤖 LangChain + LangGraph
        - 📄 Google Docs API
        - 📧 Gmail API
        - 🎨 Streamlit
        """)
        
        st.markdown("### ⚙️ Configuration")
        
        # Check token status
        token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        if os.path.exists(token_path):
            st.success("✅ OAuth token found")
        else:
            st.warning("⚠️ OAuth token not found")
        
        # Environment status
        env_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
        for var in env_vars:
            if os.getenv(var):
                st.success(f"✅ {var} configured")
            else:
                st.error(f"❌ {var} missing")
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - Data is processed securely
        - OAuth tokens are stored locally
        - No data is stored on servers
        """)

if __name__ == "__main__":
    show_sidebar()
    main()
