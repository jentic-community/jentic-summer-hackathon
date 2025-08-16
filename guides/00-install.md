# 00 – Install & Setup (10 mins)

*Get ready to build with Jentic in under 10 minutes*

## Prerequisites
- **Git** - Version control (`git --version` to check)
- **Python 3.11+** - Required for all Jentic tools
- **Terminal/Command Prompt** - You'll be running commands
- **Code Editor** - VS Code, PyCharm, Cursor, etc.
- **Discord Account** - For community support during hackathon

## 1. Verify Python Version
```bash
python --version
# Should show 3.11.x or higher
# If not found, try: python3 --version
```

**Need Python?** Download from [python.org/downloads](https://python.org/downloads)

**Using Windows?** Make sure to check "Add Python to PATH" during installation.

## 2. Create Jentic Account & Get Agent API Key

### 🆕 Create Account
1. Go to [[https://app.jentic.com/sign-in](https://app.jentic.com/sign-in)
2. Sign up with your email
3. Verify your email address (check spam folder!)

### 🔑 Add API Credentials (Track-Dependent)
*Only add what your chosen track needs:*

1. In Jentic app → **Settings → Credentials**
2. Add relevant API keys:
   - **OpenAI API key** (for tracks using LLMs: 7, 11, 13, 15, 18)
   - **Discord bot token** (for track 01, 04)
   - **Slack app credentials** (for track 04)
   - **Other APIs** as specified in your track README

### 🤖 Create Your Agent & Get API Key
1. Go to **Agents → Create New Agent**
2. Name it (e.g., "hackathon-2025-agent")
3. **Description**: Brief note about your hackathon project
4. Select **APIs/Workflows** this agent can access:
   - For most tracks: select relevant APIs from the dropdown
   - For research tracks (17): minimal permissions needed
5. Click **Generate API Key**
6. **⚠️ Copy immediately** - shown only once!

### 🌍 Set Environment Variable

**macOS/Linux (Bash/Zsh):**
```bash
# Set for current session
export JENTIC_AGENT_API_KEY="your-agent-api-key-here"

# Make permanent (choose your shell)
echo 'export JENTIC_AGENT_API_KEY="your-agent-api-key-here"' >> ~/.bashrc
# OR for zsh users:
echo 'export JENTIC_AGENT_API_KEY="your-agent-api-key-here"' >> ~/.zshrc

# Reload your shell
source ~/.bashrc  # or ~/.zshrc
```

**Windows (PowerShell):**
```powershell
# Set permanently
setx JENTIC_AGENT_API_KEY "your-agent-api-key-here"

# Set for current session
$env:JENTIC_AGENT_API_KEY = "your-agent-api-key-here"

# Restart PowerShell after using setx
```

**Windows (Command Prompt):**
```cmd
setx JENTIC_AGENT_API_KEY "your-agent-api-key-here"
```

## 3. Install Track Dependencies

**Most tracks need these basics:**
```bash
# Install common Jentic tools
pip install requests python-dotenv

# For OpenAPI/Arazzo tracks (2, 3, 5, 9, 12, 16, 20)
pip install pyyaml jsonschema

# For LLM-powered tracks (7, 11, 13, 15, 18)
pip install openai anthropic
```

**Track-specific installs** are covered in each track's README.

## 4. Verify Your Setup

Test everything works:

```bash
# Check Python
python --version

# Check environment variable
python -c "
import os
key = os.getenv('JENTIC_AGENT_API_KEY')
if key:
    print('✅ Agent API Key: SET (' + key[:8] + '...)')
else:
    print('❌ Agent API Key: NOT SET')
"

# Test basic imports
python -c "import requests, json; print('✅ Basic dependencies working')"
```

**Expected Output:**
```
Python 3.11.x (or higher)
✅ Agent API Key: SET (abc12345...)
✅ Basic dependencies working
```

## 5. Join Discord & Choose Your Track

### 🎮 Join the Community
1. **Discord**: https://discord.gg/TdbWXZsUSm
2. Go to `#summer-hackathon` channel
3. Say hi and mention which track you're considering!

### 🎯 Pick Your Track
**First hackathon?** Start with:
- **Track 06** - Standard Agent Prompts *(1 pt, 2-3h, no coding!)*
- **Track 02** - HAR → OpenAPI *(3 pts, 2-4h)*
- **Track 10** - Generic API Discovery *(3 pts, 3-8h)*

**Have some experience?**
- **Track 07** - API Quality Scorecard *(5 pts, 3-5h)*
- **Track 01** - Standard Agent (Discord) *(3 pts, 3-6h)*

**Want maximum impact?**
- **Track 13** - New Reasoning Models *(10 pts, 6-12h)*
- **Track 15** - Agent Behavior Modification *(10 pts, 8-12h)*

## 6. Final Setup Check

Run this quick validation:

```bash
# Create a test directory
mkdir jentic-hackathon-test
cd jentic-hackathon-test

# Test basic functionality
python -c "
import os
import requests
key = os.getenv('JENTIC_AGENT_API_KEY')
if not key:
    print('❌ Missing JENTIC_AGENT_API_KEY')
    exit(1)
print('✅ Environment setup complete!')
print('🚀 Ready to start building!')
"

# Clean up
cd ..
rmdir jentic-hackathon-test
```

## 📚 Next Steps

1. **Read your track's README** - Each has specific requirements
2. **Check the examples** - See `tracks/track-XX/examples/`
3. **Start coding** - Follow your track's quickstart
4. **Ask questions** - Discord `#summer-hackathon` channel

---

## 🆘 Troubleshooting

### Python Issues
```bash
# "Command not found: python"
python3 --version  # Try python3 instead
which python       # Check where Python is installed

# "Permission denied" with pip
python -m pip install --user packagename  # Install to user directory
# OR use virtual environment (recommended)
python -m venv hackathon-env
source hackathon-env/bin/activate  # Linux/Mac
# hackathon-env\Scripts\activate   # Windows
```

### Environment Variable Issues
```bash
# Variable not set after restart
echo $JENTIC_AGENT_API_KEY  # Linux/Mac - should show your key
echo $env:JENTIC_AGENT_API_KEY  # Windows PowerShell

# If empty, re-run the export/setx commands above
```

### Jentic App Issues
- **Can't access app**: Try incognito/private mode
- **Email verification not received**: Check spam, try resending
- **API key not working**: Make sure you copied the full key
- **Permissions error**: Ensure your agent has access to relevant APIs

### Track-Specific Setup
Each track folder has troubleshooting for its specific requirements:
- `tracks/track-01/README.md` - Discord bot setup
- `tracks/track-04/README.md` - Slack integration issues
- `tracks/track-13/README.md` - LLM model configuration

### Getting Help
1. **Discord `#summer-hackathon`** - Live community support
2. **Track-specific channels** - `#track-01`, `#track-02`, etc.
3. **Include in your help request**:
   - Your operating system
   - Python version (`python --version`)
   - The exact error message
   - What you were trying to do

---

## 🎉 You're Ready!

**Setup complete?** Pick your track and start building:
- Browse all tracks: [README.md](../README.md)
- Join Discord: https://discord.gg/TdbWXZsUSm  
- Start with Track 06 if unsure: [tracks/track-06/](../tracks/track-06/)

**Pro tip**: Many successful hackathon projects start simple and iterate. Pick a track that excites you, not necessarily the hardest one!

---

*Questions? Tag @rodjentic in Discord or ask in #summer-hackathon*
