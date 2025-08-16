"""
Specific policy implementations for the Agent Behavior Modification System.
"""

import re
import uuid
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Union
from .core import PolicyRule
from .models import AgentAction, ActionContext, PolicyDecision, SecurityLevel


class TimeBasedRule(PolicyRule):
    """Policy rule based on time constraints."""
    
    def __init__(self, rule_id: str, allowed_times: Optional[List[time]] = None, 
                 allowed_days: Optional[List[int]] = None, 
                 blocked_times: Optional[List[time]] = None,
                 blocked_days: Optional[List[int]] = None,
                 description: str = "Time-based access control"):
        super().__init__(rule_id, description)
        self.allowed_times = allowed_times or []
        self.allowed_days = allowed_days or []  # 0=Monday, 6=Sunday
        self.blocked_times = blocked_times or []
        self.blocked_days = blocked_days or []
    
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Check if current time/day allows the action."""
        current_time = context.current_time
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_time_obj = current_time.time()
        
        # Check day restrictions
        if self.allowed_days and current_day not in self.allowed_days:
            return PolicyDecision(
                allowed=False,
                reason=f"Action not allowed on day {current_day} (Monday=0, Sunday=6). Allowed days: {self.allowed_days}"
            )
        
        if self.blocked_days and current_day in self.blocked_days:
            return PolicyDecision(
                allowed=False,
                reason=f"Action blocked on day {current_day} (Monday=0, Sunday=6). Blocked days: {self.blocked_days}"
            )
        
        # Check time restrictions
        if self.allowed_times:
            time_allowed = False
            for allowed_time in self.allowed_times:
                if current_time_obj >= allowed_time:
                    time_allowed = True
                    break
            
            if not time_allowed:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Action not allowed at current time {current_time_obj}. Allowed times: {self.allowed_times}"
                )
        
        if self.blocked_times:
            for blocked_time in self.blocked_times:
                if current_time_obj >= blocked_time:
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Action blocked at current time {current_time_obj}. Blocked times: {self.blocked_times}"
                    )
        
        return PolicyDecision(allowed=True, reason="Time-based policy allows this action")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "allowed_times": [t.isoformat() for t in self.allowed_times],
            "allowed_days": self.allowed_days,
            "blocked_times": [t.isoformat() for t in self.blocked_times],
            "blocked_days": self.blocked_days,
        })
        return base_dict


class UserBasedRule(PolicyRule):
    """Policy rule based on user constraints."""
    
    def __init__(self, rule_id: str, allowed_users: Optional[List[str]] = None, 
                 blocked_users: Optional[List[str]] = None,
                 allowed_roles: Optional[List[str]] = None,
                 blocked_roles: Optional[List[str]] = None,
                 description: str = "User-based access control"):
        super().__init__(rule_id, description)
        self.allowed_users = allowed_users or []
        self.blocked_users = blocked_users or []
        self.allowed_roles = allowed_roles or []
        self.blocked_roles = blocked_roles or []
    
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Check if current user is allowed to trigger this action."""
        if not context.current_user:
            return PolicyDecision(
                allowed=False,
                reason="No user context available for user-based policy evaluation"
            )
        
        user = context.current_user
        
        # Check blocked users first (most restrictive)
        if self.blocked_users:
            for blocked_user in self.blocked_users:
                if (blocked_user.lower() == user.id.lower() or
                    (user.email and blocked_user.lower() == user.email.lower())):
                    return PolicyDecision(
                        allowed=False,
                        reason=f"User {user.id} is blocked by policy"
                    )
        
        # Check blocked roles
        if self.blocked_roles and user.role:
            if user.role.lower() in [role.lower() for role in self.blocked_roles]:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Role {user.role} is blocked by policy"
                )
        
        # Check allowed users (if specified, user must be in list)
        if self.allowed_users:
            user_allowed = False
            for allowed_user in self.allowed_users:
                if (allowed_user.lower() == user.id.lower() or
                    (user.email and allowed_user.lower() == user.email.lower())):
                    user_allowed = True
                    break
            
            if not user_allowed:
                return PolicyDecision(
                    allowed=False,
                    reason=f"User {user.id} not in allowed users list: {self.allowed_users}"
                )
        
        # Check allowed roles (if specified, user role must be in list)
        if self.allowed_roles and user.role:
            if user.role.lower() not in [role.lower() for role in self.allowed_roles]:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Role {user.role} not in allowed roles list: {self.allowed_roles}"
                )
        
        return PolicyDecision(allowed=True, reason="User-based policy allows this action")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "allowed_users": self.allowed_users,
            "blocked_users": self.blocked_users,
            "allowed_roles": self.allowed_roles,
            "blocked_roles": self.blocked_roles,
        })
        return base_dict


class ActionBasedRule(PolicyRule):
    """Policy rule based on action constraints."""
    
    def __init__(self, rule_id: str, restricted_actions: Optional[List[str]] = None,
                 allowed_actions: Optional[List[str]] = None,
                 conditions: Optional[Dict[str, Any]] = None,
                 description: str = "Action-based restrictions", **kwargs):
        super().__init__(rule_id, description)
        self.restricted_actions = restricted_actions or []
        self.allowed_actions = allowed_actions or []
        self.conditions = conditions or {}
        # Handle any additional kwargs (like metadata) by storing them in metadata
        for key, value in kwargs.items():
            if key not in ['rule_id', 'restricted_actions', 'allowed_actions', 'conditions', 'description']:
                self.metadata[key] = value
    
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Check if action type is restricted under current conditions."""
        action_name = action.action_name.lower()
        action_type = action.action_type.lower()
        
        # Check if action is explicitly blocked
        if self.restricted_actions:
            for restricted in self.restricted_actions:
                if (restricted.lower() in action_name or 
                    restricted.lower() in action_type):
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Action '{action.action_name}' is restricted by policy"
                    )
        
        # Check if action is explicitly allowed (if allowed_actions specified)
        if self.allowed_actions:
            action_allowed = False
            for allowed in self.allowed_actions:
                if (allowed.lower() in action_name or 
                    allowed.lower() in action_type):
                    action_allowed = True
                    break
            
            if not action_allowed:
                return PolicyDecision(
                    allowed=False,
                    reason=f"Action '{action.action_name}' not in allowed actions list: {self.allowed_actions}"
                )
        
        # Check additional conditions
        if self.conditions:
            condition_result = self._evaluate_conditions(action, context)
            if not condition_result["allowed"]:
                return PolicyDecision(
                    allowed=False,
                    reason=condition_result["reason"]
                )
        
        return PolicyDecision(allowed=True, reason="Action-based policy allows this action")
    
    def _evaluate_conditions(self, action: AgentAction, context: ActionContext) -> Dict[str, Any]:
        """Evaluate additional conditions for the action."""
        # Check content-based conditions
        if "content_keywords" in self.conditions and action.content:
            blocked_keywords = self.conditions["content_keywords"].get("blocked", [])
            for keyword in blocked_keywords:
                if keyword.lower() in action.content.lower():
                    return {
                        "allowed": False,
                        "reason": f"Content contains blocked keyword: {keyword}"
                    }
        
        # Check parameter-based conditions
        if "parameter_limits" in self.conditions:
            for param_name, limit_info in self.conditions["parameter_limits"].items():
                if param_name in action.parameters:
                    param_value = action.parameters[param_name]
                    if "max_value" in limit_info and param_value > limit_info["max_value"]:
                        return {
                            "allowed": False,
                            "reason": f"Parameter {param_name} exceeds maximum value {limit_info['max_value']}"
                        }
                    if "min_value" in limit_info and param_value < limit_info["min_value"]:
                        return {
                            "allowed": False,
                            "reason": f"Parameter {param_name} below minimum value {limit_info['min_value']}"
                        }
        
        return {"allowed": True, "reason": "All conditions satisfied"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "restricted_actions": self.restricted_actions,
            "allowed_actions": self.allowed_actions,
            "conditions": self.conditions,
        })
        return base_dict


class SecurityLevelRule(PolicyRule):
    """Policy rule based on security level constraints."""
    
    def __init__(self, rule_id: str, required_level: SecurityLevel = SecurityLevel.NORMAL,
                 restricted_levels: Optional[List[SecurityLevel]] = None,
                 description: str = "Security level restrictions"):
        super().__init__(rule_id, description)
        self.required_level = required_level
        self.restricted_levels = restricted_levels or []
    
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Check if current security level allows the action."""
        current_level = context.security_level
        
        # Check if current level is restricted
        if current_level in self.restricted_levels:
            return PolicyDecision(
                allowed=False,
                reason=f"Action not allowed at security level {current_level.value}"
            )
        
        # Check if current level meets required level
        security_hierarchy = {
            SecurityLevel.LOW: 1,
            SecurityLevel.NORMAL: 2,
            SecurityLevel.HIGH: 3,
            SecurityLevel.CRITICAL: 4
        }
        
        current_level_value = security_hierarchy.get(current_level, 0)
        required_level_value = security_hierarchy.get(self.required_level, 0)
        
        if current_level_value < required_level_value:
            return PolicyDecision(
                allowed=False,
                reason=f"Security level {current_level.value} is insufficient. Required: {self.required_level.value}"
            )
        
        return PolicyDecision(allowed=True, reason="Security level policy allows this action")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "required_level": self.required_level.value,
            "restricted_levels": [level.value for level in self.restricted_levels],
        })
        return base_dict


class ContentBasedRule(PolicyRule):
    """Policy rule based on content analysis."""
    
    def __init__(self, rule_id: str, blocked_patterns: Optional[List[str]] = None,
                 required_patterns: Optional[List[str]] = None,
                 content_filters: Optional[Dict[str, Any]] = None,
                 description: str = "Content-based restrictions"):
        super().__init__(rule_id, description)
        self.blocked_patterns = blocked_patterns or []
        self.required_patterns = required_patterns or []
        self.content_filters = content_filters or {}
    
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Check if content meets policy requirements."""
        if not action.content:
            return PolicyDecision(allowed=True, reason="No content to evaluate")
        
        content = action.content.lower()
        
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return PolicyDecision(
                    allowed=False,
                    reason=f"Content contains blocked pattern: {pattern}"
                )
        
        # Check required patterns
        if self.required_patterns:
            for pattern in self.required_patterns:
                if not re.search(pattern, content, re.IGNORECASE):
                    return PolicyDecision(
                        allowed=False,
                        reason=f"Content missing required pattern: {pattern}"
                    )
        
        # Apply content filters
        if self.content_filters:
            filter_result = self._apply_content_filters(content)
            if not filter_result["allowed"]:
                return PolicyDecision(
                    allowed=False,
                    reason=filter_result["reason"]
                )
        
        return PolicyDecision(allowed=True, reason="Content-based policy allows this action")
    
    def _apply_content_filters(self, content: str) -> Dict[str, Any]:
        """Apply content filtering rules."""
        # Check length limits
        if "max_length" in self.content_filters:
            max_length = self.content_filters["max_length"]
            if len(content) > max_length:
                return {
                    "allowed": False,
                    "reason": f"Content exceeds maximum length of {max_length} characters"
                }
        
        # Check for sensitive information patterns
        if "sensitive_patterns" in self.content_filters:
            sensitive_patterns = self.content_filters["sensitive_patterns"]
            for pattern_name, pattern in sensitive_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    return {
                        "allowed": False,
                        "reason": f"Content contains sensitive information: {pattern_name}"
                    }
        
        return {"allowed": True, "reason": "Content filters passed"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "blocked_patterns": self.blocked_patterns,
            "required_patterns": self.required_patterns,
            "content_filters": self.content_filters,
        })
        return base_dict


# Factory function for creating policy rules
def create_policy_rule(rule_type: str, **kwargs) -> PolicyRule:
    """Factory function to create policy rules based on type."""
    rule_id = kwargs.get("rule_id", str(uuid.uuid4()))
    
    if rule_type == "time_based":
        return TimeBasedRule(rule_id, **kwargs)
    elif rule_type == "user_based":
        return UserBasedRule(rule_id, **kwargs)
    elif rule_type == "action_based":
        return ActionBasedRule(rule_id, **kwargs)
    elif rule_type == "security_level":
        return SecurityLevelRule(rule_id, **kwargs)
    elif rule_type == "content_based":
        return ContentBasedRule(rule_id, **kwargs)
    else:
        raise ValueError(f"Unknown policy rule type: {rule_type}")
