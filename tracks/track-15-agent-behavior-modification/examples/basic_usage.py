"""
Basic Usage Example for the Agent Behavior Modification System.

This example demonstrates how to use the behavior modification system
to dynamically control agent behavior through natural language commands.
"""

import sys
import os
from datetime import datetime, time
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from behavior_modification import (
    BehaviorModifiedAgent,
    RuntimeBehaviorController,
    User,
    AgentAction,
    ActionContext,
    SecurityLevel,
    TimeBasedRule,
    UserBasedRule,
    ActionBasedRule,
    ContentBasedRule,
)


def create_demo_user(user_id: str, is_admin: bool = False) -> User:
    """Create a demo user for testing."""
    return User(
        id=user_id,
        email=f"{user_id}@example.com",
        name=f"Demo User {user_id}",
        role="user" if not is_admin else "admin",
        is_admin=is_admin,
        permissions=["basic_access"] if not is_admin else ["basic_access", "policy_management"]
    )


def demo_basic_behavior_modification():
    """Demonstrate basic behavior modification functionality."""
    print("=== Basic Behavior Modification Demo ===\n")
    
    # Create a behavior controller
    controller = RuntimeBehaviorController()
    
    # Create demo users
    admin_user = create_demo_user("admin", is_admin=True)
    regular_user = create_demo_user("john")
    blocked_user = create_demo_user("spam")
    
    print("1. Time-based restrictions")
    print("-" * 30)
    
    # Add a time-based policy
    time_policy = TimeBasedRule(
        rule_id="business_hours",
        allowed_days=[0, 1, 2, 3, 4],  # Monday to Friday
        allowed_times=[time(9, 0), time(17, 0)],  # 9 AM to 5 PM
        description="Only allow operations during business hours"
    )
    
    result = controller.policy_engine.add_policy(time_policy)
    print(f"Added time policy: {result.message}")
    
    # Test the policy
    test_action = AgentAction(
        action_type="email",
        action_name="send_email",
        content="Hello, this is a test email"
    )
    
    # Test during business hours (Monday 10 AM)
    business_context = ActionContext(
        current_user=regular_user,
        current_time=datetime(2024, 1, 1, 10, 0),  # Monday 10 AM
        security_level=SecurityLevel.NORMAL
    )
    
    decision = controller.intercept_agent_action(test_action, business_context)
    print(f"Action during business hours: {decision}")
    
    # Test outside business hours (Saturday 10 AM)
    weekend_context = ActionContext(
        current_user=regular_user,
        current_time=datetime(2024, 1, 6, 10, 0),  # Saturday 10 AM
        security_level=SecurityLevel.NORMAL
    )
    
    decision = controller.intercept_agent_action(test_action, weekend_context)
    print(f"Action on weekend: {decision}")
    
    print("\n2. User-based restrictions")
    print("-" * 30)
    
    # Add a user-based policy
    user_policy = UserBasedRule(
        rule_id="block_spam_user",
        blocked_users=["spam@example.com"],
        description="Block requests from spam user"
    )
    
    result = controller.policy_engine.add_policy(user_policy)
    print(f"Added user policy: {result.message}")
    
    # Test with blocked user
    blocked_context = ActionContext(
        current_user=blocked_user,
        current_time=datetime.now(),
        security_level=SecurityLevel.NORMAL
    )
    
    decision = controller.intercept_agent_action(test_action, blocked_context)
    print(f"Action from blocked user: {decision}")
    
    # Test with regular user
    regular_context = ActionContext(
        current_user=regular_user,
        current_time=datetime.now(),
        security_level=SecurityLevel.NORMAL
    )
    
    decision = controller.intercept_agent_action(test_action, regular_context)
    print(f"Action from regular user: {decision}")
    
    print("\n3. Action-based restrictions")
    print("-" * 30)
    
    # Add an action-based policy
    action_policy = ActionBasedRule(
        rule_id="no_deletes",
        restricted_actions=["delete", "remove"],
        description="Prevent deletion operations"
    )
    
    result = controller.policy_engine.add_policy(action_policy)
    print(f"Added action policy: {result.message}")
    
    # Test delete action
    delete_action = AgentAction(
        action_type="file_operation",
        action_name="delete_file",
        content="Delete important file"
    )
    
    decision = controller.intercept_agent_action(delete_action, regular_context)
    print(f"Delete action: {decision}")
    
    # Test read action (should be allowed)
    read_action = AgentAction(
        action_type="file_operation",
        action_name="read_file",
        content="Read file content"
    )
    
    decision = controller.intercept_agent_action(read_action, regular_context)
    print(f"Read action: {decision}")
    
    print("\n4. Natural language modification")
    print("-" * 30)
    
    # Test natural language modification
    modification_request = "Block all email sending operations"
    result = controller.modify_agent_behavior(modification_request, admin_user)
    print(f"Modification result: {result.message}")
    
    # Test the new policy
    email_action = AgentAction(
        action_type="communication",
        action_name="send_email",
        content="Test email"
    )
    
    decision = controller.intercept_agent_action(email_action, regular_context)
    print(f"Email action after modification: {decision}")
    
    print("\n5. Content-based restrictions")
    print("-" * 30)
    
    # Add a content-based policy
    content_policy = ContentBasedRule(
        rule_id="no_personal_info",
        blocked_patterns=[r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
        description="Block personal information like SSN and email addresses"
    )
    
    result = controller.policy_engine.add_policy(content_policy)
    print(f"Added content policy: {result.message}")
    
    # Test with personal information
    personal_action = AgentAction(
        action_type="data_processing",
        action_name="process_data",
        content="User SSN: 123-45-6789, email: test@example.com"
    )
    
    decision = controller.intercept_agent_action(personal_action, regular_context)
    print(f"Action with personal info: {decision}")
    
    # Test without personal information
    safe_action = AgentAction(
        action_type="data_processing",
        action_name="process_data",
        content="This is safe content without personal information"
    )
    
    decision = controller.intercept_agent_action(safe_action, regular_context)
    print(f"Action without personal info: {decision}")
    
    print("\n6. System status")
    print("-" * 30)
    
    # Show system status
    active_policies = controller.get_active_policies()
    print(f"Active policies: {len(active_policies)}")
    
    for policy in active_policies:
        print(f"  - {policy.description} (ID: {policy.rule_id})")
    
    audit_log = controller.get_audit_log(5)
    print(f"\nRecent audit log entries: {len(audit_log)}")
    
    for entry in audit_log[-3:]:  # Show last 3 entries
        action_type = entry.get('action_type', 'unknown')
        decision = entry.get('decision', 'unknown')
        print(f"  - {entry['timestamp']}: {action_type} - {decision}")


def demo_agent_integration():
    """Demonstrate integration with a behavior-modified agent."""
    print("\n=== Agent Integration Demo ===\n")
    
    # Create a behavior controller
    controller = RuntimeBehaviorController()
    
    # Create a behavior-modified agent
    # Note: In a real implementation, this would use actual LLM, tools, etc.
    agent = BehaviorModifiedAgent(
        llm=None,  # Placeholder
        tools=[],  # Placeholder
        memory=None,  # Placeholder
        reasoner=None,  # Placeholder
        behavior_controller=controller
    )
    
    # Create users
    admin_user = create_demo_user("admin", is_admin=True)
    regular_user = create_demo_user("john")
    
    print("1. Agent with no restrictions")
    print("-" * 30)
    
    result = agent.solve("Send an email to the team", regular_user)
    print(f"Agent response: {result}")
    
    print("\n2. Adding behavior modification")
    print("-" * 30)
    
    # Modify agent behavior
    modification_result = agent.modify_behavior(
        "Don't send emails after 6 PM",
        admin_user
    )
    print(f"Modification result: {modification_result.message}")
    
    print("\n3. Agent with restrictions")
    print("-" * 30)
    
    # Test during allowed time
    result = agent.solve("Send an email to the team", regular_user)
    print(f"Agent response (allowed time): {result}")
    
    # Test during restricted time (would need to mock time)
    result = agent.solve("Send an email to the team", regular_user)
    print(f"Agent response (restricted time): {result}")
    
    print("\n4. Agent status")
    print("-" * 30)
    
    status = agent.get_behavior_status()
    print(f"Active policies: {status['active_policies_count']}")
    print(f"Recent modifications: {len(status['recent_modifications'])}")
    print(f"Audit log entries: {status['audit_log_entries']}")


def demo_advanced_features():
    """Demonstrate advanced features of the behavior modification system."""
    print("\n=== Advanced Features Demo ===\n")
    
    controller = RuntimeBehaviorController()
    admin_user = create_demo_user("admin", is_admin=True)
    
    print("1. Policy conflict resolution")
    print("-" * 30)
    
    # Add conflicting policies
    policy1 = TimeBasedRule(
        rule_id="weekdays_only",
        allowed_days=[0, 1, 2, 3, 4],
        description="Only allow operations on weekdays"
    )
    
    policy2 = TimeBasedRule(
        rule_id="weekends_only",
        allowed_days=[5, 6],
        description="Only allow operations on weekends"
    )
    
    result1 = controller.policy_engine.add_policy(policy1)
    result2 = controller.policy_engine.add_policy(policy2)
    
    print(f"Policy 1 result: {result1.message}")
    print(f"Policy 2 result: {result2.message}")
    
    # Test with conflicting policies
    test_action = AgentAction(
        action_type="test",
        action_name="test_action",
        content="Test content"
    )
    
    context = ActionContext(
        current_user=admin_user,
        current_time=datetime.now(),
        security_level=SecurityLevel.NORMAL
    )
    
    decision = controller.intercept_agent_action(test_action, context)
    print(f"Action with conflicting policies: {decision}")
    
    print("\n2. Security level modifications")
    print("-" * 30)
    
    # Add security level policy
    security_policy = ActionBasedRule(
        rule_id="high_security_required",
        restricted_actions=["delete", "modify"],
        conditions={
            "security_level": "high"
        },
        description="Require high security for destructive operations"
    )
    
    result = controller.policy_engine.add_policy(security_policy)
    print(f"Security policy result: {result.message}")
    
    # Test with different security levels
    low_security_context = ActionContext(
        current_user=admin_user,
        current_time=datetime.now(),
        security_level=SecurityLevel.LOW
    )
    
    high_security_context = ActionContext(
        current_user=admin_user,
        current_time=datetime.now(),
        security_level=SecurityLevel.HIGH
    )
    
    delete_action = AgentAction(
        action_type="file_operation",
        action_name="delete_file",
        content="Delete important file"
    )
    
    decision_low = controller.intercept_agent_action(delete_action, low_security_context)
    decision_high = controller.intercept_agent_action(delete_action, high_security_context)
    
    print(f"Delete action (low security): {decision_low}")
    print(f"Delete action (high security): {decision_high}")
    
    print("\n3. Policy validation")
    print("-" * 30)
    
    # Test policy validation
    from behavior_modification.parser import PolicyParser
    
    parser = PolicyParser()
    
    # Test valid policy
    valid_rules = [
        TimeBasedRule(
            rule_id="test_valid",
            allowed_days=[0, 1, 2, 3, 4],
            description="Valid time policy"
        )
    ]
    
    validation_result = parser.validate_policy_rules(valid_rules)
    print(f"Valid policy validation: {validation_result.valid}")
    
    # Test invalid policy (missing description)
    invalid_rules = [
        TimeBasedRule(
            rule_id="test_invalid",
            allowed_days=[0, 1, 2, 3, 4],
            description=""  # Empty description
        )
    ]
    
    validation_result = parser.validate_policy_rules(invalid_rules)
    print(f"Invalid policy validation: {validation_result.valid}")
    if validation_result.warnings:
        print(f"Warnings: {validation_result.warnings}")


if __name__ == "__main__":
    print("Agent Behavior Modification System - Demo")
    print("=" * 50)
    
    try:
        demo_basic_behavior_modification()
        demo_agent_integration()
        demo_advanced_features()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
