"""
Submission Processing Agent

A LangChain + LangGraph agent that processes user submissions by creating
Google Docs and sending them via email.
"""

from .agent import create_agent, SubmissionAgent
from .tools import GoogleAPIManager, UserSubmission

__version__ = "1.0.0"
__all__ = ["create_agent", "SubmissionAgent", "GoogleAPIManager", "UserSubmission"]
