import os
import sys
from dotenv import load_dotenv
from slack_agent import SlackAgent

def test_connection():
    """Test basic connection to Slack."""
    load_dotenv()
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app_token = os.getenv("SLACK_APP_TOKEN")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not set in environment")
        return False
        
    if not app_token:
        print("❌ SLACK_APP_TOKEN not set in environment")
        return False
    
    try:
        slack_agent = SlackAgent(bot_token, app_token)
        
        if slack_agent.test_connection():
            print("✅ Connected to Slack successfully")
            
            # Test Standard Agent integration
            if slack_agent.standard_agent:
                print("✅ Standard Agent is available")
                
                # Test a simple query
                test_query = "What is 2 + 2?"
                user_context = {'user_id': 'test_user', 'channel': 'test_channel'}
                response = slack_agent.process_agent_query(test_query, user_context)
                print(f"🤖 Test query: '{test_query}'")
                print(f"🤖 Response: {response}")
            else:
                print("❌ Standard Agent is not available")
                
            return True
        else:
            print("❌ Failed to connect to Slack")
            return False
            
    except Exception as e:
        print(f"❌ Error during connection test: {e}")
        return False

def list_channels():
    """List available Slack channels."""
    load_dotenv()
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return
        
    try:
        slack_agent = SlackAgent(bot_token)
        
        if slack_agent.test_connection():
            print("📋 Available channels:")
            try:
                channels = slack_agent.client.conversations_list(types="public_channel,private_channel")
                for channel in channels["channels"][:10]:  # Show first 10
                    print(f"  • {channel['name']} ({channel['id']}) - {'Private' if channel.get('is_private') else 'Public'}")
            except Exception as e:
                print(f"❌ Couldn't list channels: {e}")
        else:
            print("❌ Not connected to Slack")
            
    except Exception as e:
        print(f"❌ Error listing channels: {e}")

def send_test_message():
    """Send a test message to a channel."""
    load_dotenv()
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    channel_id = os.getenv("SLACK_DEFAULT_CHANNEL")
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not set")
        return
        
    if not channel_id:
        print("❌ SLACK_DEFAULT_CHANNEL not set")
        print("💡 Set SLACK_DEFAULT_CHANNEL in your .env file to test message sending")
        return
    
    try:
        slack_agent = SlackAgent(bot_token)
        
        if slack_agent.test_connection():
            print(f"📤 Sending test message to channel {channel_id}...")
            
            # Test basic message
            response = slack_agent.send_message(channel_id, "🤖 Hello! I'm your AI assistant. How can I help you today?")
            if response.get("ok"):
                print("✅ Test message sent successfully")
            else:
                print(f"❌ Failed to send message: {response}")
                
            # Test Standard Agent integration
            if slack_agent.standard_agent:
                test_query = "What's the weather like today?"
                user_context = {'user_id': 'demo_user', 'channel': channel_id}
                agent_response = slack_agent.process_agent_query(test_query, user_context)
                
                response = slack_agent.send_message(channel_id, f"🤖 Test query: '{test_query}'\n{agent_response}")
                if response.get("ok"):
                    print("✅ Agent response sent successfully")
                else:
                    print(f"❌ Failed to send agent response: {response}")
        else:
            print("❌ Not connected to Slack")
            
    except Exception as e:
        print(f"❌ Error sending test message: {e}")

def run_bot():
    """Run the full Slack bot."""
    print("🚀 Starting Slack bot...")
    print("💡 Press Ctrl+C to stop the bot")
    
    try:
        agent = SlackAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

def main():
    """Main demo function."""
    print("🤖 Slack Agent Demo")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_connection()
        elif command == "channels":
            list_channels()
        elif command == "send":
            send_test_message()
        elif command == "run":
            run_bot()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        print_help()

def print_help():
    """Print help information."""
    print("\n📖 Available commands:")
    print("  python demo.py test     - Test connection and Standard Agent")
    print("  python demo.py channels - List available Slack channels")
    print("  python demo.py send     - Send a test message")
    print("  python demo.py run      - Run the full bot")
    print("\n💡 Make sure to set up your .env file with:")
    print("  - SLACK_BOT_TOKEN")
    print("  - SLACK_APP_TOKEN")
    print("  - SLACK_DEFAULT_CHANNEL (for testing)")
    print("  - LLM_MODEL (optional, defaults to claude-3-sonnet-20240229)")

if __name__ == "__main__":
    main()
