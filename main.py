#!/usr/bin/env python3
"""
Main script to run the submission processing agent.

Usage:
    python main.py --name "John Doe" --email "john@example.com" --address "123 Main St, City, State"
    
Or run interactively:
    python main.py
"""

import argparse
import sys
from adopt.agent import create_agent


def main():
    parser = argparse.ArgumentParser(description='Process user submission and create Google Doc with email')
    parser.add_argument('--name', help='User full name')
    parser.add_argument('--email', help='User email address')
    parser.add_argument('--address', help='User address')
    parser.add_argument('--recipient', help='Recipient email address')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Get user input
    if args.interactive or not all([args.name, args.email, args.address, args.recipient]):
        print("=== User Submission Processor ===")
        print("Please provide the following information:\n")
        
        name = input("Full Name: ").strip()
        email = input("Email Address: ").strip()
        address = input("Address: ").strip()
        recipient_email = input("Recipient Email: ").strip()
        
        if not all([name, email, address, recipient_email]):
            print("Error: All fields are required.")
            sys.exit(1)
    else:
        name = args.name
        email = args.email
        address = args.address
        recipient_email = args.recipient
    
    print(f"\nProcessing submission for: {name}")
    print("=" * 50)
    
    try:
        # Create and run the agent
        agent = create_agent()
        result = agent.process_submission(name, email, address, recipient_email)
        
        # Display results
        if result["success"]:
            print("✅ Submission processed successfully!")
            print(f"\nDocument created: {result['document_url']}")
            print(f"Email sent with message ID: {result['email_message_id']}")
        else:
            print("❌ Submission processing failed!")
            print(f"Error: {result['message']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
