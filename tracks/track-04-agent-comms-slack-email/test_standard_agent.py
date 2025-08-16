#!/usr/bin/env python3
"""
Test script for Standard Agent integration
"""

import os
import sys
from dotenv import load_dotenv

# Add the standard agent to the path
STANDARD_AGENT_PATH = os.path.join(os.path.dirname(__file__), "..", "standard-agent")
if STANDARD_AGENT_PATH not in sys.path:
    sys.path.insert(0, STANDARD_AGENT_PATH)

def test_standard_agent_import():
    """Test if we can import the Standard Agent."""
    try:
        from agents.prebuilt import ReWOOAgent
        print("✅ Successfully imported ReWOOAgent")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ReWOOAgent: {e}")
        return False

def test_standard_agent_initialization():
    """Test if we can initialize the Standard Agent."""
    try:
        from agents.prebuilt import ReWOOAgent
        
        # Check if we have the required API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not set in environment")
            print("💡 Please set your Anthropic API key in the .env file")
            return False
        
        # Try to initialize the agent
        agent = ReWOOAgent(model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"))
        print("✅ Successfully initialized ReWOOAgent")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize ReWOOAgent: {e}")
        return False

def test_standard_agent_query():
    """Test if the Standard Agent can process a simple query."""
    try:
        from agents.prebuilt import ReWOOAgent
        
        agent = ReWOOAgent(model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"))
        
        # Test a simple query
        test_query = "What is 2 + 2?"
        print(f"🤖 Testing query: '{test_query}'")
        
        result = agent.solve(test_query)
        
        print(f"✅ Query processed successfully")
        print(f"🤖 Response: {result.final_answer}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to process query: {e}")
        return False

def test_slack_agent_integration():
    """Test the Slack Agent integration with Standard Agent."""
    try:
        from slack_agent import SlackAgent
        
        # Test without tokens (should fail gracefully)
        try:
            agent = SlackAgent()
            print("❌ Should have failed without tokens")
            return False
        except ValueError as e:
            if "SLACK_BOT_TOKEN" in str(e):
                print("✅ Slack Agent correctly requires tokens")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test Slack Agent integration: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Standard Agent Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        ("Import Test", test_standard_agent_import),
        ("Initialization Test", test_standard_agent_initialization),
        ("Query Test", test_standard_agent_query),
        ("Slack Agent Integration Test", test_slack_agent_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Standard Agent integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
