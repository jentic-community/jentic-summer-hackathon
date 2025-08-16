# Track 01 – Standard Agent (Discord Bot)

**Goal**: Build a Discord bot powered by Standard Agent that can execute complex tasks using Jentic's tool ecosystem.

**Time Estimate**: 3-6 hours  
**Difficulty**: Beginner to Intermediate  
**Perfect for**: Developers new to AI agents who want to see immediate, interactive results

## What You'll Build

A Discord bot that users can interact with to:
- Execute multi-step tasks through natural language
- Access real-world APIs via Jentic's tool platform
- Demonstrate autonomous reasoning and error recovery

**Example interactions**:
- User: "!agent Find the latest 3 AI papers on Figshare and summarize them"
- Bot: *Plans task → Searches Figshare → Retrieves papers → Summarizes → Posts results*

## Prerequisites

### Technical Requirements
- Python 3.11+
- Basic familiarity with Discord bots
- Understanding of environment variables

### Accounts & Credentials
- **Discord Developer Account** - Create a bot application
- **Jentic Account** - Agent API key with appropriate scopes
- **LLM Provider** - API key for OpenAI, Anthropic, or Google

### Knowledge Prerequisites
- Basic Python programming
- Understanding of async/await (helpful but not required)
- Familiarity with command-line interfaces

## Step-by-Step Walkthrough

### Phase 1: Environment Setup (30 minutes)

#### 1. Create Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → Name it (e.g., "Hackathon Agent Bot")
3. Go to "Bot" section → "Add Bot"
4. Copy the bot token (keep it secret!)
5. Under "Privileged Gateway Intents" enable:
   - Message Content Intent
   - Server Members Intent (optional)

#### 2. Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
4. Copy generated URL, open in browser, invite to your test server

#### 3. Set Up Development Environment
```bash
# Clone the starter template
git clone [this track's template directory]
cd track-01-standard-agent-discord

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
DISCORD_BOT_TOKEN="your-discord-bot-token"
JENTIC_AGENT_API_KEY="your-jentic-agent-api-key"
OPENAI_API_KEY="your-openai-api-key"  # or ANTHROPIC_API_KEY, GEMINI_API_KEY
LLM_MODEL="gpt-4"  # or claude-sonnet-4, gemini-pro
```

### Phase 2: Basic Bot Implementation (60 minutes)

#### 1. Test the Starter Bot
```bash
python main.py
```

You should see:
```
✅ Discord bot logged in as YourBot#1234
✅ Standard Agent initialized
🤖 Bot ready! Try '!ping' in Discord
```

#### 2. Test Basic Commands
In your Discord server:
- `!ping` → Bot responds with "Pong!"
- `!help` → Shows available commands
- `!agent hello` → Bot uses Standard Agent to respond

#### 3. Understand the Code Structure
The main.py file shows how to:
- Connect to Discord with proper intents
- Initialize Standard Agent with your model
- Handle both text commands and slash commands
- Process user queries through the agent
- Send results back to Discord

### Phase 3: Enhanced Functionality (90-120 minutes)

#### 1. Add Slash Commands
Implement modern Discord slash commands for better UX.

#### 2. Add Progress Indicators
Show users the agent is working on complex tasks.

#### 3. Add Error Handling & User Feedback
Provide helpful error messages and troubleshooting tips.

### Phase 4: Advanced Features (Optional, 60+ minutes)

#### 1. Context-Aware Conversations
Track conversation history for multi-turn interactions.

#### 2. Rich Discord Embeds
Make responses more visually appealing.

#### 3. Command Categories & Help System
Organize functionality into logical groups.

## Testing Your Bot

### Basic Functionality Tests
- [ ] Bot connects to Discord successfully
- [ ] Responds to `!ping` command
- [ ] Can execute simple agent queries
- [ ] Error messages are helpful and user-friendly

### Integration Tests
- [ ] Agent can access Jentic tools (try a search query)
- [ ] Multi-step tasks work (try "find and summarize")
- [ ] Authentication works for protected APIs
- [ ] Bot handles rate limits gracefully

### User Experience Tests
- [ ] Commands are intuitive and discoverable
- [ ] Response times are reasonable (< 30 seconds for most tasks)
- [ ] Error messages help users fix issues
- [ ] Bot behavior is consistent

## Deliverables

### Minimum Viable Product (MVP)
- [ ] Working Discord bot that connects and responds
- [ ] Integration with Standard Agent for task execution
- [ ] At least 2 working commands (e.g., `!ask` and `!help`)
- [ ] Basic error handling
- [ ] Clear setup instructions in README

### Enhanced Version
- [ ] Slash commands for modern Discord UX
- [ ] Progress indicators for long-running tasks
- [ ] Rich embed responses
- [ ] Conversation context awareness
- [ ] Multiple specialized commands

### Documentation
- [ ] Complete README with setup instructions
- [ ] Example interactions with screenshots
- [ ] Troubleshooting guide
- [ ] List of supported capabilities/APIs

## Common Challenges & Solutions

### Discord API Issues
**Problem**: Bot doesn't respond to messages
**Solutions**:
- Check Message Content Intent is enabled
- Verify bot has proper permissions in the server
- Ensure bot token is correct and not expired

### Standard Agent Issues
**Problem**: "No tools found" or "401 Unauthorized"
**Solutions**:
- Verify `JENTIC_AGENT_API_KEY` is set correctly
- Check agent scope includes required APIs in Jentic dashboard
- Test API access with a simple Jentic SDK call

### Performance Issues
**Problem**: Bot responses are slow or timeout
**Solutions**:
- Implement async patterns properly
- Add progress indicators for user feedback
- Set reasonable timeouts on agent calls
- Cache frequently used results

## Getting Help

### Quick Debugging
```bash
# Test Jentic connection
python -c "
import os
from jentic import Jentic
client = Jentic()
print('✅ Jentic connection works')
"

# Test Discord connection
python -c "
import discord
import os
client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    print(f'✅ Discord connection works: {client.user}')
    await client.close()
client.run(os.getenv('DISCORD_BOT_TOKEN'))
"
```

### Resources
- **Discord.py Documentation**: https://discordpy.readthedocs.io/
- **Standard Agent Examples**: https://github.com/jentic/standard-agent/tree/main/examples
- **Jentic SDK Docs**: https://docs.jentic.com/reference/sdks/python/
- **Discord #summer-hackathon**: For real-time help

Remember: The goal is to learn and build something useful. Focus on getting a working bot first, then add enhancements if time permits!