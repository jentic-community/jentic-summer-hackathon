#!/usr/bin/env python3
"""
CLI Demo for the Agent Behavior Modification System.

This script provides an interactive command-line interface to demonstrate
the behavior modification system capabilities.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from behavior_modification import (
    BehaviorModifiedAgent,
    RuntimeBehaviorController,
    User,
    SecurityLevel,
)


class BehaviorModificationCLI:
    """Interactive CLI for demonstrating behavior modification."""
    
    def __init__(self):
        self.controller = RuntimeBehaviorController()
        self.agent = BehaviorModifiedAgent(
            llm=None,  # Placeholder
            tools=[],
            memory=None,
            reasoner=None,
            behavior_controller=self.controller
        )
        self.current_user = None
        self.running = True
    
    def run(self):
        """Run the interactive CLI."""
        print("🤖 Agent Behavior Modification System - CLI Demo")
        print("=" * 50)
        print("This demo shows how to dynamically modify agent behavior")
        print("using natural language commands.")
        print()
        
        self._setup_user()
        
        while self.running:
            self._show_menu()
            choice = input("\nEnter your choice: ").strip()
            self._handle_choice(choice)
    
    def _setup_user(self):
        """Set up the current user."""
        print("👤 User Setup")
        print("-" * 20)
        
        user_id = input("Enter user ID (or press Enter for 'demo_user'): ").strip()
        if not user_id:
            user_id = "demo_user"
        
        email = input("Enter email (or press Enter for 'demo@example.com'): ").strip()
        if not email:
            email = "demo@example.com"
        
        is_admin = input("Is this user an admin? (y/N): ").strip().lower() == 'y'
        
        self.current_user = User(
            id=user_id,
            email=email,
            name=f"Demo User {user_id}",
            role="admin" if is_admin else "user",
            is_admin=is_admin,
            permissions=["basic_access"] if not is_admin else ["basic_access", "policy_management"]
        )
        
        print(f"✅ User set up: {self.current_user.id} ({'Admin' if is_admin else 'User'})")
        print()
    
    def _show_menu(self):
        """Display the main menu."""
        print("\n📋 Main Menu")
        print("-" * 20)
        print("1. 📝 Test agent goal processing")
        print("2. 🔧 Modify agent behavior")
        print("3. 📊 View system status")
        print("4. 📋 View active policies")
        print("5. 📜 View audit log")
        print("6. 🧪 Run demo scenarios")
        print("7. 👤 Change user")
        print("8. ❌ Exit")
    
    def _handle_choice(self, choice: str):
        """Handle user menu choice."""
        if choice == "1":
            self._test_goal_processing()
        elif choice == "2":
            self._modify_behavior()
        elif choice == "3":
            self._view_status()
        elif choice == "4":
            self._view_policies()
        elif choice == "5":
            self._view_audit_log()
        elif choice == "6":
            self._run_demo_scenarios()
        elif choice == "7":
            self._change_user()
        elif choice == "8":
            self._exit()
        else:
            print("❌ Invalid choice. Please try again.")
    
    def _test_goal_processing(self):
        """Test agent goal processing."""
        print("\n🎯 Test Agent Goal Processing")
        print("-" * 30)
        
        goal = input("Enter a goal for the agent: ").strip()
        if not goal:
            print("❌ No goal entered.")
            return
        
        print(f"\n🤖 Processing goal: '{goal}'")
        print(f"👤 User: {self.current_user.id}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        result = self.agent.solve(goal, self.current_user)
        print(f"📤 Agent Response: {result}")
    
    def _modify_behavior(self):
        """Modify agent behavior using natural language."""
        print("\n🔧 Modify Agent Behavior")
        print("-" * 30)
        
        if not self.current_user.is_admin:
            print("❌ Only admin users can modify behavior.")
            return
        
        print("💡 Example modification requests:")
        print("  • 'Only work during business hours'")
        print("  • 'Block all email operations'")
        print("  • 'Don't process personal information'")
        print("  • 'Block user spam@example.com'")
        print("  • 'Only allow read operations'")
        print()
        
        modification = input("Enter behavior modification request: ").strip()
        if not modification:
            print("❌ No modification request entered.")
            return
        
        print(f"\n🔄 Applying modification: '{modification}'")
        result = self.agent.modify_behavior(modification, self.current_user)
        
        if result.success:
            print(f"✅ Success: {result.message}")
            if result.policies_created:
                print(f"📋 Policies created: {len(result.policies_created)}")
            if result.warnings:
                print(f"⚠️  Warnings: {', '.join(result.warnings)}")
        else:
            print(f"❌ Failed: {result.message}")
    
    def _view_status(self):
        """View system status."""
        print("\n📊 System Status")
        print("-" * 20)
        
        status = self.agent.get_behavior_status()
        
        print(f"🔧 Active Policies: {status['active_policies_count']}")
        print(f"📝 Recent Modifications: {len(status['recent_modifications'])}")
        print(f"📜 Audit Log Entries: {status['audit_log_entries']}")
        
        if status['recent_modifications']:
            print("\n📋 Recent Modifications:")
            for mod in status['recent_modifications'][-3:]:  # Show last 3
                print(f"  • {mod['request']} (by {mod['requester']})")
    
    def _view_policies(self):
        """View active policies."""
        print("\n📋 Active Policies")
        print("-" * 20)
        
        policies = self.controller.get_active_policies()
        
        if not policies:
            print("📭 No active policies.")
            return
        
        for i, policy in enumerate(policies, 1):
            print(f"{i}. {policy.description}")
            print(f"   ID: {policy.rule_id}")
            print(f"   Type: {policy.__class__.__name__}")
            print(f"   Active: {'✅' if policy.is_active() else '❌'}")
            print()
    
    def _view_audit_log(self):
        """View audit log."""
        print("\n📜 Audit Log")
        print("-" * 15)
        
        audit_log = self.controller.get_audit_log(10)  # Last 10 entries
        
        if not audit_log:
            print("📭 No audit log entries.")
            return
        
        for entry in audit_log[-5:]:  # Show last 5 entries
            timestamp = entry['timestamp']
            action_type = entry.get('action_type', 'unknown')
            decision = entry.get('decision', 'unknown')
            user_id = entry.get('user_id', 'unknown')
            
            print(f"⏰ {timestamp}")
            print(f"   Action: {action_type}")
            print(f"   Decision: {'✅' if decision else '❌'}")
            print(f"   User: {user_id}")
            print()
    
    def _run_demo_scenarios(self):
        """Run predefined demo scenarios."""
        print("\n🧪 Demo Scenarios")
        print("-" * 20)
        
        scenarios = [
            ("Business Hours Restriction", "Only work during business hours (9 AM to 5 PM on weekdays)"),
            ("Email Blocking", "Block all email sending operations"),
            ("User Blocking", "Block user spam@example.com"),
            ("Content Filtering", "Don't process content containing personal information"),
            ("Read-Only Mode", "Only allow read operations, block all modifications"),
        ]
        
        for i, (name, command) in enumerate(scenarios, 1):
            print(f"{i}. {name}")
        
        print("6. Run all scenarios")
        print()
        
        choice = input("Select scenario (1-6): ").strip()
        
        if choice == "6":
            self._run_all_scenarios(scenarios)
        elif choice.isdigit() and 1 <= int(choice) <= len(scenarios):
            scenario_name, command = scenarios[int(choice) - 1]
            self._run_single_scenario(scenario_name, command)
        else:
            print("❌ Invalid choice.")
    
    def _run_single_scenario(self, name: str, command: str):
        """Run a single demo scenario."""
        print(f"\n🎬 Running Scenario: {name}")
        print("-" * 40)
        
        if not self.current_user.is_admin:
            print("❌ Need admin user for this scenario.")
            print("Please change to admin user first.")
            return
        
        print(f"🔧 Applying: '{command}'")
        result = self.agent.modify_behavior(command, self.current_user)
        
        if result.success:
            print(f"✅ Success: {result.message}")
            
            # Test the modification
            print("\n🧪 Testing the modification...")
            test_goal = "Send an email to the team"
            test_result = self.agent.solve(test_goal, self.current_user)
            print(f"📤 Test result: {test_result}")
        else:
            print(f"❌ Failed: {result.message}")
    
    def _run_all_scenarios(self, scenarios):
        """Run all demo scenarios."""
        print("\n🎬 Running All Demo Scenarios")
        print("=" * 40)
        
        if not self.current_user.is_admin:
            print("❌ Need admin user for scenarios.")
            print("Please change to admin user first.")
            return
        
        for name, command in scenarios:
            print(f"\n🔧 Scenario: {name}")
            print(f"Command: {command}")
            
            result = self.agent.modify_behavior(command, self.current_user)
            if result.success:
                print(f"✅ Success: {result.message}")
            else:
                print(f"❌ Failed: {result.message}")
        
        print("\n📊 Final Status:")
        status = self.agent.get_behavior_status()
        print(f"Active Policies: {status['active_policies_count']}")
        print(f"Recent Modifications: {len(status['recent_modifications'])}")
    
    def _change_user(self):
        """Change the current user."""
        print("\n👤 Change User")
        print("-" * 15)
        
        self._setup_user()
    
    def _exit(self):
        """Exit the CLI."""
        print("\n👋 Thanks for using the Behavior Modification System!")
        print("📊 Final System Status:")
        status = self.agent.get_behavior_status()
        print(f"  • Active Policies: {status['active_policies_count']}")
        print(f"  • Modifications Made: {len(status['recent_modifications'])}")
        print(f"  • Audit Log Entries: {status['audit_log_entries']}")
        print("\n🚀 Goodbye!")
        self.running = False


def main():
    """Main entry point."""
    try:
        cli = BehaviorModificationCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
