#!/usr/bin/env python3
"""
Single prompt testing script for Track 06 - Standard Agent Prompts
Test individual prompts and see detailed execution results.
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

def test_single_prompt(prompt_text, timeout=120):
    """Test a single prompt and return detailed results."""
    print(f"🧪 Testing prompt: {prompt_text}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Import and initialize agent
        from agents.prebuilt import ReWOOAgent
        
        model = os.getenv('LLM_MODEL', 'gpt-4')
        agent = ReWOOAgent(model=model)
        
        print(f"🤖 Agent initialized with model: {model}")
        print(f"⏰ Starting execution (timeout: {timeout}s)...")
        print()
        
        # Execute prompt
        result = agent.solve(prompt_text)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Display results
        print("✅ EXECUTION SUCCESSFUL")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print()
        print("📋 RESULT:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        # Return structured results for potential logging
        return {
            'prompt': prompt_text,
            'success': True,
            'execution_time': execution_time,
            'result': result,
            'model': model,
            'timestamp': time.time()
        }
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to run: pip install -r requirements.txt")
        return {'prompt': prompt_text, 'success': False, 'error': str(e)}
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"❌ EXECUTION FAILED after {execution_time:.2f}s")
        print(f"Error: {e}")
        
        return {
            'prompt': prompt_text,
            'success': False,
            'execution_time': execution_time,
            'error': str(e),
            'model': model,
            'timestamp': time.time()
        }

def save_test_result(result, filename="test_results.json"):
    """Save test result to file for tracking."""
    try:
        # Load existing results
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        # Add new result
        results.append(result)
        
        # Save updated results
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Result saved to {filename}")
        
    except Exception as e:
        print(f"⚠️  Could not save result: {e}")

def main():
    """Main function to handle command line usage."""
    load_dotenv()
    
    if len(sys.argv) != 2:
        print("Usage: python test_prompt.py \"Your prompt here\"")
        print()
        print("Examples:")
        print("  python test_prompt.py \"What's the weather in San Francisco?\"")
        print("  python test_prompt.py \"Find the latest AI papers on Figshare\"")
        print("  python test_prompt.py \"Translate 'Hello world' to Spanish\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("🚀 Standard Agent Prompt Tester")
    print("=" * 60)
    print()
    
    # Test the prompt
    result = test_single_prompt(prompt)
    
    # Save result for tracking
    save_test_result(result)
    
    print()
    print("=" * 60)
    
    if result['success']:
        print("🎉 Test completed successfully!")
        print()
        print("💡 Tips for creating better prompts:")
        print("  - Be specific about what you want")
        print("  - Include format preferences (brief, detailed, etc.)")
        print("  - Test edge cases and error scenarios")
        print("  - Document your successful prompts")
    else:
        print("🔧 Test failed - see error details above")
        print()
        print("💡 Troubleshooting tips:")
        print("  - Check your environment variables with: python verify_setup.py")
        print("  - Try a simpler prompt first")
        print("  - Ensure you have credits/quota for your LLM provider")
        print("  - Join Discord #summer-hackathon for help")

if __name__ == "__main__":
    main()