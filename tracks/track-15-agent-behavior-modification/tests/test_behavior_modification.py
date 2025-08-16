"""
Tests for the Agent Behavior Modification System.
"""

import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch

# Import the modules we want to test
from behavior_modification import (
    BehaviorPolicyEngine,
    RuntimeBehaviorController,
    BehaviorModifiedAgent,
    User,
    AgentAction,
    ActionContext,
    SecurityLevel,
    TimeBasedRule,
    UserBasedRule,
    ActionBasedRule,
    ContentBasedRule,
    ModificationIntent,
    PolicyParser,
    ModificationIntentClassifier,
)


class TestPolicyRules:
    """Test individual policy rule implementations."""
    
    def test_time_based_rule_business_hours(self):
        """Test time-based rule for business hours."""
        rule = TimeBasedRule(
            rule_id="business_hours",
            allowed_days=[0, 1, 2, 3, 4],  # Monday to Friday
            allowed_times=[time(9, 0), time(17, 0)],  # 9 AM to 5 PM
            description="Business hours only"
        )
        
        # Test during business hours (Monday 10 AM)
        action = AgentAction(action_type="test", action_name="test_action")
        context = ActionContext(
            current_time=datetime(2024, 1, 1, 10, 0),  # Monday 10 AM
            security_level=SecurityLevel.NORMAL
        )
        
        decision = rule.evaluate(action, context)
        assert decision.allowed is True
        
        # Test outside business hours (Saturday 10 AM)
        context.current_time = datetime(2024, 1, 6, 10, 0)  # Saturday 10 AM
        decision = rule.evaluate(action, context)
        assert decision.allowed is False
        assert "not allowed on day" in decision.reason
    
    def test_user_based_rule_block_user(self):
        """Test user-based rule for blocking specific users."""
        rule = UserBasedRule(
            rule_id="block_spam",
            blocked_users=["spam@example.com"],
            description="Block spam user"
        )
        
        action = AgentAction(action_type="test", action_name="test_action")
        
        # Test with blocked user
        blocked_user = User(id="spam", email="spam@example.com")
        context = ActionContext(current_user=blocked_user, security_level=SecurityLevel.NORMAL)
        
        decision = rule.evaluate(action, context)
        assert decision.allowed is False
        assert "blocked by policy" in decision.reason
        
        # Test with regular user
        regular_user = User(id="john", email="john@example.com")
        context.current_user = regular_user
        
        decision = rule.evaluate(action, context)
        assert decision.allowed is True
    
    def test_action_based_rule_restrict_actions(self):
        """Test action-based rule for restricting specific actions."""
        rule = ActionBasedRule(
            rule_id="no_deletes",
            restricted_actions=["delete", "remove"],
            description="Prevent deletions"
        )
        
        # Test restricted action
        delete_action = AgentAction(action_type="file", action_name="delete_file")
        context = ActionContext(security_level=SecurityLevel.NORMAL)
        
        decision = rule.evaluate(delete_action, context)
        assert decision.allowed is False
        assert "restricted by policy" in decision.reason
        
        # Test allowed action
        read_action = AgentAction(action_type="file", action_name="read_file")
        decision = rule.evaluate(read_action, context)
        assert decision.allowed is True
    
    def test_content_based_rule_block_patterns(self):
        """Test content-based rule for blocking specific patterns."""
        rule = ContentBasedRule(
            rule_id="no_personal_info",
            blocked_patterns=[r'\b\d{3}-\d{2}-\d{4}\b'],  # SSN pattern
            description="Block personal information"
        )
        
        # Test with personal information
        personal_action = AgentAction(
            action_type="data",
            action_name="process_data",
            content="SSN: 123-45-6789"
        )
        context = ActionContext(security_level=SecurityLevel.NORMAL)
        
        decision = rule.evaluate(personal_action, context)
        assert decision.allowed is False
        assert "blocked pattern" in decision.reason
        
        # Test without personal information
        safe_action = AgentAction(
            action_type="data",
            action_name="process_data",
            content="This is safe content"
        )
        
        decision = rule.evaluate(safe_action, context)
        assert decision.allowed is True


class TestPolicyEngine:
    """Test the main policy engine."""
    
    def test_add_policy(self):
        """Test adding policies to the engine."""
        engine = BehaviorPolicyEngine()
        
        rule = TimeBasedRule(
            rule_id="test_rule",
            allowed_days=[0, 1, 2, 3, 4],
            description="Test rule"
        )
        
        result = engine.add_policy(rule)
        assert result.success is True
        assert result.policy_id == "test_rule"
        
        # Test adding duplicate rule
        result = engine.add_policy(rule)
        assert result.success is False
        assert "conflicts detected" in result.message
    
    def test_evaluate_action_no_policies(self):
        """Test action evaluation when no policies are active."""
        engine = BehaviorPolicyEngine()
        
        action = AgentAction(action_type="test", action_name="test_action")
        context = ActionContext(security_level=SecurityLevel.NORMAL)
        
        decision = engine.evaluate_action(action, context)
        assert decision.allowed is True
        assert "No policies to evaluate" in decision.reason
    
    def test_evaluate_action_with_policies(self):
        """Test action evaluation with active policies."""
        engine = BehaviorPolicyEngine()
        
        # Add a blocking policy
        rule = ActionBasedRule(
            rule_id="block_test",
            restricted_actions=["test_action"],
            description="Block test actions"
        )
        engine.add_policy(rule)
        
        action = AgentAction(action_type="test", action_name="test_action")
        context = ActionContext(security_level=SecurityLevel.NORMAL)
        
        decision = engine.evaluate_action(action, context)
        assert decision.allowed is False
        assert "restricted by policy" in decision.reason
    
    def test_policy_conflict_resolution(self):
        """Test resolution of conflicting policies."""
        engine = BehaviorPolicyEngine()
        
        # Add two conflicting policies
        rule1 = TimeBasedRule(
            rule_id="weekdays",
            allowed_days=[0, 1, 2, 3, 4],
            description="Weekdays only"
        )
        rule2 = TimeBasedRule(
            rule_id="weekends",
            allowed_days=[5, 6],
            description="Weekends only"
        )
        
        engine.add_policy(rule1)
        engine.add_policy(rule2)
        
        # Test on Monday (should be blocked by weekend policy)
        action = AgentAction(action_type="test", action_name="test_action")
        context = ActionContext(
            current_time=datetime(2024, 1, 1, 10, 0),  # Monday
            security_level=SecurityLevel.NORMAL
        )
        
        decision = engine.evaluate_action(action, context)
        # The most restrictive policy should win
        assert decision.allowed is False


class TestNaturalLanguageParser:
    """Test the natural language policy parser."""
    
    def test_intent_classification(self):
        """Test intent classification from natural language."""
        classifier = ModificationIntentClassifier()
        
        # Test time restriction
        intent = classifier.classify_intent("Only run on weekdays")
        assert intent == ModificationIntent.TIME_RESTRICTION
        
        # Test user restriction
        intent = classifier.classify_intent("Block user spam@example.com")
        assert intent == ModificationIntent.USER_RESTRICTION
        
        # Test action restriction
        intent = classifier.classify_intent("Don't send emails")
        assert intent == ModificationIntent.ACTION_RESTRICTION
    
    def test_parameter_extraction(self):
        """Test parameter extraction from natural language."""
        classifier = ModificationIntentClassifier()
        
        # Test time parameters
        params = classifier.extract_parameters(
            "Only allow operations on weekdays between 9 AM and 5 PM",
            ModificationIntent.TIME_RESTRICTION
        )
        assert "allowed_days" in params
        assert params["allowed_days"] == [0, 1, 2, 3, 4]  # Monday to Friday
        
        # Test user parameters
        params = classifier.extract_parameters(
            "Block user spam@example.com and admin@example.com",
            ModificationIntent.USER_RESTRICTION
        )
        assert "blocked_users" in params
        assert "spam@example.com" in params["blocked_users"]
        assert "admin@example.com" in params["blocked_users"]
    
    def test_policy_parsing(self):
        """Test complete policy parsing from natural language."""
        parser = PolicyParser()
        
        # Test simple time restriction
        rules = parser.parse_modification_request("Only run on weekdays")
        assert len(rules) > 0
        assert isinstance(rules[0], TimeBasedRule)
        
        # Test user blocking
        rules = parser.parse_modification_request("Block user spam@example.com")
        assert len(rules) > 0
        assert isinstance(rules[0], UserBasedRule)
    
    def test_policy_validation(self):
        """Test policy validation."""
        parser = PolicyParser()
        
        # Test valid policy
        valid_rules = [
            TimeBasedRule(
                rule_id="test",
                allowed_days=[0, 1, 2, 3, 4],
                description="Valid rule"
            )
        ]
        
        result = parser.validate_policy_rules(valid_rules)
        assert result.valid is True
        
        # Test invalid policy
        invalid_rules = [
            TimeBasedRule(
                rule_id="test",
                allowed_days=[0, 1, 2, 3, 4],
                description=""  # Empty description
            )
        ]
        
        result = parser.validate_policy_rules(invalid_rules)
        assert result.valid is False
        assert len(result.warnings) > 0


class TestBehaviorController:
    """Test the runtime behavior controller."""
    
    def test_behavior_modification(self):
        """Test modifying agent behavior through natural language."""
        controller = RuntimeBehaviorController()
        user = User(id="admin", is_admin=True)
        
        # Test simple modification
        result = controller.modify_agent_behavior(
            "Block all email operations",
            user
        )
        
        assert result.success is True
        assert len(result.policies_created) > 0
        
        # Test the modification
        action = AgentAction(action_type="communication", action_name="send_email")
        context = ActionContext(current_user=user, security_level=SecurityLevel.NORMAL)
        
        decision = controller.intercept_agent_action(action, context)
        assert decision == "block"  # Should be blocked
    
    def test_modification_history(self):
        """Test tracking modification history."""
        controller = RuntimeBehaviorController()
        user = User(id="admin", is_admin=True)
        
        # Add a modification
        controller.modify_agent_behavior("Block emails", user)
        
        history = controller.get_modification_history()
        assert len(history) == 1
        assert history[0].natural_language_request == "Block emails"
        assert history[0].requester.id == "admin"
    
    def test_audit_logging(self):
        """Test audit log functionality."""
        controller = RuntimeBehaviorController()
        user = User(id="test", email="test@example.com")
        
        # Perform some actions
        action = AgentAction(action_type="test", action_name="test_action")
        context = ActionContext(current_user=user, security_level=SecurityLevel.NORMAL)
        
        controller.intercept_agent_action(action, context)
        
        # Check audit log
        audit_log = controller.get_audit_log()
        assert len(audit_log) > 0
        
        latest_entry = audit_log[-1]
        assert latest_entry["action_type"] == "test"
        assert latest_entry["user_id"] == "test"


class TestBehaviorModifiedAgent:
    """Test the behavior-modified agent."""
    
    def test_agent_goal_processing(self):
        """Test agent goal processing with behavior modification."""
        controller = RuntimeBehaviorController()
        agent = BehaviorModifiedAgent(
            llm=Mock(),
            tools=[],
            memory=Mock(),
            reasoner=Mock(),
            behavior_controller=controller
        )
        
        user = User(id="test", email="test@example.com")
        
        # Test without restrictions
        result = agent.solve("Send an email", user)
        assert "Processing goal" in result
        
        # Add restriction
        admin_user = User(id="admin", is_admin=True)
        agent.modify_behavior("Block all email operations", admin_user)
        
        # Test with restriction
        result = agent.solve("Send an email", user)
        assert "Policy violation" in result
    
    def test_tool_execution_interception(self):
        """Test tool execution interception."""
        controller = RuntimeBehaviorController()
        agent = BehaviorModifiedAgent(
            llm=Mock(),
            tools=[],
            memory=Mock(),
            reasoner=Mock(),
            behavior_controller=controller
        )
        
        user = User(id="test", email="test@example.com")
        
        # Test tool execution
        tool_call = {"name": "send_email", "parameters": {"to": "test@example.com"}}
        result = agent.execute_tool_call(tool_call, user)
        assert result["success"] is True
        
        # Add restriction
        admin_user = User(id="admin", is_admin=True)
        agent.modify_behavior("Block email tools", admin_user)
        
        # Test blocked tool execution
        result = agent.execute_tool_call(tool_call, user)
        assert result["blocked"] is True
        assert "blocked by policy" in result["error"]
    
    def test_agent_status(self):
        """Test agent status reporting."""
        controller = RuntimeBehaviorController()
        agent = BehaviorModifiedAgent(
            llm=Mock(),
            tools=[],
            memory=Mock(),
            reasoner=Mock(),
            behavior_controller=controller
        )
        
        # Add some modifications
        admin_user = User(id="admin", is_admin=True)
        agent.modify_behavior("Block emails", admin_user)
        agent.modify_behavior("Only work on weekdays", admin_user)
        
        status = agent.get_behavior_status()
        assert status["active_policies_count"] >= 2
        assert len(status["recent_modifications"]) >= 2
        assert status["audit_log_entries"] > 0


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create the system
        controller = RuntimeBehaviorController()
        agent = BehaviorModifiedAgent(
            llm=Mock(),
            tools=[],
            memory=Mock(),
            reasoner=Mock(),
            behavior_controller=controller
        )
        
        # Create users
        admin_user = User(id="admin", is_admin=True)
        regular_user = User(id="user", email="user@example.com")
        
        # 1. Agent starts with no restrictions
        result = agent.solve("Send an email to the team", regular_user)
        assert "Processing goal" in result
        
        # 2. Admin adds time-based restriction
        modification_result = agent.modify_behavior(
            "Only work during business hours (9 AM to 5 PM on weekdays)",
            admin_user
        )
        assert modification_result.success is True
        
        # 3. Test during business hours
        with patch('behavior_modification.controller.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0)  # Monday 10 AM
            result = agent.solve("Send an email", regular_user)
            assert "Processing goal" in result
        
        # 4. Test outside business hours
        with patch('behavior_modification.controller.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 6, 10, 0)  # Saturday 10 AM
            result = agent.solve("Send an email", regular_user)
            assert "Policy violation" in result
        
        # 5. Check system status
        status = agent.get_behavior_status()
        assert status["active_policies_count"] > 0
        assert len(status["recent_modifications"]) > 0
    
    def test_multiple_policy_types(self):
        """Test combining multiple types of policies."""
        controller = RuntimeBehaviorController()
        agent = BehaviorModifiedAgent(
            llm=Mock(),
            tools=[],
            memory=Mock(),
            reasoner=Mock(),
            behavior_controller=controller
        )
        
        admin_user = User(id="admin", is_admin=True)
        regular_user = User(id="user", email="user@example.com")
        
        # Add multiple policies
        agent.modify_behavior("Only work on weekdays", admin_user)
        agent.modify_behavior("Block user spam@example.com", admin_user)
        agent.modify_behavior("Don't send emails", admin_user)
        
        # Test with regular user on weekday
        with patch('behavior_modification.controller.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0)  # Monday 10 AM
            result = agent.solve("Send an email", regular_user)
            assert "Policy violation" in result  # Should be blocked by email restriction
        
        # Test with blocked user
        blocked_user = User(id="spam", email="spam@example.com")
        result = agent.solve("Read a file", blocked_user)
        assert "Policy violation" in result  # Should be blocked by user restriction


if __name__ == "__main__":
    pytest.main([__file__])
