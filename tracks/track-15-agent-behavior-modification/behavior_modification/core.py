"""
Core policy framework for the Agent Behavior Modification System.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from .models import (
    AgentAction,
    ActionContext,
    PolicyDecision,
    PolicyUpdateResult,
    ValidationResult,
)


class PolicyRule(ABC):
    """Abstract base class for all policy rules."""
    
    def __init__(self, rule_id: str, description: str, priority: int = 0):
        self.rule_id = rule_id
        self.description = description
        self.priority = priority
        self.created_at = datetime.now()
        self.active = True
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def evaluate(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Evaluate whether an action is allowed under this policy."""
        pass
    
    def is_active(self) -> bool:
        """Check if the policy rule is currently active."""
        return self.active
    
    def deactivate(self):
        """Deactivate this policy rule."""
        self.active = False
    
    def activate(self):
        """Activate this policy rule."""
        self.active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy rule to dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "active": self.active,
            "metadata": self.metadata,
            "type": self.__class__.__name__,
        }


class PolicyResolver:
    """Resolves conflicts between multiple policy decisions."""
    
    def resolve_conflicts(self, decisions: List[PolicyDecision]) -> PolicyDecision:
        """Resolve conflicts between multiple policy decisions."""
        if not decisions:
            return PolicyDecision(allowed=True, reason="No policies to evaluate")
        
        # Filter out None decisions
        valid_decisions = [d for d in decisions if d is not None]
        if not valid_decisions:
            return PolicyDecision(allowed=True, reason="No valid policy decisions")
        
        # Check for any blocks (most restrictive wins)
        blocked_decisions = [d for d in valid_decisions if not d.allowed]
        if blocked_decisions:
            # Return the first blocked decision with the most detailed reason
            return max(blocked_decisions, key=lambda d: len(d.reason))
        
        # Check for escalations
        escalation_decisions = [d for d in valid_decisions if d.escalation_required]
        if escalation_decisions:
            return escalation_decisions[0]
        
        # Check for modifications
        modified_decisions = [d for d in valid_decisions if d.modified_action is not None]
        if modified_decisions:
            return modified_decisions[0]
        
        # All decisions allow the action
        return PolicyDecision(allowed=True, reason="All policies allow this action")
    
    def combine_decisions(self, decisions: List[PolicyDecision]) -> PolicyDecision:
        """Combine multiple policy decisions into a final decision."""
        return self.resolve_conflicts(decisions)


class BehaviorContext:
    """Context information for behavior evaluation."""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.current_user = None
        self.conversation_history = []
        self.system_state = {}
        self.security_level = "normal"
        self.session_id = None
        self.request_id = None
    
    def update_context(self, **kwargs):
        """Update context information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_context_for_evaluation(self) -> Dict[str, Any]:
        """Return context dict for policy evaluation."""
        return {
            "current_time": self.current_time,
            "current_user": self.current_user,
            "conversation_history": self.conversation_history,
            "system_state": self.system_state,
            "security_level": self.security_level,
            "session_id": self.session_id,
            "request_id": self.request_id,
        }


class BehaviorPolicyEngine:
    """Main policy engine for evaluating agent actions."""
    
    def __init__(self):
        self.active_policies: List[PolicyRule] = []
        self.policy_resolver = PolicyResolver()
        self.context_evaluator = BehaviorContext()
        self.audit_log: List[Dict[str, Any]] = []
    
    def add_policy(self, policy: PolicyRule) -> PolicyUpdateResult:
        """Add a new behavior policy to the active set."""
        try:
            # Check for conflicts with existing policies
            conflicts = self._detect_policy_conflicts(policy)
            
            if conflicts:
                return PolicyUpdateResult(
                    success=False,
                    message=f"Policy conflicts detected: {', '.join(conflicts)}",
                    conflicts=conflicts
                )
            
            self.active_policies.append(policy)
            self._log_policy_change("add", policy.rule_id)
            
            return PolicyUpdateResult(
                success=True,
                policy_id=policy.rule_id,
                message=f"Policy '{policy.description}' added successfully"
            )
        
        except Exception as e:
            return PolicyUpdateResult(
                success=False,
                message=f"Failed to add policy: {str(e)}"
            )
    
    def remove_policy(self, policy_id: str) -> PolicyUpdateResult:
        """Remove a policy from the active set."""
        try:
            policy = next((p for p in self.active_policies if p.rule_id == policy_id), None)
            
            if not policy:
                return PolicyUpdateResult(
                    success=False,
                    message=f"Policy with ID '{policy_id}' not found"
                )
            
            self.active_policies = [p for p in self.active_policies if p.rule_id != policy_id]
            self._log_policy_change("remove", policy_id)
            
            return PolicyUpdateResult(
                success=True,
                policy_id=policy_id,
                message=f"Policy '{policy.description}' removed successfully"
            )
        
        except Exception as e:
            return PolicyUpdateResult(
                success=False,
                message=f"Failed to remove policy: {str(e)}"
            )
    
    def evaluate_action(self, action: AgentAction, context: ActionContext) -> PolicyDecision:
        """Evaluate if an action is allowed under current policies."""
        try:
            # Update context
            self.context_evaluator.update_context(
                current_time=context.current_time,
                current_user=context.current_user,
                security_level=context.security_level.value if context.security_level else "normal"
            )
            
            # Evaluate all active policies
            decisions = []
            for policy in self.active_policies:
                if policy.is_active():
                    decision = policy.evaluate(action, context)
                    decisions.append(decision)
            
            # Resolve conflicts and get final decision
            final_decision = self.policy_resolver.resolve_conflicts(decisions)
            
            # Log the evaluation
            self._log_action_evaluation(action, context, final_decision, decisions)
            
            return final_decision
        
        except Exception as e:
            # In case of error, default to blocking the action
            error_decision = PolicyDecision(
                allowed=False,
                reason=f"Policy evaluation error: {str(e)}"
            )
            self._log_action_evaluation(action, context, error_decision, [])
            return error_decision
    
    def modify_behavior(self, modification_request: str) -> PolicyUpdateResult:
        """Parse natural language modification and update policies."""
        # This is a placeholder - actual implementation will be in the parser
        return PolicyUpdateResult(
            success=False,
            message="Behavior modification not implemented yet"
        )
    
    def get_active_policies(self) -> List[PolicyRule]:
        """Get all currently active policies."""
        return [p for p in self.active_policies if p.is_active()]
    
    def get_policy_by_id(self, policy_id: str) -> Optional[PolicyRule]:
        """Get a specific policy by ID."""
        return next((p for p in self.active_policies if p.rule_id == policy_id), None)
    
    def _detect_policy_conflicts(self, new_policy: PolicyRule) -> List[str]:
        """Detect conflicts between a new policy and existing policies."""
        conflicts = []
        
        for existing_policy in self.active_policies:
            if existing_policy.is_active():
                conflict = self._check_policy_pair(new_policy, existing_policy)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_policy_pair(self, policy1: PolicyRule, policy2: PolicyRule) -> Optional[str]:
        """Check for conflicts between two policies."""
        # Basic conflict detection - can be enhanced
        if (policy1.__class__ == policy2.__class__ and 
            hasattr(policy1, 'rule_id') and hasattr(policy2, 'rule_id') and
            policy1.rule_id == policy2.rule_id):
            return f"Duplicate policy ID: {policy1.rule_id}"
        
        return None
    
    def _log_policy_change(self, action: str, policy_id: str):
        """Log policy changes for audit purposes."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "policy_id": policy_id,
            "active_policy_count": len(self.get_active_policies())
        })
    
    def _log_action_evaluation(self, action: AgentAction, context: ActionContext, 
                              decision: PolicyDecision, all_decisions: List[PolicyDecision]):
        """Log action evaluations for audit purposes."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action_type": action.action_type,
            "action_name": action.action_name,
            "user_id": context.current_user.id if context.current_user else None,
            "decision": decision.allowed,
            "reason": decision.reason,
            "policies_evaluated": len(all_decisions),
            "escalation_required": decision.escalation_required
        })
    
    def get_audit_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        if limit:
            return self.audit_log[-limit:]
        return self.audit_log.copy()
