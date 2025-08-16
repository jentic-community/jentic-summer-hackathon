#!/usr/bin/env python3
"""
Setup script for Track 04 - Agent Communications (Slack/Email)
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_standard_agent():
    """Install the Standard Agent from the local path."""
    standard_agent_path = Path(__file__).parent.parent / "standard-agent"
    
    if not standard_agent_path.exists():
        print("❌ Standard Agent not found at expected location")
        print(f"Expected path: {standard_agent_path}")
        print("Please ensure you're running this from the correct directory")
        return False
    
    # Install in development mode
    return run_command(
        f"pip install -e {standard_agent_path}",
        "Installing Standard Agent"
    )

def install_dependencies():
    """Install required dependencies."""
    return run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    env_content = """# Slack Configuration
# Get these from your Slack app settings at https://api.slack.com/apps
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_DEFAULT_CHANNEL=C1234567890  # Optional: for testing

# Standard Agent Configuration
# Required for the AI agent to work
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Additional tools and customization
JENTIC_API_KEY=your-jentic-api-key-here  # Optional: for additional tools
LLM_MODEL=claude-3-sonnet-20240229  # Optional: defaults to this model

# Alternative LLM providers (use one of these instead of ANTHROPIC_API_KEY)
# OPENAI_API_KEY=your-openai-api-key-here
# GOOGLE_API_KEY=your-google-api-key-here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("💡 Please edit .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Track 04 - Agent Communications (Slack/Email)")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install Standard Agent
    if not install_standard_agent():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Set up your Slack app (see README.md for instructions)")
    print("3. Test the setup: python demo.py test")
    print("4. Run the bot: python demo.py run")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
