"""
Natural Language Policy Parser for the Agent Behavior Modification System.
"""

import re
import uuid
from datetime import time
from typing import Any, Dict, List, Optional, Tuple
from .models import ModificationIntent, ValidationResult
from .core import PolicyRule
from .policies import (
    TimeBasedRule,
    UserBasedRule,
    ActionBasedRule,
    SecurityLevelRule,
    ContentBasedRule,
    create_policy_rule,
)
from .core import BehaviorPolicyEngine


class ModificationIntentClassifier:
    """Classifies the type of modification requested from natural language."""
    
    def __init__(self):
        # Define patterns for different types of modifications
        self.patterns = {
            ModificationIntent.TIME_RESTRICTION: [
                r'\b(only|just|during|between|from|to|until|after|before)\s+(weekdays?|weekends?|business\s+hours?|office\s+hours?|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                r'\b(9\s*am|10\s*am|11\s*am|12\s*pm|1\s*pm|2\s*pm|3\s*pm|4\s*pm|5\s*pm|6\s*pm|7\s*pm|8\s*pm|9\s*pm)',
                r'\b(morning|afternoon|evening|night|daytime|nighttime)',
                r'\b(weekday|weekend|business\s+hours?|office\s+hours?)',
            ],
            ModificationIntent.USER_RESTRICTION: [
                r'\b(block|deny|prevent|restrict)\s+(user|users?|person|people)',
                r'\b(only|just)\s+(allow|permit|let)\s+(user|users?|person|people)',
                r'\b(admin|administrator|manager|supervisor|employee|staff)',
                r'\b(email|user|account)\s+(block|deny|prevent)',
            ],
            ModificationIntent.ACTION_RESTRICTION: [
                r'\b(block|deny|prevent|restrict|stop|disable)\s+(email|send|delete|modify|change|update|create)',
                r'\b(only|just)\s+(allow|permit|let)\s+(read|view|get|fetch)',
                r'\b(don\'t|do\s+not|never)\s+(send|delete|modify|change|update|create)',
                r'\b(read\s*-?\s*only|readonly)',
            ],
            ModificationIntent.SECURITY_MODIFICATION: [
                r'\b(increase|raise|boost|enhance)\s+(security|safety|protection)',
                r'\b(decrease|lower|reduce)\s+(security|safety|protection)',
                r'\b(high|low|normal|critical)\s+(security|safety|protection)\s+(level)',
                r'\b(secure|safe|protected|restricted)',
            ],
            ModificationIntent.CONTENT_RESTRICTION: [
                r'\b(block|deny|prevent|restrict)\s+(content|text|message|information)',
                r'\b(don\'t|do\s+not|never)\s+(process|handle|deal\s+with)\s+(personal|sensitive|confidential)',
                r'\b(keyword|pattern|phrase)\s+(block|deny|prevent)',
                r'\b(content|text|message)\s+(filter|screening)',
            ],
        }
    
    def classify_intent(self, request: str) -> ModificationIntent:
        """Classify the type of modification requested."""
        request_lower = request.lower()
        
        # Count matches for each intent type
        intent_scores = {}
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, request_lower, re.IGNORECASE)
                score += len(matches)
            intent_scores[intent] = score
        
        # Return the intent with the highest score
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            if best_intent[1] > 0:
                return best_intent[0]
        
        # Default to general restriction if no clear pattern
        return ModificationIntent.GENERAL_RESTRICTION
    
    def extract_parameters(self, request: str, intent: ModificationIntent) -> Dict[str, Any]:
        """Extract specific parameters from natural language based on intent."""
        request_lower = request.lower()
        params = {}
        
        if intent == ModificationIntent.TIME_RESTRICTION:
            params.update(self._extract_time_parameters(request_lower))
        elif intent == ModificationIntent.USER_RESTRICTION:
            params.update(self._extract_user_parameters(request_lower))
        elif intent == ModificationIntent.ACTION_RESTRICTION:
            params.update(self._extract_action_parameters(request_lower))
        elif intent == ModificationIntent.SECURITY_MODIFICATION:
            params.update(self._extract_security_parameters(request_lower))
        elif intent == ModificationIntent.CONTENT_RESTRICTION:
            params.update(self._extract_content_parameters(request_lower))
        
        return params
    
    def _extract_time_parameters(self, request: str) -> Dict[str, Any]:
        """Extract time-related parameters."""
        params = {}
        
        # Extract days
        day_patterns = {
            'weekdays': [0, 1, 2, 3, 4],  # Monday to Friday
            'weekends': [5, 6],  # Saturday, Sunday
            'monday': [0], 'tuesday': [1], 'wednesday': [2], 'thursday': [3], 'friday': [4],
            'saturday': [5], 'sunday': [6]
        }
        
        for day_name, day_numbers in day_patterns.items():
            if day_name in request:
                if 'blocked' in request or 'not' in request:
                    params['blocked_days'] = day_numbers
                else:
                    params['allowed_days'] = day_numbers
        
        # Extract times
        time_pattern = r'(\d{1,2})\s*(am|pm)'
        times = re.findall(time_pattern, request)
        if times:
            time_objects = []
            for hour, period in times:
                hour = int(hour)
                if period.lower() == 'pm' and hour != 12:
                    hour += 12
                elif period.lower() == 'am' and hour == 12:
                    hour = 0
                time_objects.append(time(hour, 0))
            
            if 'after' in request or 'from' in request:
                params['allowed_times'] = time_objects
            elif 'before' in request or 'until' in request:
                params['blocked_times'] = time_objects
        
        return params
    
    def _extract_user_parameters(self, request: str) -> Dict[str, Any]:
        """Extract user-related parameters."""
        params = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, request)
        
        # Extract user roles
        role_patterns = ['admin', 'administrator', 'manager', 'supervisor', 'employee', 'staff']
        roles = [role for role in role_patterns if role in request]
        
        if 'block' in request or 'deny' in request or 'prevent' in request:
            if emails:
                params['blocked_users'] = emails
            if roles:
                params['blocked_roles'] = roles
        else:
            if emails:
                params['allowed_users'] = emails
            if roles:
                params['allowed_roles'] = roles
        
        return params
    
    def _extract_action_parameters(self, request: str) -> Dict[str, Any]:
        """Extract action-related parameters."""
        params = {}
        
        # Define action mappings
        action_mappings = {
            'email': ['send_email', 'email', 'mail'],
            'delete': ['delete', 'remove', 'erase'],
            'modify': ['modify', 'change', 'update', 'edit'],
            'create': ['create', 'add', 'insert'],
            'read': ['read', 'view', 'get', 'fetch', 'retrieve'],
        }
        
        restricted_actions = []
        allowed_actions = []
        
        for action_type, keywords in action_mappings.items():
            for keyword in keywords:
                if keyword in request:
                    if 'block' in request or 'deny' in request or 'prevent' in request or "don't" in request:
                        restricted_actions.append(action_type)
                    elif 'allow' in request or 'permit' in request:
                        allowed_actions.append(action_type)
        
        if restricted_actions:
            params['restricted_actions'] = restricted_actions
        if allowed_actions:
            params['allowed_actions'] = allowed_actions
        
        return params
    
    def _extract_security_parameters(self, request: str) -> Dict[str, Any]:
        """Extract security-related parameters."""
        params = {}
        
        # Extract security levels
        if 'high' in request and 'security' in request:
            params['required_level'] = 'high'
        elif 'low' in request and 'security' in request:
            params['required_level'] = 'low'
        elif 'critical' in request and 'security' in request:
            params['required_level'] = 'critical'
        elif 'normal' in request and 'security' in request:
            params['required_level'] = 'normal'
        
        return params
    
    def _extract_content_parameters(self, request: str) -> Dict[str, Any]:
        """Extract content-related parameters."""
        params = {}
        
        # Extract keywords (simple approach - can be enhanced)
        keyword_pattern = r'"([^"]+)"'
        keywords = re.findall(keyword_pattern, request)
        
        if keywords:
            params['blocked_patterns'] = keywords
        
        # Extract content types
        content_types = ['personal', 'sensitive', 'confidential', 'private']
        found_types = [ct for ct in content_types if ct in request]
        
        if found_types:
            params['content_filters'] = {
                'sensitive_patterns': {ct: rf'\b{ct}\b' for ct in found_types}
            }
        
        return params


class PolicyParser:
    """Parses natural language modification requests into structured policy rules."""
    
    def __init__(self):
        self.intent_classifier = ModificationIntentClassifier()
    
    def parse_modification_request(self, request: str) -> List[PolicyRule]:
        """Convert natural language modification request to structured policy rules."""
        try:
            # Classify the intent
            intent = self.intent_classifier.classify_intent(request)
            
            # Extract parameters
            parameters = self.intent_classifier.extract_parameters(request, intent)
            
            # Generate policy rules based on intent and parameters
            rules = self._generate_policy_rules(intent, parameters, request)
            
            return rules
        
        except Exception as e:
            # Return a basic restriction rule if parsing fails
            return [self._create_fallback_rule(request, str(e))]
    
    def validate_policy_rules(self, rules: List[PolicyRule]) -> ValidationResult:
        """Check for conflicts, impossibilities, and safety issues."""
        errors = []
        warnings = []
        suggestions = []
        
        for rule in rules:
            # Basic validation
            if not rule.rule_id:
                errors.append(f"Rule missing ID: {rule}")
            
            if not rule.description:
                warnings.append(f"Rule missing description: {rule}")
        
        # Check for conflicts between rules
        conflicts = self._detect_rule_conflicts(rules)
        if conflicts:
            errors.extend(conflicts)
        
        # Check for safety issues
        safety_issues = self._check_safety_issues(rules)
        if safety_issues:
            warnings.extend(safety_issues)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _generate_policy_rules(self, intent: ModificationIntent, parameters: Dict[str, Any], 
                              original_request: str) -> List[PolicyRule]:
        """Generate policy rules based on intent and parameters."""
        rules = []
        rule_id = str(uuid.uuid4())
        
        if intent == ModificationIntent.TIME_RESTRICTION:
            if parameters:
                rule = TimeBasedRule(
                    rule_id=rule_id,
                    description=f"Time-based restriction: {original_request}",
                    **parameters
                )
                rules.append(rule)
        
        elif intent == ModificationIntent.USER_RESTRICTION:
            if parameters:
                rule = UserBasedRule(
                    rule_id=rule_id,
                    description=f"User-based restriction: {original_request}",
                    **parameters
                )
                rules.append(rule)
        
        elif intent == ModificationIntent.ACTION_RESTRICTION:
            if parameters:
                rule = ActionBasedRule(
                    rule_id=rule_id,
                    description=f"Action-based restriction: {original_request}",
                    **parameters
                )
                rules.append(rule)
        
        elif intent == ModificationIntent.SECURITY_MODIFICATION:
            if parameters:
                rule = SecurityLevelRule(
                    rule_id=rule_id,
                    description=f"Security level modification: {original_request}",
                    **parameters
                )
                rules.append(rule)
        
        elif intent == ModificationIntent.CONTENT_RESTRICTION:
            if parameters:
                rule = ContentBasedRule(
                    rule_id=rule_id,
                    description=f"Content-based restriction: {original_request}",
                    **parameters
                )
                rules.append(rule)
        
        # If no specific parameters were extracted, create a general restriction
        if not rules:
            rules.append(self._create_general_restriction_rule(original_request))
        
        return rules
    
    def _create_fallback_rule(self, request: str, error: str) -> PolicyRule:
        """Create a fallback rule when parsing fails."""
        return ActionBasedRule(
            rule_id=str(uuid.uuid4()),
            description=f"General restriction (parsing failed): {request}",
            restricted_actions=["all"],
            metadata={"parsing_error": error, "fallback": True}
        )
    
    def _create_general_restriction_rule(self, request: str) -> PolicyRule:
        """Create a general restriction rule when intent is unclear."""
        return ActionBasedRule(
            rule_id=str(uuid.uuid4()),
            description=f"General restriction: {request}",
            restricted_actions=["all"],
            metadata={"general_restriction": True}
        )
    
    def _detect_rule_conflicts(self, rules: List[PolicyRule]) -> List[str]:
        """Detect conflicts between policy rules."""
        conflicts = []
        
        # Check for duplicate rule IDs
        rule_ids = [rule.rule_id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            conflicts.append("Duplicate rule IDs detected")
        
        # Check for contradictory time rules
        time_rules = [r for r in rules if isinstance(r, TimeBasedRule)]
        if len(time_rules) > 1:
            # Check for overlapping time restrictions
            for i, rule1 in enumerate(time_rules):
                for rule2 in time_rules[i+1:]:
                    if self._time_rules_conflict(rule1, rule2):
                        conflicts.append(f"Conflicting time rules: {rule1.rule_id} and {rule2.rule_id}")
        
        return conflicts
    
    def _time_rules_conflict(self, rule1: TimeBasedRule, rule2: TimeBasedRule) -> bool:
        """Check if two time rules conflict."""
        # Simple conflict detection - can be enhanced
        if rule1.allowed_days and rule2.blocked_days:
            for day in rule1.allowed_days:
                if day in rule2.blocked_days:
                    return True
        
        if rule2.allowed_days and rule1.blocked_days:
            for day in rule2.allowed_days:
                if day in rule1.blocked_days:
                    return True
        
        return False
    
    def _check_safety_issues(self, rules: List[PolicyRule]) -> List[str]:
        """Check for potential safety issues in policy rules."""
        issues = []
        
        # Check for overly restrictive rules
        for rule in rules:
            if isinstance(rule, ActionBasedRule):
                if rule.restricted_actions and "all" in rule.restricted_actions:
                    issues.append(f"Rule {rule.rule_id} blocks all actions - may be too restrictive")
            
            if isinstance(rule, UserBasedRule):
                if rule.blocked_users and len(rule.blocked_users) > 10:
                    issues.append(f"Rule {rule.rule_id} blocks many users - verify this is intentional")
        
        return issues


class LLMPolicyGenerator:
    """Uses LLM to generate more sophisticated policy rules."""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def generate_policy_from_request(self, request: str, context: Dict[str, Any]) -> List[PolicyRule]:
        """Use LLM to convert natural language to policy rules."""
        if not self.llm:
            # Fallback to basic parser if no LLM available
            parser = PolicyParser()
            return parser.parse_modification_request(request)
        
        # TODO: Implement LLM-based policy generation
        # This would involve sending the request to an LLM with a prompt
        # that asks it to generate structured policy rules
        
        prompt = f"""
        Convert this behavior modification request into structured policy rules:
        Request: "{request}"
        Context: {context}
        
        Generate specific, enforceable policy rules that implement this request.
        Consider edge cases and potential conflicts.
        """
        
        # For now, fall back to basic parser
        parser = PolicyParser()
        return parser.parse_modification_request(request)
    
    def validate_generated_policy(self, policy: PolicyRule, original_request: str) -> bool:
        """Verify the generated policy matches the intent."""
        # TODO: Implement LLM-based validation
        return True
