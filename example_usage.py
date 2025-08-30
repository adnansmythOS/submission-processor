#!/usr/bin/env python3
"""
Example usage of the submission processing agent.
"""

from adopt.agent import create_agent


def example_submission():
    """Example of processing a user submission."""
    
    # Example user data
    name = "Jane Smith"
    email = "jane.smith@example.com"
    address = "456 Oak Avenue, Springfield, IL 62701"
    recipient_email = "admin@company.com"
    
    print("=== Example Submission Processing ===")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Address: {address}")
    print(f"Recipient: {recipient_email}")
    print("\nProcessing...")
    
    try:
        # Create the agent
        agent = create_agent()
        
        # Process the submission
        result = agent.process_submission(name, email, address, recipient_email)
        
        # Display results
        if result["success"]:
            print("\n✅ SUCCESS!")
            print(result["message"])
            
            if result["document_url"]:
                print(f"\n📄 Document: {result['document_url']}")
            
            if result["email_message_id"]:
                print(f"📧 Email Message ID: {result['email_message_id']}")
                
        else:
            print("\n❌ FAILED!")
            print(result["message"])
            
    except Exception as e:
        print(f"\n💥 Error: {str(e)}")


def test_validation_errors():
    """Test various validation scenarios."""
    
    print("\n=== Testing Validation ===")
    
    test_cases = [
        {
            "name": "Test Invalid Email",
            "data": {"name": "John Doe", "email": "invalid-email", "address": "123 Main St", "recipient_email": "test@example.com"}
        },
        {
            "name": "Test Empty Name",
            "data": {"name": "", "email": "test@example.com", "address": "123 Main St", "recipient_email": "test@example.com"}
        },
        {
            "name": "Test Empty Address",
            "data": {"name": "John Doe", "email": "test@example.com", "address": "", "recipient_email": "test@example.com"}
        },
        {
            "name": "Test Invalid Recipient Email",
            "data": {"name": "John Doe", "email": "test@example.com", "address": "123 Main St", "recipient_email": "invalid-email"}
        }
    ]
    
    agent = create_agent()
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        data = test_case['data']
        
        try:
            result = agent.process_submission(
                name=data["name"],
                email=data["email"], 
                address=data["address"],
                recipient_email=data["recipient_email"]
            )
            
            if result["success"]:
                print("  ❌ Expected validation error but got success")
            else:
                print(f"  ✅ Validation failed as expected: {result['message']}")
                
        except Exception as e:
            print(f"  ✅ Exception caught as expected: {str(e)}")


if __name__ == "__main__":
    # Run example
    example_submission()
    
    # Test validation
    test_validation_errors()
    
    print("\n=== Example Complete ===")
    print("Note: Make sure to set up your .env file with the required credentials before running.")
