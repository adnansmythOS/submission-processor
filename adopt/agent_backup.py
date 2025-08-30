import os
import logging
from typing import Dict, Any, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage

from .tools import GoogleAPIManager, CreateGoogleDocTool, ExportDocxTool, SendEmailTool, UserSubmission

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State schema for the LangGraph workflow."""
    # Input data
    user_input: Dict[str, Any]
    
    # Processing results
    validation_result: Dict[str, Any]
    doc_creation_result: Dict[str, Any]
    docx_export_result: Dict[str, Any]
    email_result: Dict[str, Any]
    
    # Error handling
    error_message: str
    retry_count: int
    
    # Final status
    success: bool
    final_message: str


class SubmissionAgent:
    """LangGraph agent for processing user submissions."""
    
    def __init__(self):
        # Load configuration from environment
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        self.recipient_email = os.getenv('FIXED_RECIPIENT_EMAIL')
        self.drive_folder_id = os.getenv('DRIVE_FOLDER_ID')
        
        # Validate configuration
        if not all([self.client_id, self.client_secret, self.recipient_email]):
            raise ValueError("Missing required environment variables: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FIXED_RECIPIENT_EMAIL")
        
        # Initialize Google API manager and tools
        self.api_manager = GoogleAPIManager(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_path=self.token_path
        )
        
        self.doc_tool = CreateGoogleDocTool(self.api_manager, self.drive_folder_id)
        self.export_tool = ExportDocxTool(self.api_manager)
        self.email_tool = SendEmailTool(self.api_manager, self.recipient_email)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("create_document", self._create_document)
        workflow.add_node("export_docx", self._export_docx)
        workflow.add_node("send_email", self._send_email)
        workflow.add_node("handle_error", self._handle_error)
        workflow.add_node("finalize", self._finalize)
        
        # Define edges
        workflow.set_entry_point("validate_input")
        
        workflow.add_conditional_edges(
            "validate_input",
            self._should_continue_after_validation,
            {
                "continue": "create_document",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "create_document",
            self._should_continue_after_doc_creation,
            {
                "continue": "export_docx",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "export_docx",
            self._should_continue_after_export,
            {
                "continue": "send_email",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "send_email",
            self._should_continue_after_email,
            {
                "continue": "finalize",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("handle_error", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _validate_input(self, state: AgentState) -> AgentState:
        """Validate user input data."""
        logger.info("Validating user input...")
        
        try:
            # Validate using Pydantic model
            submission = UserSubmission(**state["user_input"])
            
            state["validation_result"] = {
                "success": True,
                "validated_data": submission.dict()
            }
            logger.info(f"Input validation successful for user: {submission.name}")
            
        except Exception as e:
            state["validation_result"] = {
                "success": False,
                "error": str(e)
            }
            state["error_message"] = f"Input validation failed: {str(e)}"
            logger.error(f"Input validation failed: {str(e)}")
        
        return state
    
    def _create_document(self, state: AgentState) -> AgentState:
        """Create Google Doc with submission data."""
        logger.info("Creating Google Doc...")
        
        try:
            validated_data = state["validation_result"]["validated_data"]
            result = self.doc_tool._run(validated_data)
            
            state["doc_creation_result"] = result
            
            if result["success"]:
                logger.info(f"Document created successfully: {result['document_id']}")
            else:
                state["error_message"] = f"Document creation failed: {result.get('error', 'Unknown error')}"
                logger.error(state["error_message"])
                
        except Exception as e:
            state["doc_creation_result"] = {"success": False, "error": str(e)}
            state["error_message"] = f"Document creation failed: {str(e)}"
            logger.error(state["error_message"])
        
        return state
    
    def _export_docx(self, state: AgentState) -> AgentState:
        """Export Google Doc as DOCX."""
        logger.info("Exporting document as DOCX...")
        
        try:
            document_id = state["doc_creation_result"]["document_id"]
            result = self.export_tool._run(document_id)
            
            state["docx_export_result"] = result
            
            if result["success"]:
                logger.info("DOCX export successful")
            else:
                state["error_message"] = f"DOCX export failed: {result.get('error', 'Unknown error')}"
                logger.error(state["error_message"])
                
        except Exception as e:
            state["docx_export_result"] = {"success": False, "error": str(e)}
            state["error_message"] = f"DOCX export failed: {str(e)}"
            logger.error(state["error_message"])
        
        return state
    
    def _send_email(self, state: AgentState) -> AgentState:
        """Send email with DOCX attachment."""
        logger.info("Sending email with attachment...")
        
        try:
            docx_content = state["docx_export_result"]["docx_content"]
            doc_title = state["doc_creation_result"]["title"]
            doc_url = state["doc_creation_result"]["document_url"]
            submission_name = state["validation_result"]["validated_data"]["name"]
            
            result = self.email_tool._run(
                docx_content=docx_content,
                document_title=doc_title,
                document_url=doc_url,
                submission_name=submission_name
            )
            
            state["email_result"] = result
            
            if result["success"]:
                logger.info(f"Email sent successfully: {result['message_id']}")
            else:
                state["error_message"] = f"Email sending failed: {result.get('error', 'Unknown error')}"
                logger.error(state["error_message"])
                
        except Exception as e:
            state["email_result"] = {"success": False, "error": str(e)}
            state["error_message"] = f"Email sending failed: {str(e)}"
            logger.error(state["error_message"])
        
        return state
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors and determine retry logic."""
        logger.error(f"Handling error: {state.get('error_message', 'Unknown error')}")
        
        retry_count = state.get("retry_count", 0)
        
        # Simple retry logic - could be enhanced with exponential backoff
        if retry_count < 3:
            state["retry_count"] = retry_count + 1
            logger.info(f"Retry attempt {retry_count + 1}")
            # In a more sophisticated implementation, you could retry specific steps
        
        state["success"] = False
        return state
    
    def _finalize(self, state: AgentState) -> AgentState:
        """Finalize the workflow and prepare final message."""
        # Check if all steps completed successfully
        validation_success = state.get("validation_result", {}).get("success", False)
        doc_success = state.get("doc_creation_result", {}).get("success", False)
        export_success = state.get("docx_export_result", {}).get("success", False)
        email_success = state.get("email_result", {}).get("success", False)
        
        if all([validation_success, doc_success, export_success, email_success]):
            state["success"] = True
            doc_id = state["doc_creation_result"]["document_id"]
            message_id = state["email_result"]["message_id"]
            recipient = state["email_result"]["recipient"]
            
            state["final_message"] = f"""Submission processed successfully!
            
Document ID: {doc_id}
Document URL: {state["doc_creation_result"]["document_url"]}
Email sent to: {recipient}
Gmail Message ID: {message_id}"""
            
            logger.info("Workflow completed successfully")
        else:
            state["success"] = False
            error_msg = state.get('error_message', 'Unknown error')
            state["final_message"] = f"Workflow failed: {error_msg}"
            logger.error(f"Workflow failed in finalize: {error_msg}")
        
        return state
    
    # Conditional edge functions
    def _should_continue_after_validation(self, state: AgentState) -> str:
        return "continue" if state["validation_result"]["success"] else "error"
    
    def _should_continue_after_doc_creation(self, state: AgentState) -> str:
        return "continue" if state["doc_creation_result"]["success"] else "error"
    
    def _should_continue_after_export(self, state: AgentState) -> str:
        return "continue" if state["docx_export_result"]["success"] else "error"
    
    def _should_continue_after_email(self, state: AgentState) -> str:
        return "continue" if state["email_result"]["success"] else "error"
    
    def process_submission(self, name: str, email: str, address: str) -> Dict[str, Any]:
        """Process a user submission through the complete workflow."""
        logger.info(f"Processing submission for: {name}")
        
        # Initialize state
        initial_state = AgentState(
            user_input={
                "name": name,
                "email": email,
                "address": address
            },
            validation_result={},
            doc_creation_result={},
            docx_export_result={},
            email_result={},
            error_message="",
            retry_count=0,
            success=False,
            final_message=""
        )
        
        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            return {
                "success": final_state["success"],
                "message": final_state["final_message"],
                "document_id": final_state.get("doc_creation_result", {}).get("document_id"),
                "document_url": final_state.get("doc_creation_result", {}).get("document_url"),
                "email_message_id": final_state.get("email_result", {}).get("message_id")
            }
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "message": f"Workflow execution failed: {str(e)}",
                "document_id": None,
                "document_url": None,
                "email_message_id": None
            }


def create_agent() -> SubmissionAgent:
    """Factory function to create a configured SubmissionAgent."""
    return SubmissionAgent()
