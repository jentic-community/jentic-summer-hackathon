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

## Current Implementation Status

### ✅ Slack Integration (COMPLETED)
- **Full Slack Bot**: Complete implementation with Socket Mode for real-time events
- **Standard Agent Integration**: Direct integration with ReWOO Standard Agent
- **Event Handling**: Supports mentions and direct messages
- **Conversation Context**: Maintains conversation history per user
- **Message Formatting**: Proper Slack formatting with truncation and styling
- **Error Handling**: Comprehensive error handling and user feedback

### 🔄 Email Integration (IN PROGRESS)
- Basic structure created, needs implementation

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
# Navigate to the track directory
cd tracks/track-04-agent-comms-slack-email

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Slack Setup (Required for current implementation)

#### Step 1: Create a Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "AI Assistant Bot")
4. Select your workspace

#### Step 2: Configure Bot Permissions
1. Go to "OAuth & Permissions" in the sidebar
2. Under "Scopes" → "Bot Token Scopes", add:
   - `chat:write` - Send messages
   - `channels:read` - Read channel info
   - `app_mentions:read` - Handle mentions
   - `im:read` - Read direct messages
   - `im:write` - Send direct messages
   - `im:history` - Read direct message history

#### Step 3: Enable Socket Mode
1. Go to "Socket Mode" in the sidebar
2. Enable Socket Mode
3. Create an app-level token (save this as `SLACK_APP_TOKEN`)

#### Step 4: Subscribe to Events
1. Go to "Event Subscriptions" in the sidebar
2. Enable Events
3. Subscribe to bot events:
   - `app_mention` - When someone mentions your bot
   - `message.im` - When someone sends a direct message

#### Step 5: Install to Workspace
1. Go to "OAuth & Permissions"
2. Click "Install to Workspace"
3. Copy the "Bot User OAuth Token" (save as `SLACK_BOT_TOKEN`)

### 3. Environment Configuration
```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials:
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_DEFAULT_CHANNEL=C1234567890  # Optional: for testing

# Standard Agent configuration
LLM_MODEL=claude-3-sonnet-20240229  # Optional: defaults to this
ANTHROPIC_API_KEY=your-anthropic-key  # Required for Standard Agent
JENTIC_API_KEY=your-jentic-key  # Optional: for additional tools
```

## Usage

### Testing the Implementation

#### 1. Test Connection and Standard Agent
```bash
python demo.py test
```
This will:
- Test Slack connection
- Verify Standard Agent initialization
- Run a test query through the Standard Agent

#### 2. List Available Channels
```bash
python demo.py channels
```
Shows all channels your bot can access.

#### 3. Send Test Message
```bash
python demo.py send
```
Sends a test message to your default channel (requires `SLACK_DEFAULT_CHANNEL` in .env).

#### 4. Run the Full Bot
```bash
python demo.py run
```
Starts the bot in Socket Mode. The bot will:
- Listen for mentions in channels
- Respond to direct messages
- Process queries through the Standard Agent
- Maintain conversation context

### Using the Bot

#### In Channels
Mention your bot to interact:
```
@your-bot What's the weather in Paris?
@your-bot Can you help me with a math problem?
```

#### Direct Messages
Send direct messages to your bot for private conversations:
```
What's 2 + 2?
Tell me a joke
Help me plan my day
```

## Implementation Details

### Slack Agent Features

#### 1. Real-time Event Handling
- **Socket Mode**: Uses Slack's Socket Mode for real-time communication
- **Event Types**: Handles mentions and direct messages
- **Async Processing**: Non-blocking event processing

#### 2. Standard Agent Integration
- **ReWOO Agent**: Uses the ReWOO reasoning methodology
- **Tool Access**: Has access to 1500+ tools via Jentic
- **Conversation Memory**: Maintains context across interactions

#### 3. Conversation Management
- **User Context**: Tracks conversation history per user
- **Memory Management**: Keeps last 10 interactions per user
- **Context Preservation**: Maintains conversation flow

#### 4. Message Formatting
- **Slack Optimization**: Proper formatting for Slack
- **Length Limits**: Handles message truncation
- **Rich Formatting**: Supports bold, bullet points, etc.

### Code Structure

```
track-04-agent-comms-slack-email/
├── slack_agent.py          # Main Slack bot implementation
├── base_agent.py           # Base interface for communication agents
├── demo.py                 # Testing and demo utilities
├── email_integration.py    # Email integration (to be implemented)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Key Classes

#### `SlackAgent`
- **Inherits from**: `BaseCommunicationAgent`
- **Features**:
  - Socket Mode event handling
  - Standard Agent integration
  - Conversation context management
  - Message formatting

#### `BaseCommunicationAgent`
- **Purpose**: Abstract interface for communication platforms
- **Methods**:
  - `test_connection()`: Verify platform connectivity
  - `send_message()`: Send messages to recipients
  - `process_agent_query()`: Process queries with Standard Agent

## Testing Your Implementation

### Basic Tests
```bash
# Test connection and Standard Agent
python demo.py test

# List available channels
python demo.py channels

# Send test message
python demo.py send

# Run full bot
python demo.py run
```

### Manual Testing
1. **Start the bot**: `python demo.py run`
2. **Mention in channel**: `@your-bot Hello!`
3. **Send DM**: Direct message your bot
4. **Test complex queries**: Ask questions that require tools

### Expected Behaviors
1. **Simple Q&A**: "What is 2+2?" → Correct mathematical answer
2. **Tool Usage**: "What's the weather?" → Uses weather tools
3. **Conversation**: Follow-up questions maintain context
4. **Error Handling**: Graceful handling of invalid inputs

## Troubleshooting

### Common Issues

#### 1. Connection Failures
```
❌ SLACK_BOT_TOKEN not set
❌ SLACK_APP_TOKEN not set
❌ Failed to connect to Slack
```
**Solution**: Verify your tokens in the .env file

#### 2. Standard Agent Issues
```
❌ Standard Agent is not available
❌ Failed to initialize Standard Agent
```
**Solution**: Check your `ANTHROPIC_API_KEY` and `LLM_MODEL` settings

#### 3. Permission Errors
```
❌ Missing required scopes
❌ Bot not installed to workspace
```
**Solution**: Verify bot permissions and workspace installation

#### 4. Event Handling Issues
```
❌ Bot not responding to mentions
❌ Direct messages not working
```
**Solution**: Check Event Subscriptions and Socket Mode setup

### Debug Mode
Enable debug logging by setting:
```bash
export PYTHONPATH="${PYTHONPATH}:../standard-agent"
python -u demo.py run
```

## Extension Ideas

### For Slack Implementation
- **Interactive Elements**: Add buttons, dropdowns, and forms
- **File Uploads**: Handle file attachments and processing
- **Thread Support**: Respond in threads for better organization
- **Rich Messages**: Use Slack Block Kit for rich formatting
- **User Preferences**: Store user preferences and settings

### For Email Implementation
- **HTML Templates**: Create beautiful email templates
- **Attachment Handling**: Process email attachments
- **Threading**: Maintain email conversation threads
- **Scheduling**: Send scheduled responses
- **Signature Management**: Professional email signatures

### General Enhancements
- **Multi-platform Support**: Unified interface for multiple platforms
- **Analytics**: Track usage and performance metrics
- **Admin Interface**: Web interface for bot management
- **Plugin System**: Extensible architecture for new features
- **Rate Limiting**: Smart rate limiting and queuing

## Success Criteria

Your implementation succeeds when:
1. **Users can naturally interact** with Standard Agent through Slack
2. **Responses are well-formatted** and appropriate for Slack
3. **Error cases are handled gracefully** with helpful feedback
4. **The system is reliable** and doesn't crash on edge cases
5. **Setup instructions are clear** and others can run your code
6. **Conversation context is maintained** across multiple interactions

## Getting Help

### Quick Debugging
```bash
# Test environment setup
python demo.py test

# Check channels
python demo.py channels

# Test message sending
python demo.py send
```

### Support Resources
- **Discord**: #summer-hackathon for real-time help
- **Slack API Docs**: [api.slack.com](https://api.slack.com)
- **Standard Agent**: See Track 01 for integration patterns
- **Socket Mode**: [Socket Mode Guide](https://api.slack.com/apis/connections/socket)

## Next Steps

### Immediate Tasks
1. **Test the current implementation** with your Slack workspace
2. **Customize the bot** for your specific use case
3. **Add error handling** for edge cases
4. **Implement email integration** following the same pattern

### Advanced Features
1. **Add interactive elements** (buttons, forms)
2. **Implement user preferences** and settings
3. **Create admin interface** for bot management
4. **Add analytics** and monitoring
5. **Support multiple platforms** simultaneously

Remember: **Start simple**, get it working, then enhance. The goal is to create a useful bridge between humans and AI agents!