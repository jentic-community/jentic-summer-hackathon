import os
import sys
import asyncio

STANDARD_AGENT_PATH = os.path.join(os.path.dirname(__file__), 'standard-agent')
if STANDARD_AGENT_PATH not in sys.path:
    sys.path.insert(0, STANDARD_AGENT_PATH)

from config import get_config

def test_config():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Bot prefix: {config.bot_prefix}")
        print(f"   - LLM Model: {config.llm_model}")
        print(f"   - LLM Provider: {config.get_active_llm_provider()}")
        print(f"   - Log level: {config.log_level}")
        assert config is not None
        assert config.bot_prefix is not None
        assert config.llm_model is not None
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        assert False, f"Configuration loading failed: {e}"

def test_standard_agent_import():
    """Test Standard Agent import."""
    print("\n🤖 Testing Standard Agent import...")
    try:
        from agents.prebuilt import ReACTAgent
        print("✅ Standard Agent imported successfully")
        assert ReACTAgent is not None
    except Exception as e:
        print(f"❌ Standard Agent import failed: {e}")
        assert False, f"Standard Agent import failed: {e}"

def test_agent_initialization():
    """Test agent initialization."""
    print("\n🚀 Testing agent initialization...")
    try:
        from agents.prebuilt import ReACTAgent
        config = get_config()
        
        # Set environment variables that the Standard Agent expects
        os.environ['JENTIC_AGENT_API_KEY'] = config.jentic_agent_api_key
        os.environ['OPENAI_API_KEY'] = config.openai_api_key or ''
        os.environ['LLM_MODEL'] = config.llm_model
        
        # Create the agent
        agent = ReACTAgent(model=config.llm_model)
        print(f"✅ Agent initialized with model: {config.llm_model}")
        assert agent is not None
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        assert False, f"Agent initialization failed: {e}"

def test_discord_imports():
    """Test Discord.py imports."""
    print("\n💬 Testing Discord imports...")
    try:
        import discord
        from discord.ext import commands
        print("✅ Discord.py imported successfully")
        print(f"   - Discord.py version: {discord.__version__}")
        assert discord is not None
        assert commands is not None
    except Exception as e:
        print(f"❌ Discord import failed: {e}")
        assert False, f"Discord import failed: {e}"

def main():
    """Run all tests."""
    print("🧪 Running Discord Bot Integration Tests\n")
    
    tests = [
        test_config,
        test_discord_imports,
        test_standard_agent_import,
        test_agent_initialization,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to run.")
        print("\n📝 Next steps:")
        print("1. Go to https://discord.com/developers/applications/")
        print("2. Select your bot application")
        print("3. Go to 'Bot' section")
        print("4. Enable 'Message Content Intent' under 'Privileged Gateway Intents'")
        print("5. Save changes and run the bot again")
        print(f"\n🚀 Run the bot with: cd tracks/track-01-standard-agent-discord && rye run python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)