# Track 06 – Standard Agent Prompts

**Goal**: Create, test, and verify high-quality prompts that demonstrate Standard Agent capabilities across different APIs and use cases.

**Time Estimate**: 2-3 hours  
**Difficulty**: Beginner  
**Perfect for**: Newcomers to AI agents, prompt engineers, and those wanting to explore Jentic's API ecosystem

## What You'll Build

A collection of verified, working prompts that:
- **Demonstrate real-world use cases** for Standard Agent
- **Showcase different API combinations** available through Jentic
- **Provide examples** for other developers to build upon
- **Test agent reasoning** across simple to complex scenarios

**Example prompts you might create**:
- "Find the latest 3 AI research papers on Figshare and post summaries to Discord"
- "Translate this text to Yoda speak and send it via email"
- "Search NYT for climate articles and create a brief report"

## Prerequisites

### Technical Requirements
- Python 3.11+
- Basic understanding of AI prompts and natural language
- Familiarity with Standard Agent (see [Track 01](../track-01-standard-agent-discord/))

### Accounts & Credentials
- **Jentic Account** with Agent API key
- **LLM Provider** (OpenAI, Anthropic, or Google)
- **API credentials** for services you want to test (Discord, email, etc.)

### Knowledge Prerequisites
- Understanding of what makes a good AI prompt
- Basic familiarity with APIs and web services
- No programming experience required

## Getting Started (30 minutes)

### 1. Environment Setup
```bash
# Create project directory
mkdir standard-agent-prompts
cd standard-agent-prompts

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your Test Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
JENTIC_AGENT_API_KEY="your-jentic-agent-api-key"
OPENAI_API_KEY="your-openai-api-key"  # or ANTHROPIC_API_KEY, GEMINI_API_KEY
LLM_MODEL="gpt-4"  # or claude-sonnet-4, gemini-pro
```

### 3. Test Your Setup
```bash
# Run the setup verification script
python verify_setup.py

# Expected output:
# ✅ Environment variables configured
# ✅ Standard Agent connection working
# ✅ Jentic API access confirmed
# 🚀 Ready to create prompts!
```

## Your Prompt Creation Tasks

### Phase 1: Simple Single-API Prompts (45 minutes)

#### Task 1: Create Basic Information Retrieval Prompts
Create prompts that use **one API** to fetch and present information.

**Examples to try**:
- Weather information queries
- Academic paper searches
- News article summaries
- Translation requests

**Deliverable**: 3-5 working prompts that successfully retrieve and format information.

#### Task 2: Test Prompt Variations
For each basic prompt, create variations that test:
- **Different parameters** (locations, topics, time ranges)
- **Different output formats** (brief vs detailed, formal vs casual)
- **Edge cases** (invalid inputs, missing data)

**Deliverable**: Documentation showing how prompts behave with different inputs.

### Phase 2: Multi-API Workflow Prompts (60 minutes)

#### Task 3: Create Chain Prompts
Build prompts that combine **multiple APIs** in sequence.

**Example patterns**:
- **Search → Summarize → Share**: Find content, process it, distribute it
- **Translate → Format → Send**: Process text and deliver via messaging
- **Fetch → Analyze → Report**: Gather data and create formatted output

**Deliverable**: 3 working multi-step prompts with clear success criteria.

#### Task 4: Test Error Handling
Create prompts that test how Standard Agent handles:
- **API failures** (invalid credentials, rate limits)
- **Missing data** (empty search results, unavailable services)
- **User errors** (malformed requests, impossible tasks)

**Deliverable**: Documentation of how agents gracefully handle failures.

### Phase 3: Advanced Prompt Patterns (45 minutes)

#### Task 5: Conversational Context Prompts
Create prompts that maintain context across multiple interactions.

**Examples**:
- "Remember my preferred news topics and find articles about them"
- "Based on our previous conversation, suggest follow-up actions"
- "Update the report we created earlier with new information"

#### Task 6: Conditional Logic Prompts
Design prompts that make decisions based on data or user preferences.

**Examples**:
- "If the weather is bad, suggest indoor activities, otherwise outdoor ones"
- "Only send notifications during business hours"
- "Escalate to email if Discord message fails"

**Deliverable**: Working examples of intelligent decision-making prompts.

## Testing Your Prompts

### Verification Checklist
For each prompt you create, verify:

- [ ] **Executes successfully** with valid inputs
- [ ] **Handles errors gracefully** with invalid inputs
- [ ] **Produces useful output** that matches the request
- [ ] **Uses appropriate APIs** for the task
- [ ] **Completes within reasonable time** (< 2 minutes for most tasks)

### Testing Framework
Use the provided testing script:

```bash
# Test a single prompt
python test_prompt.py "Find the latest AI research papers on Figshare"

# Test all prompts in your collection
python test_all_prompts.py

# Generate performance report
python prompt_performance_report.py
```

### Documentation Template
For each prompt, document:

```markdown
## Prompt: [Brief Description]

**Purpose**: What this prompt accomplishes
**APIs Used**: List of APIs/services involved
**Expected Time**: How long it typically takes
**Example Input**: Sample user request
**Example Output**: What the agent returns
**Edge Cases**: Known limitations or failure modes
**Variations**: Alternative phrasings or parameters
```

## Deliverables

### Minimum Viable Product
- [ ] **5 working prompts** covering different use cases
- [ ] **Test verification** showing successful execution
- [ ] **Documentation** explaining each prompt's purpose and usage
- [ ] **Setup instructions** for others to reproduce your work

### Enhanced Collection
- [ ] **10+ prompts** spanning simple to complex scenarios
- [ ] **Error handling examples** showing graceful failures
- [ ] **Performance benchmarks** with timing and success rates
- [ ] **Conversation flows** demonstrating multi-turn interactions

### Professional Quality
- [ ] **Comprehensive test suite** with automated verification
- [ ] **User experience guidelines** for prompt design
- [ ] **API coverage analysis** showing breadth of integrations
- [ ] **Contribution to Standard Agent examples** repository

## Common Challenges & Solutions

### Prompt Design Issues
**Challenge**: Agent doesn't understand what you want
**Solutions**:
- Be specific about desired output format
- Include examples of good responses
- Break complex requests into smaller steps
- Test with different phrasings

### API Integration Problems
**Challenge**: Agent can't access required APIs
**Solutions**:
- Verify API credentials in Jentic dashboard
- Check agent scope includes needed services
- Test individual API calls manually first
- Review API rate limits and quotas

### Performance Issues
**Challenge**: Prompts take too long or fail frequently
**Solutions**:
- Simplify complex multi-step requests
- Add timeout expectations to prompts
- Test during off-peak hours
- Consider breaking into smaller workflows

## Quality Guidelines

### What Makes a Good Agent Prompt
- **Clear intent**: Specific about what should happen
- **Realistic scope**: Achievable with available APIs
- **Good examples**: Shows expected input/output
- **Error awareness**: Handles common failure cases
- **User-friendly**: Easy for others to understand and use

### Prompt Categories to Cover
- **Information retrieval**: Search, fetch, analyze
- **Communication**: Send messages, notifications, reports
- **Content processing**: Translate, summarize, transform
- **Workflow automation**: Multi-step business processes
- **Creative tasks**: Content generation, formatting

## Getting Help

### Quick Debugging
```bash
# Test Standard Agent connection
python -c "from agents.prebuilt import ReWOOAgent; agent = ReWOOAgent(); print('✅ Agent ready')"

# Test Jentic API access
python -c "from jentic import Jentic; client = Jentic(); print('✅ Jentic connected')"

# Validate environment setup
python verify_setup.py
```

### Support Resources
- **Discord**: #summer-hackathon for real-time help
- **Standard Agent Examples**: See existing examples in the repo
- **API Documentation**: Review available APIs in Jentic dashboard
- **Prompt Engineering**: General AI prompting best practices

## Extension Ideas

Once you have a working collection:
- **Create prompt templates** for common patterns
- **Build a prompt testing framework** for automated verification
- **Develop conversation flows** with multi-turn interactions
- **Create domain-specific collections** (research, business, creative)
- **Write prompt optimization guidelines** based on your findings

## Success Criteria

Your prompt collection succeeds when:
1. **Others can easily use your prompts** with clear instructions
2. **Prompts reliably work** across different conditions
3. **Coverage demonstrates** Standard Agent capabilities well
4. **Documentation helps** newcomers understand agent potential
5. **Quality examples** inspire others to build better prompts

Remember: **Start simple**, verify each prompt works, then build complexity. The goal is to create valuable examples that showcase what's possible with Standard Agent and Jentic's API ecosystem!