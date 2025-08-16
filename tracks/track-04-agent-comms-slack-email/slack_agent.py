import os
import sys
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

# Add the standard agent to the path
STANDARD_AGENT_PATH = os.path.join(os.path.dirname(__file__), "..", "standard-agent")
if STANDARD_AGENT_PATH not in sys.path:
    sys.path.insert(0, STANDARD_AGENT_PATH)

from agents.prebuilt import ReWOOAgent
from base_agent import BaseCommunicationAgent

load_dotenv()


class SlackAgent(BaseCommunicationAgent):
    def __init__(self, bot_token: Optional[str] = None, app_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.app_token = app_token or os.getenv("SLACK_APP_TOKEN")
        
        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN not set")
        if not self.app_token:
            raise ValueError("SLACK_APP_TOKEN not set")
            
        self.client = WebClient(token=self.bot_token)
        self.socket_client = None
        
        # Initialize Standard Agent
        try:
            self.standard_agent = ReWOOAgent(model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"))
            print("✅ Standard Agent initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Standard Agent: {e}")
            self.standard_agent = None
            
        # Conversation context storage
        self.conversation_contexts: Dict[str, Dict[str, Any]] = {}

    def test_connection(self) -> bool:
        try:
            resp = self.client.auth_test()
            return bool(resp.get("ok"))
        except SlackApiError as e:
            print(f"Slack auth failed: {e.response['error']}")
            return False

    def send_message(self, recipient: str, message: str) -> dict:
        try:
            # Format message for Slack
            formatted_message = self._format_message_for_slack(message)
            resp = self.client.chat_postMessage(
                channel=recipient, 
                text=formatted_message,
                unfurl_links=False,
                unfurl_media=False
            )
            return resp.data
        except SlackApiError as e:
            print(f"Send failed: {e.response['error']}")
            return {"ok": False, "error": e.response["error"]}

    def process_agent_query(self, query: str, user_context: dict) -> str:
        """Process query with Standard Agent."""
        if not self.standard_agent:
            return "❌ Standard Agent is not available. Please check your configuration."
            
        try:
            # Get or create conversation context
            user_id = user_context.get('user_id', 'unknown')
            if user_id not in self.conversation_contexts:
                self.conversation_contexts[user_id] = {
                    'conversation_history': [],
                    'last_interaction': datetime.now()
                }
            
            # Process with Standard Agent
            result = self.standard_agent.solve(query)
            
            # Update conversation context
            self.conversation_contexts[user_id]['conversation_history'].append({
                'query': query,
                'response': result.final_answer,
                'timestamp': datetime.now()
            })
            self.conversation_contexts[user_id]['last_interaction'] = datetime.now()
            
            # Keep only last 10 interactions to manage memory
            if len(self.conversation_contexts[user_id]['conversation_history']) > 10:
                self.conversation_contexts[user_id]['conversation_history'] = \
                    self.conversation_contexts[user_id]['conversation_history'][-10:]
            
            return result.final_answer
                
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"❌ Sorry, I encountered an error processing your query: {str(e)}"

    def _format_message_for_slack(self, message: str) -> str:
        """Format message appropriately for Slack."""
        # Truncate if too long (Slack has limits)
        if len(message) > 3000:
            message = message[:2997] + "..."
        
        # Add some basic formatting
        lines = message.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip().startswith('•') or line.strip().startswith('-'):
                formatted_lines.append(line)  # Keep bullet points
            elif line.strip().startswith('#'):
                formatted_lines.append(f"*{line.strip('#').strip()}*")  # Bold headers
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    async def start_socket_mode(self):
        """Start the Socket Mode client to handle events."""
        if not self.app_token:
            print("❌ SLACK_APP_TOKEN not set. Cannot start Socket Mode.")
            return
            
        self.socket_client = SocketModeClient(
            app_token=self.app_token,
            web_client=self.client
        )
        
        @self.socket_client.on("message")
        async def handle_message(client: SocketModeClient, req: SocketModeRequest):
            await self._handle_slack_event(req)
        
        print("🚀 Starting Slack bot in Socket Mode...")
        await self.socket_client.start()

    async def _handle_slack_event(self, req: SocketModeRequest):
        """Handle incoming Slack events."""
        try:
            event = req.payload.get("event", {})
            event_type = event.get("type")
            
            if event_type == "app_mention":
                await self._handle_app_mention(event)
            elif event_type == "message" and event.get("channel_type") == "im":
                await self._handle_direct_message(event)
                
        except Exception as e:
            print(f"Error handling Slack event: {e}")

    async def _handle_app_mention(self, event: dict):
        """Handle when the bot is mentioned in a channel."""
        channel = event.get("channel")
        user = event.get("user")
        text = event.get("text", "")
        
        # Remove the bot mention from the text
        # Format: <@BOT_ID> message
        bot_mention = f"<@{self.client.auth_test()['user_id']}>"
        query = text.replace(bot_mention, "").strip()
        
        if not query:
            response = "👋 Hi! I'm your AI assistant. How can I help you today?"
        else:
            user_context = {
                'user_id': user,
                'channel': channel,
                'event_type': 'mention'
            }
            response = self.process_agent_query(query, user_context)
        
        self.send_message(channel, response)

    async def _handle_direct_message(self, event: dict):
        """Handle direct messages to the bot."""
        channel = event.get("channel")
        user = event.get("user")
        text = event.get("text", "")
        
        # Ignore bot's own messages
        if event.get("bot_id"):
            return
            
        user_context = {
            'user_id': user,
            'channel': channel,
            'event_type': 'dm'
        }
        
        response = self.process_agent_query(text, user_context)
        self.send_message(channel, response)

    def run(self):
        """Run the Slack bot."""
        print("🤖 Starting Slack Agent...")
        
        if not self.test_connection():
            print("❌ Failed to connect to Slack")
            return
            
        print("✅ Connected to Slack successfully")
        
        # Start the async event loop
        try:
            asyncio.run(self.start_socket_mode())
        except KeyboardInterrupt:
            print("\n🛑 Stopping Slack bot...")
            if self.socket_client:
                asyncio.run(self.socket_client.stop())
        except Exception as e:
            print(f"❌ Error running Slack bot: {e}")


def main():
    """Main entry point for the Slack bot."""
    try:
        agent = SlackAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Failed to start Slack Agent: {e}")


if __name__ == "__main__":
    main()


