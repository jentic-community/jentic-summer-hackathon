"""
Agent Behavior Modification System

A comprehensive system for dynamically modifying agent behavior through
natural language commands and policy-based constraints.
"""

from .core import (
    BehaviorPolicyEngine,
    PolicyRule,
    BehaviorContext,
)
from .models import (
    PolicyDecision,
    AgentAction,
    ActionContext,
    User,
    SecurityLevel,
)
from .policies import (
    TimeBasedRule,
    UserBasedRule,
    ActionBasedRule,
    SecurityLevelRule,
    ContentBasedRule,
)
from .parser import PolicyParser, ModificationIntentClassifier
from .controller import RuntimeBehaviorController, BehaviorModifiedAgent
from .models import (
    ModificationRequest,
    ModificationResult,
    PolicyUpdateResult,
    ValidationResult,
)

__version__ = "0.1.0"
__all__ = [
    "BehaviorPolicyEngine",
    "PolicyRule",
    "PolicyDecision",
    "BehaviorContext",
    "AgentAction",
    "ActionContext",
    "User",
    "SecurityLevel",
    "TimeBasedRule",
    "UserBasedRule",
    "ActionBasedRule",
    "SecurityLevelRule",
    "ContentBasedRule",
    "PolicyParser",
    "ModificationIntentClassifier",
    "RuntimeBehaviorController",
    "BehaviorModifiedAgent",
    "ModificationRequest",
    "ModificationResult",
    "PolicyUpdateResult",
    "ValidationResult",
]
