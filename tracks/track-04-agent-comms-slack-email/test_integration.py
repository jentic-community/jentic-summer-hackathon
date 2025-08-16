#!/usr/bin/env python3
"""
Integration Test Framework for Track 04

Use this to test your communication agent implementation.
"""

import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import the base agent and your implementations
from integrations.base_agent import BaseCommunicationAgent, create_agent

load_dotenv()

class AgentTester:
    """Test framework for communication agents."""
    
    def __init__(self, platform: str):
        """Initialize tester for specific platform."""
        self.platform = platform
        self.agent = None
        self.test_results = []
        
        try:
            self.agent = create_agent(platform)
            print(f"✅ Created {platform} agent for testing")
        except Exception as e:
            print(f"❌ Failed to create {platform} agent: {e}")
            sys.exit(1)
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        try:
            result = test_func(*args, **kwargs)
            if result:
                print(f"   ✅ PASS: {test_name}")
                self.test_results.append({'test': test_name, 'status': 'PASS'})
                return True
            else:
                print(f"   ❌ FAIL: {test_name}")
                self.test_results.append({'test': test_name, 'status': 'FAIL'})
                return False
        except Exception as e:
            print(f"   💥 ERROR: {test_name} - {str(e)}")
            self.test_results.append({'test': test_name, 'status': 'ERROR', 'error': str(e)})
            return False
    
    def test_environment_setup(self) -> bool:
        """Test that required environment variables are set."""
        required_vars = ['JENTIC_AGENT_API_KEY']
        
        # Platform-specific requirements
        platform_vars = {
            'slack': ['SLACK_BOT_TOKEN'],
            'email': ['SENDGRID_API_KEY', 'SMTP_HOST'],  # Either one is OK
            'sms': ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']
        }
        
        # Check basic requirements
        missing_basic = [var for var in required_vars if not os.getenv(var)]
        if missing_basic:
            print(f"   Missing basic environment variables: {missing_basic}")
            return False
        
        # Check platform-specific requirements
        if self.platform in platform_vars:
            platform_required = platform_vars[self.platform]
            if self.platform == 'email':
                # For email, either SendGrid OR SMTP is acceptable
                has_sendgrid = bool(os.getenv('SENDGRID_API_KEY'))
                has_smtp = all(os.getenv(var) for var in ['SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD'])
                if not (has_sendgrid or has_smtp):
                    print(f"   Missing email configuration: Need either SENDGRID_API_KEY or SMTP credentials")
                    return False
            else:
                missing_platform = [var for var in platform_required if not os.getenv(var)]
                if missing_platform:
                    print(f"   Missing {self.platform} environment variables: {missing_platform}")
                    return False
        
        print(f"   All required environment variables are set")
        return True
    
    def test_agent_initialization(self) -> bool:
        """Test that the agent initializes without errors."""
        if not self.agent:
            print("   Agent not initialized")
            return False
        
        # Check if Standard Agent is available
        if hasattr(self.agent, 'agent') and self.agent.agent:
            print("   Standard Agent integration: ✅")
        else:
            print("   Standard Agent integration: ❌ (but this might be OK for testing)")
        
        return True
    
    def test_connection(self) -> bool:
        """Test platform connection."""
        try:
            result = self.agent.test_connection()
            if result:
                print("   Platform connection successful")
                return True
            else:
                print("   Platform connection failed - check your credentials")
                return False
        except NotImplementedError:
            print("   test_connection() not implemented yet - implement this method!")
            return False
        except Exception as e:
            print(f"   Connection test error: {e}")
            return False
    
    def test_message_formatting(self) -> bool:
        """Test message formatting functionality."""
        test_cases = [
            ("Hello world", "default"),
            ("This is an error message", "error"),
            ("Operation completed successfully", "success")
        ]
        
        try:
            for message, msg_type in test_cases:
                formatted = self.agent.format_message(message, msg_type)
                if not formatted:
                    print(f"   Formatting failed for: {message}")
                    return False
                print(f"   Formatted '{msg_type}': {formatted[:50]}...")
            
            return True
        except NotImplementedError:
            print("   format_message() not implemented yet")
            return False
        except Exception as e:
            print(f"   Formatting test error: {e}")
            return False
    
    def test_agent_query_processing(self) -> bool:
        """Test Standard Agent query processing."""
        if not hasattr(self.agent, 'agent') or not self.agent.agent:
            print("   Standard Agent not available - skipping query test")
            return True  # Not a failure if agent isn't configured
        
        try:
            test_query = "What is 2 + 2?"
            response = self.agent.process_agent_query(test_query)
            
            if not response:
                print("   Agent returned empty response")
                return False
            
            if len(response) < 3:
                print("   Agent response too short - might indicate an error")
                return False
            
            print(f"   Agent response preview: {response[:100]}...")
            return True
            
        except Exception as e:
            print(f"   Agent query processing error: {e}")
            return False
    
    def test_send_message_interface(self) -> bool:
        """Test the send_message method interface (without actually sending)."""
        try:
            # Test with a fake recipient to check method signature
            # We expect this to fail with "not implemented" rather than crash
            result = self.agent.send_message("test-recipient", "test message")
            
            # Check that result is a dictionary
            if not isinstance(result, dict):
                print("   send_message should return a dictionary")
                return False
            
            # Check for expected keys
            if 'success' not in result:
                print("   send_message result should include 'success' key")
                return False
            
            print("   send_message interface looks correct")
            return True
            
        except NotImplementedError:
            print("   send_message() not implemented yet - implement this method!")
            return False
        except Exception as e:
            print(f"   send_message interface error: {e}")
            return False
    
    def test_user_message_handling(self) -> bool:
        """Test the user message handling workflow."""
        try:
            test_context = {
                'channel': 'test-channel',
                'user_id': 'test-user',
                'platform': self.platform
            }
            
            result = self.agent.handle_user_message(
                user_message="Hello, how are you?",
                user_id="test-user",
                platform_context=test_context
            )
            
            if not isinstance(result, dict):
                print("   handle_user_message should return a dictionary")
                return False
            
            print("   User message handling interface looks correct")
            return True
            
        except Exception as e:
            print(f"   User message handling error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary."""
        print(f"🚀 Testing {self.platform.upper()} Communication Agent")
        print("=" * 50)
        
        # Define test suite
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Agent Initialization", self.test_agent_initialization),
            ("Platform Connection", self.test_connection),
            ("Message Formatting", self.test_message_formatting),
            ("Agent Query Processing", self.test_agent_query_processing),
            ("Send Message Interface", self.test_send_message_interface),
            ("User Message Handling", self.test_user_message_handling)
        ]
        
        # Run tests
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # Generate summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary for {self.platform.upper()}")
        print(f"   Passed: {passed}/{total}")
        print(f"   Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 All tests passed! Your implementation is ready.")
        elif passed >= total * 0.7:
            print("✅ Most tests passed. Check failed tests and improve.")
        else:
            print("❌ Many tests failed. Review implementation and try again.")
        
        return {
            'platform': self.platform,
            'passed': passed,
            'total': total,
            'success_rate': (passed/total)*100,
            'results': self.test_results
        }

def test_platform_implementation(platform: str):
    """Test a specific platform implementation."""
    tester = AgentTester(platform)
    return tester.run_all_tests()

def interactive_test():
    """Interactive test runner."""
    print("🧪 Agent Communication Integration Tester")
    print("This tool helps you verify your implementation.")
    print()
    
    # Ask user which platform to test
    available_platforms = ['slack', 'email', 'sms']
    print("Available platforms:")
    for i, platform in enumerate(available_platforms, 1):
        print(f"  {i}. {platform.title()}")
    
    while True:
        try:
            choice = input("\nEnter platform number (1-3): ").strip()
            platform_index = int(choice) - 1
            if 0 <= platform_index < len(available_platforms):
                platform = available_platforms[platform_index]
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Run tests for chosen platform
    print(f"\n🎯 Testing {platform.title()} implementation...")
    results = test_platform_implementation(platform)
    
    # Provide guidance based on results
    print("\n💡 Next Steps:")
    if results['success_rate'] == 100:
        print("   Your implementation is working great!")
        print("   Consider adding these enhancements:")
        print("   - Rich message formatting")
        print("   - Conversation context management")
        print("   - Error recovery mechanisms")
        print("   - User experience improvements")
    elif results['success_rate'] >= 70:
        print("   Your implementation is mostly working.")
        print("   Focus on fixing the failed tests:")
        failed_tests = [r['test'] for r in results['results'] if r['status'] != 'PASS']
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("   Your implementation needs more work.")
        print("   Start with these essential components:")
        print("   - Complete the test_connection() method")
        print("   - Implement send_message() method")
        print("   - Verify environment variables are set correctly")
    
    return results

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        # Platform specified as command line argument
        platform = sys.argv[1].lower()
        if platform in ['slack', 'email', 'sms']:
            test_platform_implementation(platform)
        else:
            print(f"Unknown platform: {platform}")
            print("Supported platforms: slack, email, sms")
    else:
        # Interactive mode
        interactive_test()

if __name__ == "__main__":
    main()