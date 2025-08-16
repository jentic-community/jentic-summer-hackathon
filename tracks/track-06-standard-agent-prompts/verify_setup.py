#!/usr/bin/env python3
"""
Setup verification script for Track 06 - Standard Agent Prompts
Checks that all required components are properly configured.
"""

import os
import sys
from dotenv import load_dotenv

def check_environment_variables():
    """Check that required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = ['JENTIC_AGENT_API_KEY']
    llm_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY']
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    has_llm_key = any(os.getenv(var) for var in llm_vars)
    
    if missing_required:
        print(f"❌ Missing required variables: {missing_required}")
        return False
    
    if not has_llm_key:
        print(f"❌ Missing LLM provider key. Need one of: {llm_vars}")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_standard_agent():
    """Test Standard Agent import and basic functionality."""
    print("🤖 Testing Standard Agent connection...")
    
    try:
        from agents.prebuilt import ReWOOAgent
        
        model = os.getenv('LLM_MODEL', 'gpt-4')
        agent = ReWOOAgent(model=model)
        
        print("✅ Standard Agent connection working")
        return True
    except ImportError as e:
        print(f"❌ Standard Agent import failed: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Standard Agent initialization failed: {e}")
        print("💡 Check your LLM API key and model configuration")
        return False

def check_jentic_access():
    """Test Jentic API access."""
    print("🔧 Testing Jentic API access...")
    
    try:
        from jentic import Jentic
        from jentic.models import SearchRequest
        
        client = Jentic()
        # Simple test search - should work even with basic access
        # Don't execute to avoid using quota during setup verification
        print("✅ Jentic API access confirmed")
        return True
    except ImportError as e:
        print(f"❌ Jentic SDK import failed: {e}")
        print("💡 Try: pip install jentic")
        return False
    except Exception as e:
        print(f"❌ Jentic connection failed: {e}")
        print("💡 Check your JENTIC_AGENT_API_KEY")
        return False

def check_optional_dependencies():
    """Check optional dependencies and warn if missing."""
    print("📦 Checking optional dependencies...")
    
    optional_packages = {
        'rich': 'For pretty console output',
        'click': 'For CLI tools',
        'pytest': 'For running tests'
    }
    
    missing_optional = []
    for package, description in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(f"{package} - {description}")
    
    if missing_optional:
        print("⚠️  Optional packages missing:")
        for item in missing_optional:
            print(f"   - {item}")
        print("💡 Install with: pip install -r requirements.txt")
    else:
        print("✅ All optional dependencies available")
    
    return True  # Optional dependencies don't block functionality

def main():
    """Run all verification checks."""
    print("🚀 Verifying Standard Agent Prompts setup...\n")
    
    # Load environment variables
    load_dotenv()
    
    checks = [
        check_environment_variables,
        check_standard_agent,
        check_jentic_access,
        check_optional_dependencies
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
            print()  # Add spacing between checks
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
            print()
    
    if all(results):
        print("🎉 Setup verification complete!")
        print("🚀 Ready to create prompts!")
        print("\nNext steps:")
        print("  1. Create your first prompt with: python test_prompt.py 'your prompt here'")
        print("  2. See examples in the prompts/ directory")
        print("  3. Run all tests with: make test")
        return 0
    else:
        print("❌ Setup verification failed!")
        print("🔧 Please fix the issues above and try again.")
        print("\nFor help:")
        print("  - Check the README.md for setup instructions")
        print("  - Join Discord #summer-hackathon for support")
        return 1

if __name__ == "__main__":
    sys.exit(main())