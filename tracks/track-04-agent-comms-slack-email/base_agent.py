#!/usr/bin/env python3
"""
Base Communication Agent Template

This is a starting template for building your communication agent.
Implement the methods below to create your own platform integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Standard Agent integration
try:
    from agents.prebuilt import ReWOOAgent
    STANDARD_AGENT_AVAILABLE = True
except ImportError:
    STANDARD_AGENT_AVAILABLE = False
    print("⚠️  Standard Agent not installed. See setup instructions.")

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCommunicationAgent(ABC):
    """
    Base class for communication agents.
    
    Implement this interface for your chosen platform (Slack, Email, SMS, etc.)
    """
    
    def __init__(self):
        """Initialize your communication agent."""
        # Initialize Standard Agent if available
        self.agent = None
        if STANDARD_AGENT_AVAILABLE:
            try:
                model = os.getenv('LLM_MODEL', 'gpt-4')
                self.agent = ReWOOAgent(model=model)
                logger.info(f"✅ Standard Agent initialized with model: {model}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Standard Agent: {e}")
        
        # TODO: Initialize your platform-specific client here
        # Example:
        # self.client = YourPlatformClient(api_key=os.getenv('YOUR_API_KEY'))
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to your communication platform.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        # TODO: Implement connection test for your platform
        # Example:
        # try:
        #     response = self.client.test_auth()
        #     return response.get('ok', False)
        # except Exception as e:
        #     logger.error(f"Connection test failed: {e}")
        #     return False
        pass
    
    @abstractmethod
    def send_message(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message through your platform.
        
        Args:
            recipient: Platform-specific recipient identifier (channel, email, phone, etc.)
            message: Text message to send
            **kwargs: Platform-specific options (thread_id, priority, etc.)
        
        Returns:
            dict: Result with 'success' boolean and additional info
        """
        # TODO: Implement message sending for your platform
        # Example:
        # try:
        #     response = self.client.send_message(
        #         recipient=recipient,
        #         text=message,
        #         **kwargs
        #     )
        #     return {'success': True, 'message_id': response.get('id')}
        # except Exception as e:
        #     logger.error(f"Failed to send message: {e}")
        #     return {'success': False, 'error': str(e)}
        pass
    
    def process_agent_query(self, query: str, user_context: Optional[Dict] = None) -> str:
        """
        Process a query using Standard Agent.
        
        Args:
            query: User's question or request
            user_context: Optional context about the user/conversation
        
        Returns:
            str: Agent's response
        """
        if not self.agent:
            return "Sorry, the AI agent is not available right now."
        
        try:
            # TODO: You can enhance this with context management
            # For now, it's a simple query processing
            response = self.agent.solve(query)
            return response
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def format_message(self, message: str, message_type: str = "default") -> str:
        """
        Format message for your platform.
        
        Args:
            message: Raw message content
            message_type: Type of message (response, error, notification, etc.)
        
        Returns:
            str: Formatted message
        """
        # TODO: Implement platform-specific formatting
        # Examples:
        # - For Slack: Add emojis, format with markdown
        # - For Email: Add HTML formatting, subject line
        # - For SMS: Truncate to character limits
        
        # Basic implementation - you should enhance this
        if message_type == "error":
            return f"❌ {message}"
        elif message_type == "success":
            return f"✅ {message}"
        else:
            return message
    
    def handle_user_message(self, user_message: str, user_id: str, platform_context: Dict) -> Dict[str, Any]:
        """
        Handle incoming message from user.
        
        Args:
            user_message: Message text from user
            user_id: Platform-specific user identifier
            platform_context: Platform-specific context (channel, thread, etc.)
        
        Returns:
            dict: Response to send back to user
        """
        # TODO: Implement your message handling logic
        # This is where you'd:
        # 1. Parse the user message
        # 2. Determine if it needs agent processing
        # 3. Process with agent if needed
        # 4. Format response appropriately
        # 5. Send response back to user
        
        # Basic example implementation:
        try:
            # Process query with agent
            agent_response = self.process_agent_query(user_message)
            
            # Format response
            formatted_response = self.format_message(agent_response, "response")
            
            # Send response (you'll need to adapt recipient format)
            result = self.send_message(
                recipient=platform_context.get('channel', user_id),
                message=formatted_response
            )
            
            return {
                'success': result.get('success', False),
                'response_sent': formatted_response,
                'original_query': user_message
            }
            
        except Exception as e:
            error_message = self.format_message(
                f"Sorry, I encountered an error: {str(e)}", 
                "error"
            )
            return {
                'success': False,
                'error': str(e),
                'error_message_sent': error_message
            }

# Example implementation starter for Slack
class SlackAgent(BaseCommunicationAgent):
    """
    Slack communication agent implementation.
    
    TODO: Complete this implementation for Slack integration.
    """
    
    def __init__(self):
        super().__init__()
        
        # TODO: Initialize Slack client
        # Hint: Use slack-sdk library
        # self.slack_client = slack_sdk.WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        
        # TODO: Set up event handlers if using real-time events
        pass
    
    def test_connection(self) -> bool:
        """Test Slack connection."""
        # TODO: Implement Slack auth test
        # Hint: Use self.slack_client.auth_test()
        return False  # Replace with actual implementation
    
    def send_message(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send message to Slack channel or user."""
        # TODO: Implement Slack message sending
        # Hint: Use self.slack_client.chat_postMessage()
        return {'success': False, 'error': 'Not implemented'}
    
    def format_message(self, message: str, message_type: str = "default") -> str:
        """Format message for Slack (with emojis, markdown, etc.)"""
        # TODO: Add Slack-specific formatting
        # Hint: Slack supports markdown-like formatting
        if message_type == "error":
            return f"🚨 *Error:* {message}"
        elif message_type == "response":
            return f"🤖 {message}"
        return message

# Example implementation starter for Email
class EmailAgent(BaseCommunicationAgent):
    """
    Email communication agent implementation.
    
    TODO: Complete this implementation for email integration.
    """
    
    def __init__(self):
        super().__init__()
        
        # TODO: Initialize email client (SendGrid, SMTP, etc.)
        # Example for SendGrid:
        # import sendgrid
        # self.sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        pass
    
    def test_connection(self) -> bool:
        """Test email service connection."""
        # TODO: Implement email service test
        return False  # Replace with actual implementation
    
    def send_message(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send email message."""
        # TODO: Implement email sending
        # Consider both HTML and plain text versions
        subject = kwargs.get('subject', 'Message from AI Agent')
        return {'success': False, 'error': 'Not implemented'}
    
    def format_message(self, message: str, message_type: str = "default") -> str:
        """Format message for email (HTML, plain text, etc.)"""
        # TODO: Add email-specific formatting
        # Consider HTML templates for rich formatting
        return message

# Example implementation starter for SMS
class SMSAgent(BaseCommunicationAgent):
    """
    SMS communication agent implementation.
    
    TODO: Complete this implementation for SMS integration.
    """
    
    def __init__(self):
        super().__init__()
        
        # TODO: Initialize SMS client (Twilio, etc.)
        # Example for Twilio:
        # from twilio.rest import Client
        # self.twilio = Client(
        #     os.getenv('TWILIO_ACCOUNT_SID'),
        #     os.getenv('TWILIO_AUTH_TOKEN')
        # )
        pass
    
    def test_connection(self) -> bool:
        """Test SMS service connection."""
        # TODO: Implement SMS service test
        return False  # Replace with actual implementation
    
    def send_message(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS message."""
        # TODO: Implement SMS sending
        # Remember: SMS has character limits (usually 160)
        if len(message) > 160:
            message = message[:157] + "..."
        
        return {'success': False, 'error': 'Not implemented'}
    
    def format_message(self, message: str, message_type: str = "default") -> str:
        """Format message for SMS (short, clear, no special formatting)"""
        # TODO: SMS-specific formatting (very limited)
        # Keep it simple - no emojis, markdown, etc.
        return message

# Factory function to help users get started
def create_agent(platform: str) -> BaseCommunicationAgent:
    """
    Factory function to create agents for different platforms.
    
    Args:
        platform: Platform name ('slack', 'email', 'sms')
    
    Returns:
        BaseCommunicationAgent: Configured agent for the platform
    """
    platform = platform.lower()
    
    if platform == 'slack':
        return SlackAgent()
    elif platform == 'email':
        return EmailAgent()
    elif platform == 'sms':
        return SMSAgent()
    else:
        raise ValueError(f"Unsupported platform: {platform}. Choose from: slack, email, sms")

# Example usage for participants
if __name__ == "__main__":
    print("🚀 Communication Agent Template")
    print("This is a starting template for your implementation.")
    print("\n📋 To get started:")
    print("1. Choose a platform (slack, email, or sms)")
    print("2. Implement the TODO methods in the corresponding class")
    print("3. Test your implementation with test_integration.py")
    print("4. Build your custom features on top of the base functionality")
    print("\n💡 Example:")
    print("   agent = create_agent('slack')")
    print("   # Implement the methods, then:")
    print("   agent.send_message('#general', 'Hello from my agent!')")