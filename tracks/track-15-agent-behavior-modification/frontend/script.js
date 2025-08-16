// Global state
let currentUser = {
    id: 'admin',
    email: 'admin@example.com',
    name: 'Admin User',
    role: 'admin',
    is_admin: true
};

let currentPolicyType = 'time';
let policies = [];
let auditLog = [];
let agentStatus = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadPolicies();
    loadAuditLog();
    loadAgentStatus();
    updateUserDisplay();
});

// Dashboard Functions
function loadDashboard() {
    // Simulate loading dashboard data
    updateStats({
        activePolicies: policies.length,
        recentActions: auditLog.length,
        blockedActions: auditLog.filter(entry => !entry.allowed).length,
        allowedActions: auditLog.filter(entry => entry.allowed).length
    });
}

function updateStats(stats) {
    document.getElementById('active-policies-count').textContent = stats.activePolicies;
    document.getElementById('recent-actions').textContent = stats.recentActions;
    document.getElementById('blocked-actions').textContent = stats.blockedActions;
    document.getElementById('allowed-actions').textContent = stats.allowedActions;
}

// Tab Management
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load tab-specific data
    switch(tabName) {
        case 'policies':
            loadPolicies();
            break;
        case 'audit':
            loadAuditLog();
            break;
        case 'agent':
            loadAgentStatus();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

// Policy Management
function loadPolicies() {
    // Simulate API call to get policies
    const policiesList = document.getElementById('policies-list');
    
    if (policies.length === 0) {
        policiesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shield-alt" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                <h3>No Active Policies</h3>
                <p>Create your first policy to start controlling agent behavior.</p>
                <button class="btn-primary" onclick="showModal('add-policy')">
                    <i class="fas fa-plus"></i>
                    Add Policy
                </button>
            </div>
        `;
        return;
    }
    
    policiesList.innerHTML = policies.map(policy => `
        <div class="policy-card">
            <div class="policy-header">
                <div>
                    <div class="policy-title">${policy.description}</div>
                    <div class="policy-type">${getPolicyTypeName(policy.type)}</div>
                </div>
                <div class="policy-actions">
                    <button class="btn-secondary btn-small" onclick="editPolicy('${policy.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-danger btn-small" onclick="removePolicy('${policy.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="policy-description">
                ${getPolicyDescription(policy)}
            </div>
        </div>
    `).join('');
}

function getPolicyTypeName(type) {
    const types = {
        'time': 'Time-based',
        'user': 'User-based',
        'action': 'Action-based',
        'content': 'Content-based'
    };
    return types[type] || type;
}

function getPolicyDescription(policy) {
    switch(policy.type) {
        case 'time':
            return `Restricts actions based on time constraints`;
        case 'user':
            return `Controls access based on user identity or role`;
        case 'action':
            return `Blocks specific types of actions`;
        case 'content':
            return `Filters content based on patterns`;
        default:
            return policy.description;
    }
}

// Modal Management
function showModal(modalId) {
    const modal = document.getElementById(`${modalId}-modal`);
    modal.classList.add('active');
    
    // Load modal-specific content
    switch(modalId) {
        case 'add-policy':
            loadPolicyForm();
            break;
        case 'test-goal':
            document.getElementById('modal-user').textContent = currentUser.name;
            break;
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(`${modalId}-modal`);
    modal.classList.remove('active');
    
    // Clear form data
    if (modalId === 'add-policy') {
        document.getElementById('policy-form').innerHTML = '';
    }
}

// Policy Form Management
function selectPolicyType(type) {
    currentPolicyType = type;
    
    // Update active button
    document.querySelectorAll('.policy-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load form for selected type
    loadPolicyForm();
}

function loadPolicyForm() {
    const formContainer = document.getElementById('policy-form');
    
    switch(currentPolicyType) {
        case 'time':
            formContainer.innerHTML = `
                <div class="form-group">
                    <label for="policy-description">Description</label>
                    <input type="text" id="policy-description" placeholder="e.g., Only allow operations during business hours">
                </div>
                <div class="form-group">
                    <label for="allowed-days">Allowed Days</label>
                    <select id="allowed-days" multiple>
                        <option value="0">Monday</option>
                        <option value="1">Tuesday</option>
                        <option value="2">Wednesday</option>
                        <option value="3">Thursday</option>
                        <option value="4">Friday</option>
                        <option value="5">Saturday</option>
                        <option value="6">Sunday</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="start-time">Start Time</label>
                    <input type="time" id="start-time" value="09:00">
                </div>
                <div class="form-group">
                    <label for="end-time">End Time</label>
                    <input type="time" id="end-time" value="17:00">
                </div>
            `;
            break;
            
        case 'user':
            formContainer.innerHTML = `
                <div class="form-group">
                    <label for="policy-description">Description</label>
                    <input type="text" id="policy-description" placeholder="e.g., Block specific users from accessing sensitive data">
                </div>
                <div class="form-group">
                    <label for="blocked-users">Blocked Users (comma-separated)</label>
                    <input type="text" id="blocked-users" placeholder="e.g., spam@example.com, guest@example.com">
                </div>
                <div class="form-group">
                    <label for="blocked-roles">Blocked Roles (comma-separated)</label>
                    <input type="text" id="blocked-roles" placeholder="e.g., guest, visitor">
                </div>
            `;
            break;
            
        case 'action':
            formContainer.innerHTML = `
                <div class="form-group">
                    <label for="policy-description">Description</label>
                    <input type="text" id="policy-description" placeholder="e.g., Prevent deletion operations">
                </div>
                <div class="form-group">
                    <label for="restricted-actions">Restricted Actions (comma-separated)</label>
                    <input type="text" id="restricted-actions" placeholder="e.g., delete, remove, format">
                </div>
            `;
            break;
            
        case 'content':
            formContainer.innerHTML = `
                <div class="form-group">
                    <label for="policy-description">Description</label>
                    <input type="text" id="policy-description" placeholder="e.g., Block personal information like SSN and email addresses">
                </div>
                <div class="form-group">
                    <label for="blocked-patterns">Blocked Patterns (one per line)</label>
                    <textarea id="blocked-patterns" placeholder="e.g., \\b\\d{3}-\\d{2}-\\d{4}\\b (SSN pattern)&#10;\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b (Email pattern)"></textarea>
                </div>
            `;
            break;
    }
}

function submitPolicy() {
    const description = document.getElementById('policy-description')?.value;
    
    if (!description) {
        showToast('Please provide a policy description', 'error');
        return;
    }
    
    // Create policy object based on type
    const policy = {
        id: generateId(),
        type: currentPolicyType,
        description: description,
        created_at: new Date().toISOString(),
        active: true
    };
    
    // Add type-specific data
    switch(currentPolicyType) {
        case 'time':
            const allowedDays = Array.from(document.getElementById('allowed-days').selectedOptions).map(opt => parseInt(opt.value));
            policy.allowed_days = allowedDays;
            policy.start_time = document.getElementById('start-time').value;
            policy.end_time = document.getElementById('end-time').value;
            break;
            
        case 'user':
            policy.blocked_users = document.getElementById('blocked-users').value.split(',').map(u => u.trim()).filter(u => u);
            policy.blocked_roles = document.getElementById('blocked-roles').value.split(',').map(r => r.trim()).filter(r => r);
            break;
            
        case 'action':
            policy.restricted_actions = document.getElementById('restricted-actions').value.split(',').map(a => a.trim()).filter(a => a);
            break;
            
        case 'content':
            policy.blocked_patterns = document.getElementById('blocked-patterns').value.split('\n').map(p => p.trim()).filter(p => p);
            break;
    }
    
    // Add policy to list
    policies.push(policy);
    
    // Update UI
    loadPolicies();
    loadDashboard();
    closeModal('add-policy');
    showToast('Policy created successfully', 'success');
}

// Natural Language Policy
function submitNaturalLanguage() {
    const request = document.getElementById('nl-input').value;
    
    if (!request) {
        showToast('Please describe the behavior modification you want', 'error');
        return;
    }
    
    // Simulate natural language processing
    const policy = createPolicyFromNaturalLanguage(request);
    
    if (policy) {
        policies.push(policy);
        loadPolicies();
        loadDashboard();
        closeModal('natural-language');
        showToast('Policy created from natural language', 'success');
    } else {
        showToast('Could not understand the request. Please try a different description.', 'error');
    }
}

function createPolicyFromNaturalLanguage(request) {
    const lowerRequest = request.toLowerCase();
    
    // Simple pattern matching for demo purposes
    if (lowerRequest.includes('email') && (lowerRequest.includes('block') || lowerRequest.includes('prevent'))) {
        return {
            id: generateId(),
            type: 'action',
            description: `Block email operations: ${request}`,
            restricted_actions: ['email', 'send_email', 'mail'],
            created_at: new Date().toISOString(),
            active: true
        };
    }
    
    if (lowerRequest.includes('business hours') || lowerRequest.includes('work hours')) {
        return {
            id: generateId(),
            type: 'time',
            description: `Time restriction: ${request}`,
            allowed_days: [0, 1, 2, 3, 4], // Monday to Friday
            start_time: '09:00',
            end_time: '17:00',
            created_at: new Date().toISOString(),
            active: true
        };
    }
    
    if (lowerRequest.includes('delete') || lowerRequest.includes('remove')) {
        return {
            id: generateId(),
            type: 'action',
            description: `Prevent deletion: ${request}`,
            restricted_actions: ['delete', 'remove', 'erase'],
            created_at: new Date().toISOString(),
            active: true
        };
    }
    
    if (lowerRequest.includes('personal') || lowerRequest.includes('ssn') || lowerRequest.includes('sensitive')) {
        return {
            id: generateId(),
            type: 'content',
            description: `Content filtering: ${request}`,
            blocked_patterns: [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            created_at: new Date().toISOString(),
            active: true
        };
    }
    
    return null;
}

// Agent Goal Testing
function submitGoal() {
    const goal = document.getElementById('goal-input').value;
    
    if (!goal) {
        showToast('Please enter a goal for the agent', 'error');
        return;
    }
    
    // Simulate agent goal processing
    const result = processAgentGoal(goal);
    
    // Add to audit log
    const auditEntry = {
        id: generateId(),
        timestamp: new Date().toISOString(),
        action: 'goal_processing',
        goal: goal,
        user: currentUser.name,
        allowed: result.allowed,
        reason: result.reason
    };
    
    auditLog.unshift(auditEntry);
    
    // Update UI
    loadAuditLog();
    loadDashboard();
    closeModal('test-goal');
    
    showToast(result.allowed ? 'Goal processed successfully' : 'Goal blocked by policy', result.allowed ? 'success' : 'warning');
}

function processAgentGoal(goal) {
    const lowerGoal = goal.toLowerCase();
    
    // Check against active policies
    for (const policy of policies) {
        if (!policy.active) continue;
        
        switch(policy.type) {
            case 'action':
                if (policy.restricted_actions) {
                    for (const action of policy.restricted_actions) {
                        if (lowerGoal.includes(action.toLowerCase())) {
                            return {
                                allowed: false,
                                reason: `Action '${action}' is restricted by policy: ${policy.description}`
                            };
                        }
                    }
                }
                break;
                
            case 'time':
                const now = new Date();
                const currentDay = now.getDay();
                const currentTime = now.toTimeString().slice(0, 5);
                
                if (policy.allowed_days && !policy.allowed_days.includes(currentDay)) {
                    return {
                        allowed: false,
                        reason: `Action not allowed on day ${currentDay} (${getDayName(currentDay)})`
                    };
                }
                
                if (policy.start_time && policy.end_time) {
                    if (currentTime < policy.start_time || currentTime > policy.end_time) {
                        return {
                            allowed: false,
                            reason: `Action not allowed outside business hours (${policy.start_time} - ${policy.end_time})`
                        };
                    }
                }
                break;
        }
    }
    
    return {
        allowed: true,
        reason: 'Goal allowed by all active policies'
    };
}

// Audit Log Management
function loadAuditLog() {
    const auditContainer = document.getElementById('audit-log');
    
    if (auditLog.length === 0) {
        auditContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-history" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                <h3>No Audit Log Entries</h3>
                <p>Audit log entries will appear here when you test agent goals or modify policies.</p>
            </div>
        `;
        return;
    }
    
    auditContainer.innerHTML = auditLog.map(entry => `
        <div class="audit-entry">
            <div class="audit-icon ${entry.allowed ? 'allowed' : 'blocked'}">
                <i class="fas fa-${entry.allowed ? 'check' : 'ban'}"></i>
            </div>
            <div class="audit-content">
                <div class="audit-action">${entry.action === 'goal_processing' ? 'Goal Processing' : entry.action}</div>
                <div class="audit-details">
                    ${entry.goal ? `Goal: "${entry.goal}"` : ''}
                    ${entry.reason ? `<br>Reason: ${entry.reason}` : ''}
                </div>
            </div>
            <div class="audit-time">
                ${formatTime(entry.timestamp)}
            </div>
        </div>
    `).join('');
}

function filterAuditLog() {
    const filter = document.getElementById('audit-filter').value;
    const filteredLog = filter === 'all' ? auditLog : 
                       filter === 'blocked' ? auditLog.filter(entry => !entry.allowed) :
                       auditLog.filter(entry => entry.allowed);
    
    const auditContainer = document.getElementById('audit-log');
    auditContainer.innerHTML = filteredLog.map(entry => `
        <div class="audit-entry">
            <div class="audit-icon ${entry.allowed ? 'allowed' : 'blocked'}">
                <i class="fas fa-${entry.allowed ? 'check' : 'ban'}"></i>
            </div>
            <div class="audit-content">
                <div class="audit-action">${entry.action === 'goal_processing' ? 'Goal Processing' : entry.action}</div>
                <div class="audit-details">
                    ${entry.goal ? `Goal: "${entry.goal}"` : ''}
                    ${entry.reason ? `<br>Reason: ${entry.reason}` : ''}
                </div>
            </div>
            <div class="audit-time">
                ${formatTime(entry.timestamp)}
            </div>
        </div>
    `).join('');
}

// Agent Status Management
function loadAgentStatus() {
    const statusContent = document.getElementById('agent-status-content');
    const recentGoals = document.getElementById('recent-goals');
    
    // Simulate agent status
    const status = {
        status: 'Active',
        policies: policies.length,
        lastActivity: new Date().toISOString(),
        uptime: '2 hours 15 minutes'
    };
    
    statusContent.innerHTML = `
        <div class="status-item">
            <strong>Status:</strong> <span class="status-active">${status.status}</span>
        </div>
        <div class="status-item">
            <strong>Active Policies:</strong> ${status.policies}
        </div>
        <div class="status-item">
            <strong>Last Activity:</strong> ${formatTime(status.lastActivity)}
        </div>
        <div class="status-item">
            <strong>Uptime:</strong> ${status.uptime}
        </div>
    `;
    
    // Show recent goals
    const recent = auditLog.filter(entry => entry.action === 'goal_processing').slice(0, 5);
    recentGoals.innerHTML = recent.length > 0 ? recent.map(entry => `
        <div class="goal-item">
            <div class="goal-text">${entry.goal}</div>
            <div class="goal-status ${entry.allowed ? 'allowed' : 'blocked'}">
                ${entry.allowed ? '✓ Allowed' : '✗ Blocked'}
            </div>
            <div class="goal-time">${formatTime(entry.timestamp)}</div>
        </div>
    `).join('') : '<p>No recent goals</p>';
}

// Analytics Management
function loadAnalytics() {
    // Simulate analytics data
    const actionData = {
        labels: ['Allowed', 'Blocked'],
        datasets: [{
            data: [
                auditLog.filter(entry => entry.allowed).length,
                auditLog.filter(entry => !entry.allowed).length
            ],
            backgroundColor: ['#28a745', '#dc3545']
        }]
    };
    
    const policyData = {
        labels: policies.map(p => p.type),
        datasets: [{
            data: policies.map(p => 1),
            backgroundColor: ['#667eea', '#f093fb', '#4facfe', '#43e97b']
        }]
    };
    
    // Create charts (simplified for demo)
    const actionChart = document.getElementById('action-chart');
    const policyChart = document.getElementById('policy-chart');
    
    actionChart.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <h4>Action Distribution</h4>
            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
                <div>
                    <div style="width: 50px; height: 50px; background: #28a745; border-radius: 50%; margin: 0 auto;"></div>
                    <p>Allowed: ${actionData.datasets[0].data[0]}</p>
                </div>
                <div>
                    <div style="width: 50px; height: 50px; background: #dc3545; border-radius: 50%; margin: 0 auto;"></div>
                    <p>Blocked: ${actionData.datasets[0].data[1]}</p>
                </div>
            </div>
        </div>
    `;
    
    policyChart.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <h4>Policy Distribution</h4>
            <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                ${policyData.labels.map((label, i) => `
                    <div>
                        <div style="width: 40px; height: 40px; background: ${policyData.datasets[0].backgroundColor[i]}; border-radius: 50%; margin: 0 auto;"></div>
                        <p style="font-size: 0.8rem;">${label}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Demo Scenarios
function runDemo(demoType) {
    closeModal('demo-scenarios');
    
    switch(demoType) {
        case 'basic':
            runBasicDemo();
            break;
        case 'security':
            runSecurityDemo();
            break;
        case 'conflicts':
            runConflictsDemo();
            break;
        case 'content':
            runContentDemo();
            break;
    }
}

function runBasicDemo() {
    // Add sample policies
    const demoPolicies = [
        {
            id: generateId(),
            type: 'time',
            description: 'Only allow operations during business hours',
            allowed_days: [0, 1, 2, 3, 4],
            start_time: '09:00',
            end_time: '17:00',
            created_at: new Date().toISOString(),
            active: true
        },
        {
            id: generateId(),
            type: 'action',
            description: 'Prevent deletion operations',
            restricted_actions: ['delete', 'remove'],
            created_at: new Date().toISOString(),
            active: true
        }
    ];
    
    policies.push(...demoPolicies);
    loadPolicies();
    loadDashboard();
    showToast('Basic demo policies added', 'success');
}

function runSecurityDemo() {
    const securityPolicy = {
        id: generateId(),
        type: 'action',
        description: 'Require high security for destructive operations',
        restricted_actions: ['delete', 'format', 'wipe'],
        created_at: new Date().toISOString(),
        active: true
    };
    
    policies.push(securityPolicy);
    loadPolicies();
    loadDashboard();
    showToast('Security demo policy added', 'success');
}

function runConflictsDemo() {
    const conflictingPolicies = [
        {
            id: generateId(),
            type: 'time',
            description: 'Only allow operations on weekdays',
            allowed_days: [0, 1, 2, 3, 4],
            created_at: new Date().toISOString(),
            active: true
        },
        {
            id: generateId(),
            type: 'time',
            description: 'Only allow operations on weekends',
            allowed_days: [5, 6],
            created_at: new Date().toISOString(),
            active: true
        }
    ];
    
    policies.push(...conflictingPolicies);
    loadPolicies();
    loadDashboard();
    showToast('Conflicting demo policies added', 'warning');
}

function runContentDemo() {
    const contentPolicy = {
        id: generateId(),
        type: 'content',
        description: 'Block personal information like SSN and email addresses',
        blocked_patterns: [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
        created_at: new Date().toISOString(),
        active: true
    };
    
    policies.push(contentPolicy);
    loadPolicies();
    loadDashboard();
    showToast('Content filtering demo policy added', 'success');
}

// Utility Functions
function generateId() {
    return Math.random().toString(36).substr(2, 9);
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function getDayName(day) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day];
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function changeUser() {
    const newName = prompt('Enter new user name:', currentUser.name);
    if (newName) {
        currentUser.name = newName;
        updateUserDisplay();
        showToast('User changed successfully', 'success');
    }
}

function updateUserDisplay() {
    document.getElementById('current-user').textContent = currentUser.name;
}

// Policy Management Functions
function editPolicy(policyId) {
    const policy = policies.find(p => p.id === policyId);
    if (policy) {
        showToast(`Editing policy: ${policy.description}`, 'info');
        // In a real implementation, this would open an edit modal
    }
}

function removePolicy(policyId) {
    if (confirm('Are you sure you want to remove this policy?')) {
        policies = policies.filter(p => p.id !== policyId);
        loadPolicies();
        loadDashboard();
        showToast('Policy removed successfully', 'success');
    }
}

// Test agent goal function for direct access
function testAgentGoal() {
    showModal('test-goal');
}

// Update analytics when time range changes
function updateAnalytics() {
    loadAnalytics();
}

// Add some sample data on page load for demo purposes
setTimeout(() => {
    if (policies.length === 0) {
        // Add a sample policy
        policies.push({
            id: generateId(),
            type: 'action',
            description: 'Block all email sending operations',
            restricted_actions: ['email', 'send_email'],
            created_at: new Date().toISOString(),
            active: true
        });
        
        // Add sample audit entries
        auditLog.push(
            {
                id: generateId(),
                timestamp: new Date(Date.now() - 300000).toISOString(),
                action: 'goal_processing',
                goal: 'Send an email to the team',
                user: currentUser.name,
                allowed: false,
                reason: 'Email sending is restricted by policy'
            },
            {
                id: generateId(),
                timestamp: new Date(Date.now() - 600000).toISOString(),
                action: 'goal_processing',
                goal: 'Analyze this document',
                user: currentUser.name,
                allowed: true,
                reason: 'Goal allowed by all active policies'
            }
        );
        
        loadPolicies();
        loadAuditLog();
        loadDashboard();
    }
}, 1000);
