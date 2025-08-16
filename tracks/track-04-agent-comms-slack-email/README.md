# Track 04 – Agent Comms (Slack/Email)

**Goal**: Build communication bridges between Standard Agent and messaging platforms like Slack, email, or SMS.

**Time Estimate**: 4-6 hours  
**Difficulty**: Intermediate  
**Perfect for**: Developers interested in agent-human interaction and multi-channel communication

## What You'll Build

You'll create your own communication integrations that:
- **Connect Standard Agent** to one or more messaging platforms
- **Handle user interactions** through natural conversation
- **Send intelligent responses** with appropriate formatting
- **Route messages** based on content, urgency, or user preference

**Your deliverable**: A working system where users can interact with your Standard Agent through their preferred communication channel.

## Prerequisites

### Technical Requirements
- Python 3.11+
- Understanding of Standard Agent architecture (see [Track 01](../track-01-standard-agent-discord/))
- Basic knowledge of API authentication
- Familiarity with async programming (helpful)

### Accounts & Services (Choose at least one)
- **Slack workspace** and developer account
- **Email service** (Gmail, SendGrid, etc.)
- **SMS service** (Twilio) for advanced implementations

### Knowledge Prerequisites
- Understanding of webhooks and event handling
- Basic knowledge of OAuth and API authentication
- Familiarity with message formatting (Markdown, HTML)

## Getting Started (30 minutes)

### 1. Environment Setup
```bash
# Create project directory
mkdir agent-comms-project
cd agent-comms-project

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install starter dependencies
pip install -r requirements.txt
```

### 2. Choose Your Platform

Pick **one platform** to focus on initially (you can add more later):

**Option A: Slack** (Recommended for beginners)
- Good for: Real-time interaction, rich formatting, team environments
- Complexity: Medium
- Setup time: ~45 minutes

**Option B: Email** 
- Good for: Formal communications, detailed responses, asynchronous interaction
- Complexity: Medium
- Setup time: ~30 minutes

**Option C: SMS**
- Good for: Urgent notifications, simple interactions, mobile-first users
- Complexity: Lower
- Setup time: ~20 minutes

### 3. Set Up Your Chosen Platform

#### For Slack:
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app → "From scratch"
3. Configure basic bot permissions:
   - `chat:write` - Send messages
   - `channels:read` - Read channel info
   - `app_mentions:read` - Handle mentions
4. Install to your workspace
5. Copy the Bot User OAuth Token

#### For Email:
1. **Option A**: Set up SendGrid account (recommended)
   - Get API key from SendGrid
2. **Option B**: Use Gmail with app password
   - Enable 2FA and create app password
   - Note: SMTP settings needed

#### For SMS:
1. Create Twilio account
2. Get Account SID and Auth Token
3. Get a Twilio phone number (trial is fine)

### 4. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# Add only the credentials for your chosen platform
```

## Your Implementation Tasks

### Phase 1: Basic Integration (90 minutes)

#### Task 1: Create Your Communication Class
Build a class that can:
- Connect to your chosen platform
- Send a simple message
- Handle basic errors

**Deliverable**: A working class that can send "Hello World" messages.

**Files to create/modify**:
- `integrations/my_platform_agent.py` (implement your communication logic)
- Test it with the provided skeleton

#### Task 2: Connect Standard Agent
Integrate your communication class with Standard Agent:
- Accept user queries through your platform
- Process them with Standard Agent
- Send responses back

**Deliverable**: Users can ask your agent questions and get intelligent responses.

### Phase 2: Enhanced Features (90-120 minutes)

#### Task 3: Improve User Experience
Add features like:
- **Message formatting** appropriate for your platform
- **Error handling** with helpful user messages
- **Typing indicators** or progress feedback
- **Command parsing** (for platforms that support it)

#### Task 4: Smart Response Handling
Implement:
- **Response length management** (truncate for SMS, paginate for long responses)
- **Context awareness** (remember conversation history)
- **Different response types** (quick answers vs detailed explanations)

### Phase 3: Advanced Features (Optional, 60+ minutes)

#### Task 5: Multi-Channel or Advanced Features
Choose one:
- **Add a second platform** and create a unified interface
- **Interactive elements** (buttons, forms, etc. if platform supports)
- **Conversation flows** with follow-up questions
- **User preferences** and personalization

## Provided Starter Code

### Communication Interface Template
```python
# integrations/base_agent.py - Interface your agent should implement
class BaseCommunicationAgent:
    def __init__(self):
        # TODO: Initialize your platform connection
        pass
    
    def test_connection(self) -> bool:
        # TODO: Test if platform is reachable
        pass
    
    def send_message(self, recipient: str, message: str) -> dict:
        # TODO: Send message to recipient
        pass
    
    def process_agent_query(self, query: str, user_context: dict) -> str:
        # TODO: Use Standard Agent to process query
        pass
```

### Testing Framework
```python
# test_integration.py - Test your implementation
def test_platform_connection():
    # TODO: Verify platform connectivity
    pass

def test_agent_integration():
    # TODO: Test Standard Agent integration
    pass

def test_message_formatting():
    # TODO: Test message formatting
    pass
```

### Example Usage
```python
# examples/demo.py - Shows how your agent should work
def demo_conversation():
    # User: "What's the weather in Paris?"
    # Agent: Processes query → Gets weather → Formats response → Sends via platform
    pass
```

## Implementation Guidance

### For Slack Implementers
**Key challenges to solve**:
- Event handling for mentions and DMs
- Slack's block-based message formatting
- Managing conversation threads
- Handling rate limits

**Hints**:
- Use `slack-sdk` library
- Implement webhook endpoint for events
- Study Slack Block Kit for rich messages

### For Email Implementers  
**Key challenges to solve**:
- HTML vs plain text formatting
- Email threading for conversations
- Attachment handling
- SMTP vs API-based sending

**Hints**:
- Consider SendGrid for simplicity
- Use email templates for consistent formatting
- Implement subject line generation

### For SMS Implementers
**Key challenges to solve**:
- 160 character message limits
- Conversation context without threading
- Number formatting and validation
- Cost management

**Hints**:
- Implement smart truncation
- Use conversation state tracking
- Consider message splitting for long responses

## Testing Your Implementation

### Basic Tests
```bash
# Test platform connectivity
python -c "from integrations.my_agent import MyAgent; agent = MyAgent(); print(agent.test_connection())"

# Test message sending
python -c "from integrations.my_agent import MyAgent; agent = MyAgent(); agent.send_message('test-recipient', 'Hello!')"

# Test agent integration
python examples/demo.py
```

### Integration Tests
Your implementation should pass these scenarios:
1. **Simple Q&A**: User asks "What is 2+2?" → Agent responds correctly
2. **Complex Query**: User asks research question → Agent uses tools and responds
3. **Error Handling**: Invalid input → Agent responds helpfully
4. **Long Response**: Agent response > platform limit → Handled gracefully

## Deliverables

### Minimum Viable Product
- [ ] **Working platform integration** that can send/receive messages
- [ ] **Standard Agent connection** that processes queries
- [ ] **Basic error handling** with user-friendly messages
- [ ] **Demo script** showing the system in action
- [ ] **README** with setup and usage instructions

### Enhanced Implementation
- [ ] **Rich message formatting** using platform-specific features
- [ ] **Conversation context** management
- [ ] **Multiple message types** (quick answers, detailed responses, errors)
- [ ] **User experience optimizations** (typing indicators, progress updates)

### Advanced Implementation
- [ ] **Multi-platform support** or **advanced platform features**
- [ ] **Interactive elements** (buttons, forms, etc.)
- [ ] **Conversation flows** with follow-up questions
- [ ] **Performance optimizations** and **scalability considerations**

## Success Criteria

Your implementation succeeds when:
1. **Users can naturally interact** with Standard Agent through your platform
2. **Responses are well-formatted** and appropriate for the platform
3. **Error cases are handled gracefully** with helpful feedback
4. **The system is reliable** and doesn't crash on edge cases
5. **Setup instructions are clear** and others can run your code

## Getting Help

### Quick Debugging
```bash
# Test environment setup
python test_environment.py

# Test Standard Agent
python test_agent.py

# Test your integration
python test_integration.py
```

### Common Issues
- **Authentication failures**: Double-check API keys and permissions
- **Message formatting**: Study platform documentation for formatting rules
- **Rate limiting**: Implement backoff and respect platform limits
- **Agent integration**: Ensure Standard Agent is properly initialized

### Support
- **Discord**: #summer-hackathon for real-time help
- **Platform docs**: Each platform has extensive API documentation
- **Standard Agent**: See Track 01 for integration patterns

## Extension Ideas

Once you have a working basic implementation:
- **Add conversation memory** across multiple interactions
- **Implement user preferences** (response length, formality level)
- **Create specialized commands** for common tasks
- **Add approval workflows** for sensitive operations
- **Build admin/monitoring interfaces**
- **Integrate with other services** (calendars, databases, etc.)

Remember: **Start simple**, get it working, then enhance. The goal is to create a useful bridge between humans and AI agents!