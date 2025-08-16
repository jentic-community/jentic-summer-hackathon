"""
Runtime Behavior Controller for the Agent Behavior Modification System.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from .core import BehaviorPolicyEngine, PolicyRule
from .models import (
    AgentAction,
    ActionContext,
    PolicyDecision,
    ModificationRequest,
    ModificationResult,
    User,
    ActionDecision,
)
from .parser import PolicyParser


class RuntimeBehaviorController:
    """Controls agent behavior at runtime by intercepting actions and applying policies."""
    
    def __init__(self, agent=None):
        self.agent = agent
        self.policy_engine = BehaviorPolicyEngine()
        self.policy_parser = PolicyParser()
        self.modification_history: List[ModificationRequest] = []
        self.active_modifications: Dict[str, ModificationRequest] = {}
    
    def intercept_agent_action(self, action: AgentAction, context: ActionContext) -> ActionDecision:
        """Intercept agent actions and apply policy evaluation."""
        try:
            # Evaluate the action against current policies
            decision = self.policy_engine.evaluate_action(action, context)
            
            if decision.allowed:
                return ActionDecision.PROCEED
            else:
                return ActionDecision.BLOCK
            
        except Exception as e:
            # Log error and default to blocking
            print(f"Error evaluating action: {e}")
            return ActionDecision.BLOCK
    
    def modify_agent_behavior(self, modification_request: str, requester: User) -> ModificationResult:
        """Process behavior modification request."""
        try:
            # Create modification request
            request_id = str(uuid.uuid4())
            request = ModificationRequest(
                request_id=request_id,
                natural_language_request=modification_request,
                requester=requester,
                timestamp=datetime.now()
            )
            
            # Parse the request into policy rules
            policy_rules = self.policy_parser.parse_modification_request(modification_request)
            
            # Validate the generated rules
            validation_result = self.policy_parser.validate_policy_rules(policy_rules)
            
            if not validation_result.valid:
                return ModificationResult(
                    success=False,
                    request_id=request_id,
                    message=f"Policy validation failed: {', '.join(validation_result.errors)}",
                    warnings=validation_result.warnings
                )
            
            # Apply the policies
            policies_created = []
            policies_modified = []
            conflicts_resolved = []
            
            for rule in policy_rules:
                result = self.policy_engine.add_policy(rule)
                if result.success:
                    policies_created.append(rule.rule_id)
                else:
                    # Handle conflicts
                    if result.conflicts:
                        conflicts_resolved.extend(result.conflicts)
            
            # Store the modification request
            self.modification_history.append(request)
            self.active_modifications[request_id] = request
            
            return ModificationResult(
                success=True,
                request_id=request_id,
                policies_created=policies_created,
                policies_modified=policies_modified,
                conflicts_resolved=conflicts_resolved,
                message=f"Successfully applied {len(policies_created)} policy rules",
                warnings=validation_result.warnings
            )
        
        except Exception as e:
            return ModificationResult(
                success=False,
                request_id=request_id if 'request_id' in locals() else str(uuid.uuid4()),
                message=f"Failed to modify behavior: {str(e)}"
            )
    
    def remove_behavior_modification(self, request_id: str, requester: User) -> ModificationResult:
        """Remove a behavior modification."""
        try:
            if request_id not in self.active_modifications:
                return ModificationResult(
                    success=False,
                    request_id=request_id,
                    message="Modification request not found"
                )
            
            # Get the modification request
            modification = self.active_modifications[request_id]
            
            # Check if requester has permission to remove this modification
            if not self._can_modify_policy(requester, modification.requester):
                return ModificationResult(
                    success=False,
                    request_id=request_id,
                    message="Insufficient permissions to remove this modification"
                )
            
            # Remove the modification
            del self.active_modifications[request_id]
            
            # Note: In a full implementation, you might want to remove specific policies
            # associated with this modification rather than just removing the request
            
            return ModificationResult(
                success=True,
                request_id=request_id,
                message="Behavior modification removed successfully"
            )
        
        except Exception as e:
            return ModificationResult(
                success=False,
                request_id=request_id,
                message=f"Failed to remove modification: {str(e)}"
            )
    
    def get_active_policies(self) -> List[PolicyRule]:
        """Get all currently active policies."""
        return self.policy_engine.get_active_policies()
    
    def get_modification_history(self, limit: Optional[int] = None) -> List[ModificationRequest]:
        """Get modification history."""
        if limit:
            return self.modification_history[-limit:]
        return self.modification_history.copy()
    
    def get_audit_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get audit log from the policy engine."""
        return self.policy_engine.get_audit_log(limit)
    
    def _can_modify_policy(self, requester: User, original_requester: User) -> bool:
        """Check if a user can modify a policy created by another user."""
        # Basic permission check - can be enhanced
        if requester.is_admin:
            return True
        
        if requester.id == original_requester.id:
            return True
        
        # Check if requester has specific permissions
        if "policy_management" in requester.permissions:
            return True
        
        return False


class BehaviorModifiedAgent:
    """A Standard Agent that has been modified to support behavior control."""
    
    def __init__(self, llm, tools, memory, reasoner, behavior_controller: RuntimeBehaviorController):
        # Note: In a real implementation, this would inherit from StandardAgent
        # For now, we'll create a simplified version
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.reasoner = reasoner
        self.behavior_controller = behavior_controller
    
    def solve(self, goal: str, user: Optional[User] = None) -> str:
        """Solve a goal with behavior modification applied."""
        try:
            # Create action context
            context = ActionContext(
                current_user=user,
                current_time=datetime.now(),
                session_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4())
            )
            
            # Create agent action for goal evaluation
            goal_action = AgentAction(
                action_type="goal_processing",
                action_name="solve_goal",
                content=goal,
                parameters={"goal": goal}
            )
            
            # Evaluate the goal against policies
            decision = self.behavior_controller.intercept_agent_action(goal_action, context)
            
            if decision == ActionDecision.BLOCK:
                return f"Cannot process request: Policy violation detected"
            
            # If allowed, proceed with normal processing
            # In a real implementation, this would call the parent class's solve method
            return f"Processing goal: {goal} (behavior modification applied)"
        
        except Exception as e:
            return f"Error processing goal: {str(e)}"
    
    def execute_tool_call(self, tool_call: Dict[str, Any], user: Optional[User] = None) -> Dict[str, Any]:
        """Execute a tool call with behavior modification applied."""
        try:
            # Create action context
            context = ActionContext(
                current_user=user,
                current_time=datetime.now(),
                session_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4())
            )
            
            # Create agent action for tool execution
            tool_action = AgentAction(
                action_type="tool_execution",
                action_name=tool_call.get("name", "unknown_tool"),
                parameters=tool_call.get("parameters", {}),
                content=str(tool_call)
            )
            
            # Evaluate the tool call against policies
            decision = self.behavior_controller.intercept_agent_action(tool_action, context)
            
            if decision == ActionDecision.BLOCK:
                return {
                    "success": False,
                    "error": "Tool execution blocked by policy",
                    "blocked": True
                }
            
            # If allowed, proceed with normal tool execution
            # In a real implementation, this would call the actual tool
            return {
                "success": True,
                "result": f"Tool {tool_action.action_name} executed successfully",
                "blocked": False
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing tool: {str(e)}",
                "blocked": False
            }
    
    def modify_behavior(self, modification_request: str, requester: User) -> ModificationResult:
        """Modify the agent's behavior using natural language."""
        return self.behavior_controller.modify_agent_behavior(modification_request, requester)
    
    def get_behavior_status(self) -> Dict[str, Any]:
        """Get current behavior modification status."""
        active_policies = self.behavior_controller.get_active_policies()
        modification_history = self.behavior_controller.get_modification_history(5)  # Last 5
        
        return {
            "active_policies_count": len(active_policies),
            "active_policies": [policy.to_dict() for policy in active_policies],
            "recent_modifications": [
                {
                    "request_id": mod.request_id,
                    "request": mod.natural_language_request,
                    "requester": mod.requester.id,
                    "timestamp": mod.timestamp.isoformat()
                }
                for mod in modification_history
            ],
            "audit_log_entries": len(self.behavior_controller.get_audit_log())
        }


class PolicyUpdateManager:
    """Manages real-time policy updates and modifications."""
    
    def __init__(self, behavior_controller: RuntimeBehaviorController):
        self.controller = behavior_controller
        self.update_queue: List[ModificationRequest] = []
        self.processing = False
    
    def queue_modification(self, request: str, requester: User, priority: int = 0):
        """Queue a modification request for processing."""
        modification = ModificationRequest(
            request_id=str(uuid.uuid4()),
            natural_language_request=request,
            requester=requester,
            priority=priority,
            timestamp=datetime.now()
        )
        
        # Insert based on priority (higher priority first)
        if priority > 0:
            # Find position to insert based on priority
            insert_index = 0
            for i, queued_mod in enumerate(self.update_queue):
                if queued_mod.priority < priority:
                    insert_index = i
                    break
                insert_index = i + 1
            
            self.update_queue.insert(insert_index, modification)
        else:
            self.update_queue.append(modification)
    
    def process_modification_queue(self) -> List[ModificationResult]:
        """Process queued modifications in priority order."""
        if self.processing:
            return []  # Already processing
        
        self.processing = True
        results = []
        
        try:
            while self.update_queue:
                modification = self.update_queue.pop(0)
                result = self.apply_modification(modification)
                results.append(result)
                self.log_modification_result(modification, result)
        finally:
            self.processing = False
        
        return results
    
    def apply_modification(self, modification: ModificationRequest) -> ModificationResult:
        """Apply behavior modification to active agent."""
        return self.controller.modify_agent_behavior(
            modification.natural_language_request,
            modification.requester
        )
    
    def log_modification_result(self, modification: ModificationRequest, result: ModificationResult):
        """Log the result of a modification."""
        # In a real implementation, this would write to a log file or database
        print(f"Modification {modification.request_id}: {result.success} - {result.message}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of the modification queue."""
        return {
            "queue_length": len(self.update_queue),
            "processing": self.processing,
            "queued_modifications": [
                {
                    "request_id": mod.request_id,
                    "priority": mod.priority,
                    "timestamp": mod.timestamp.isoformat()
                }
                for mod in self.update_queue
            ]
        }
