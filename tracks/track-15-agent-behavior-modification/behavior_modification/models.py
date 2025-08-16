"""
Core data models for the Agent Behavior Modification System.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ModificationIntent(str, Enum):
    """Types of behavior modification intents."""
    TIME_RESTRICTION = "time_restriction"
    USER_RESTRICTION = "user_restriction"
    ACTION_RESTRICTION = "action_restriction"
    SECURITY_MODIFICATION = "security_modification"
    CONTENT_RESTRICTION = "content_restriction"
    GENERAL_RESTRICTION = "general_restriction"


class SecurityLevel(str, Enum):
    """Security levels for agent behavior."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ActionDecision(str, Enum):
    """Possible decisions for agent actions."""
    PROCEED = "proceed"
    BLOCK = "block"
    MODIFY = "modify"
    ESCALATE = "escalate"


class User(BaseModel):
    """User information for policy evaluation."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    is_admin: bool = False


class AgentAction(BaseModel):
    """Represents an action the agent is attempting to perform."""
    action_type: str
    action_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    content: Optional[str] = None
    target_user: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActionContext(BaseModel):
    """Context information for action evaluation."""
    current_user: Optional[User] = None
    current_time: datetime = Field(default_factory=datetime.now)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    system_state: Dict[str, Any] = Field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.NORMAL
    session_id: Optional[str] = None
    request_id: Optional[str] = None


class PolicyDecision(BaseModel):
    """Decision made by policy evaluation."""
    allowed: bool
    reason: str = ""
    modified_action: Optional[AgentAction] = None
    escalation_required: bool = False
    audit_log_entry: Optional[Dict[str, Any]] = None


class PolicyUpdateResult(BaseModel):
    """Result of a policy update operation."""
    success: bool
    policy_id: Optional[str] = None
    message: str = ""
    conflicts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result of policy validation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class ModificationRequest(BaseModel):
    """Request to modify agent behavior."""
    request_id: str
    natural_language_request: str
    requester: User
    priority: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    approval_status: Optional[str] = None


class ModificationResult(BaseModel):
    """Result of a behavior modification operation."""
    success: bool
    request_id: str
    policies_created: List[str] = Field(default_factory=list)
    policies_modified: List[str] = Field(default_factory=list)
    policies_removed: List[str] = Field(default_factory=list)
    message: str = ""
    conflicts_resolved: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class Conflict(BaseModel):
    """Represents a conflict between policies."""
    conflict_id: str
    policy_ids: List[str]
    conflict_type: str
    description: str
    severity: str = "medium"
    suggested_resolution: Optional[str] = None


class Resolution(BaseModel):
    """Suggested resolution for a policy conflict."""
    resolution_id: str
    conflict_id: str
    description: str
    action: str
    priority: int = 0
    automatic: bool = False


class PolicyCheckpoint(BaseModel):
    """Checkpoint for policy versioning."""
    checkpoint_id: str
    timestamp: datetime
    description: str
    policy_snapshot: Dict[str, Any]
    created_by: User
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RollbackResult(BaseModel):
    """Result of a policy rollback operation."""
    success: bool
    checkpoint_id: str
    policies_restored: List[str] = Field(default_factory=list)
    policies_removed: List[str] = Field(default_factory=list)
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
