#!/usr/bin/env python3
"""
Simple Flask web server for the Agent Behavior Modification System frontend.
This provides both the web interface and API endpoints for the behavior modification system.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add the parent directory to the path so we can import the behavior modification system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from behavior_modification import (
        BehaviorPolicyEngine,
        TimeBasedRule,
        UserBasedRule,
        ActionBasedRule,
        ContentBasedRule,
        PolicyParser,
        RuntimeBehaviorController,
        BehaviorModifiedAgent,
        User,
        SecurityLevel,
        BehaviorContext,
        AgentAction,
        ActionContext
    )
except ImportError as e:
    print(f"Warning: Could not import behavior modification system: {e}")
    print("Running in demo mode with mock data")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global state for the web interface
policies = []
audit_log = []
agent_status = {
    "status": "Active",
    "policies": 0,
    "last_activity": datetime.now().isoformat(),
    "uptime": "0 minutes"
}

# Initialize the behavior modification system if available
try:
    policy_engine = BehaviorPolicyEngine()
    policy_parser = PolicyParser()
    behavior_controller = RuntimeBehaviorController(policy_engine)
    agent = BehaviorModifiedAgent(behavior_controller)
    system_available = True
except Exception as e:
    print(f"Warning: Could not initialize behavior modification system: {e}")
    system_available = False

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)."""
    return send_from_directory('.', filename)

@app.route('/api/status')
def get_status():
    """Get system status."""
    return jsonify({
        "system_available": system_available,
        "active_policies": len(policies),
        "recent_actions": len(audit_log),
        "blocked_actions": len([entry for entry in audit_log if not entry.get('allowed', True)]),
        "allowed_actions": len([entry for entry in audit_log if entry.get('allowed', True)])
    })

@app.route('/api/policies', methods=['GET'])
def get_policies():
    """Get all active policies."""
    return jsonify(policies)

@app.route('/api/policies', methods=['POST'])
def create_policy():
    """Create a new policy."""
    try:
        data = request.json
        
        if not data.get('description'):
            return jsonify({"error": "Description is required"}), 400
        
        policy = {
            "id": generate_id(),
            "type": data.get('type', 'action'),
            "description": data['description'],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        # Add type-specific data
        if data.get('type') == 'time':
            policy.update({
                "allowed_days": data.get('allowed_days', []),
                "start_time": data.get('start_time', '09:00'),
                "end_time": data.get('end_time', '17:00')
            })
        elif data.get('type') == 'user':
            policy.update({
                "blocked_users": data.get('blocked_users', []),
                "blocked_roles": data.get('blocked_roles', [])
            })
        elif data.get('type') == 'action':
            policy.update({
                "restricted_actions": data.get('restricted_actions', [])
            })
        elif data.get('type') == 'content':
            policy.update({
                "blocked_patterns": data.get('blocked_patterns', [])
            })
        
        policies.append(policy)
        
        # If the behavior modification system is available, add the policy there too
        if system_available:
            try:
                add_policy_to_engine(policy)
            except Exception as e:
                print(f"Warning: Could not add policy to engine: {e}")
        
        return jsonify({"success": True, "policy": policy})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/policies/<policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    """Delete a policy."""
    global policies
    policies = [p for p in policies if p['id'] != policy_id]
    
    # If the behavior modification system is available, remove the policy there too
    if system_available:
        try:
            policy_engine.remove_policy(policy_id)
        except Exception as e:
            print(f"Warning: Could not remove policy from engine: {e}")
    
    return jsonify({"success": True})

@app.route('/api/audit-log')
def get_audit_log():
    """Get audit log entries."""
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'blocked':
        filtered_log = [entry for entry in audit_log if not entry.get('allowed', True)]
    elif filter_type == 'allowed':
        filtered_log = [entry for entry in audit_log if entry.get('allowed', True)]
    else:
        filtered_log = audit_log
    
    return jsonify(filtered_log)

@app.route('/api/test-goal', methods=['POST'])
def test_goal():
    """Test an agent goal against active policies."""
    try:
        data = request.json
        goal = data.get('goal', '')
        user_name = data.get('user', 'Admin User')
        
        if not goal:
            return jsonify({"error": "Goal is required"}), 400
        
        # Process the goal
        result = process_goal(goal, user_name)
        
        # Add to audit log
        audit_entry = {
            "id": generate_id(),
            "timestamp": datetime.now().isoformat(),
            "action": "goal_processing",
            "goal": goal,
            "user": user_name,
            "allowed": result['allowed'],
            "reason": result['reason']
        }
        
        audit_log.insert(0, audit_entry)
        
        # Update agent status
        agent_status["last_activity"] = datetime.now().isoformat()
        agent_status["policies"] = len(policies)
        
        return jsonify({
            "success": True,
            "result": result,
            "audit_entry": audit_entry
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/natural-language', methods=['POST'])
def natural_language_policy():
    """Create a policy from natural language description."""
    try:
        data = request.json
        request_text = data.get('request', '')
        
        if not request_text:
            return jsonify({"error": "Request text is required"}), 400
        
        # Parse natural language request
        policy = parse_natural_language(request_text)
        
        if policy:
            policies.append(policy)
            
            # If the behavior modification system is available, add the policy there too
            if system_available:
                try:
                    add_policy_to_engine(policy)
                except Exception as e:
                    print(f"Warning: Could not add policy to engine: {e}")
            
            return jsonify({
                "success": True,
                "policy": policy
            })
        else:
            return jsonify({
                "error": "Could not understand the request. Please try a different description."
            }), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo/<demo_type>', methods=['POST'])
def run_demo(demo_type):
    """Run a demo scenario."""
    try:
        demo_policies = []
        
        if demo_type == 'basic':
            demo_policies = [
                {
                    "id": generate_id(),
                    "type": "time",
                    "description": "Only allow operations during business hours",
                    "allowed_days": [0, 1, 2, 3, 4],
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "created_at": datetime.now().isoformat(),
                    "active": True
                },
                {
                    "id": generate_id(),
                    "type": "action",
                    "description": "Prevent deletion operations",
                    "restricted_actions": ["delete", "remove"],
                    "created_at": datetime.now().isoformat(),
                    "active": True
                }
            ]
        elif demo_type == 'security':
            demo_policies = [{
                "id": generate_id(),
                "type": "action",
                "description": "Require high security for destructive operations",
                "restricted_actions": ["delete", "format", "wipe"],
                "created_at": datetime.now().isoformat(),
                "active": True
            }]
        elif demo_type == 'conflicts':
            demo_policies = [
                {
                    "id": generate_id(),
                    "type": "time",
                    "description": "Only allow operations on weekdays",
                    "allowed_days": [0, 1, 2, 3, 4],
                    "created_at": datetime.now().isoformat(),
                    "active": True
                },
                {
                    "id": generate_id(),
                    "type": "time",
                    "description": "Only allow operations on weekends",
                    "allowed_days": [5, 6],
                    "created_at": datetime.now().isoformat(),
                    "active": True
                }
            ]
        elif demo_type == 'content':
            demo_policies = [{
                "id": generate_id(),
                "type": "content",
                "description": "Block personal information like SSN and email addresses",
                "blocked_patterns": [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
                "created_at": datetime.now().isoformat(),
                "active": True
            }]
        else:
            return jsonify({"error": "Unknown demo type"}), 400
        
        policies.extend(demo_policies)
        
        # If the behavior modification system is available, add the policies there too
        if system_available:
            try:
                for policy in demo_policies:
                    add_policy_to_engine(policy)
            except Exception as e:
                print(f"Warning: Could not add demo policies to engine: {e}")
        
        return jsonify({
            "success": True,
            "policies_added": len(demo_policies)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_goal(goal, user_name):
    """Process an agent goal against active policies."""
    lower_goal = goal.lower()
    
    # Check against active policies
    for policy in policies:
        if not policy.get('active', True):
            continue
        
        if policy['type'] == 'action':
            restricted_actions = policy.get('restricted_actions', [])
            for action in restricted_actions:
                if action.lower() in lower_goal:
                    return {
                        "allowed": False,
                        "reason": f"Action '{action}' is restricted by policy: {policy['description']}"
                    }
        
        elif policy['type'] == 'time':
            now = datetime.now()
            current_day = now.weekday()
            current_time = now.strftime('%H:%M')
            
            allowed_days = policy.get('allowed_days', [])
            if allowed_days and current_day not in allowed_days:
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                return {
                    "allowed": False,
                    "reason": f"Action not allowed on {day_names[current_day]}"
                }
            
            start_time = policy.get('start_time')
            end_time = policy.get('end_time')
            if start_time and end_time:
                if current_time < start_time or current_time > end_time:
                    return {
                        "allowed": False,
                        "reason": f"Action not allowed outside business hours ({start_time} - {end_time})"
                    }
        
        elif policy['type'] == 'user':
            blocked_users = policy.get('blocked_users', [])
            if user_name in blocked_users:
                return {
                    "allowed": False,
                    "reason": f"User '{user_name}' is blocked by policy: {policy['description']}"
                }
    
    return {
        "allowed": True,
        "reason": "Goal allowed by all active policies"
    }

def parse_natural_language(request_text):
    """Parse natural language request into a policy."""
    lower_request = request_text.lower()
    
    # Simple pattern matching for demo purposes
    if 'email' in lower_request and ('block' in lower_request or 'prevent' in lower_request):
        return {
            "id": generate_id(),
            "type": "action",
            "description": f"Block email operations: {request_text}",
            "restricted_actions": ["email", "send_email", "mail"],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
    
    if 'business hours' in lower_request or 'work hours' in lower_request:
        return {
            "id": generate_id(),
            "type": "time",
            "description": f"Time restriction: {request_text}",
            "allowed_days": [0, 1, 2, 3, 4],  # Monday to Friday
            "start_time": "09:00",
            "end_time": "17:00",
            "created_at": datetime.now().isoformat(),
            "active": True
        }
    
    if 'delete' in lower_request or 'remove' in lower_request:
        return {
            "id": generate_id(),
            "type": "action",
            "description": f"Prevent deletion: {request_text}",
            "restricted_actions": ["delete", "remove", "erase"],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
    
    if 'personal' in lower_request or 'ssn' in lower_request or 'sensitive' in lower_request:
        return {
            "id": generate_id(),
            "type": "content",
            "description": f"Content filtering: {request_text}",
            "blocked_patterns": [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
    
    return None

def add_policy_to_engine(policy):
    """Add a policy to the behavior modification engine."""
    if not system_available:
        return
    
    try:
        if policy['type'] == 'time':
            rule = TimeBasedRule(
                rule_id=policy['id'],
                allowed_days=policy.get('allowed_days', []),
                start_time=policy.get('start_time', '09:00'),
                end_time=policy.get('end_time', '17:00'),
                description=policy['description']
            )
        elif policy['type'] == 'user':
            rule = UserBasedRule(
                rule_id=policy['id'],
                blocked_users=policy.get('blocked_users', []),
                blocked_roles=policy.get('blocked_roles', []),
                description=policy['description']
            )
        elif policy['type'] == 'action':
            rule = ActionBasedRule(
                rule_id=policy['id'],
                restricted_actions=policy.get('restricted_actions', []),
                description=policy['description']
            )
        elif policy['type'] == 'content':
            rule = ContentBasedRule(
                rule_id=policy['id'],
                blocked_patterns=policy.get('blocked_patterns', []),
                description=policy['description']
            )
        else:
            return
        
        policy_engine.add_policy(rule)
    
    except Exception as e:
        print(f"Error adding policy to engine: {e}")

def generate_id():
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())

if __name__ == '__main__':
    print("🤖 Agent Behavior Modification System - Web Interface")
    print("=" * 60)
    print(f"System available: {system_available}")
    print("Starting web server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()
    
    # Add some sample data for demo
    if not policies:
        sample_policy = {
            "id": generate_id(),
            "type": "action",
            "description": "Block all email sending operations",
            "restricted_actions": ["email", "send_email"],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        policies.append(sample_policy)
        
        if system_available:
            try:
                add_policy_to_engine(sample_policy)
            except Exception as e:
                print(f"Warning: Could not add sample policy to engine: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
