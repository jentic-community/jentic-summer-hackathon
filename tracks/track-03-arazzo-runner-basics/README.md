# Track 03 – Arazzo Runner Basics

**Goal**: Master the fundamentals of Arazzo workflows by creating, executing, and debugging multi-step API orchestrations.

**Time Estimate**: 3-5 hours  
**Difficulty**: Beginner to Intermediate  
**Perfect for**: Developers wanting to understand workflow automation and multi-API coordination

## What You'll Build

Hands-on experience with Arazzo workflows:
- **Basic workflows** that chain multiple API calls
- **Parameterized workflows** with dynamic inputs
- **Error handling and recovery** patterns
- **Real-world integrations** using public APIs

**Example outcomes**:
- Workflow that searches for research papers and posts summaries to Discord
- Multi-step data processing pipeline with external APIs
- Automated content aggregation and distribution workflow

## Prerequisites

### Technical Requirements
- Python 3.11+
- Basic understanding of APIs and HTTP
- Familiarity with YAML/JSON formats
- Command-line comfort

### Accounts & Credentials
- **Jentic Account** - To compare workflows executed locally vs with Jentic
- **API credentials** for testing (Discord, news APIs, etc.)
- **LLM Provider** (optional, for content processing workflows)

### Knowledge Prerequisites
- Understanding of REST APIs
- Basic workflow/automation concepts
- Familiarity with environment variables

## Learning Path

### Phase 1: Understanding Arazzo (45 minutes)

#### 1. Core Concepts Review
Read the [Arazzo Guide](../../guides/01-what-is-arazzo.md) if you haven't already.

Key concepts to understand:
- **Workflows**: Sequences of API operations
- **Steps**: Individual API calls within a workflow
- **Parameters**: Input/output data flow
- **Dependencies**: Step execution order
- **Operations**: HTTP requests with specific endpoints

#### 2. Set Up Your Environment
```bash
# Create project directory
mkdir arazzo-basics-track
cd arazzo-basics-track

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Arazzo Runner
pip install -r requirements.txt

# Verify installation
arazzo-runner --help
```

#### 3. Create Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or your preferred editor
```

### Phase 2: Your First Workflow (60 minutes)

#### 1. Hello World Workflow
Run the provided hello world example:

```bash
# Execute the basic workflow
arazzo-runner execute-workflow workflows/01-hello-world.arazzo.yaml --workflow-id helloWorld

# Expected output: JSON with current time and IP address
```

#### 2. Understand the Structure
Examine `workflows/01-hello-world.arazzo.yaml` to see:
- Basic workflow structure
- How operations are defined
- Output capture and data flow
- Simple API calls without authentication

#### 3. Explore Runner Commands
```bash
# List workflows in a file
arazzo-runner list-workflows workflows/01-hello-world.arazzo.yaml

# Show detailed workflow info
arazzo-runner describe-workflow workflows/01-hello-world.arazzo.yaml --workflow-id helloWorld

# Show environment variables needed
arazzo-runner show-env-mappings workflows/01-hello-world.arazzo.yaml
```

### Phase 3: Parameterized Workflows (75 minutes)

#### 1. Workflow with Inputs
Study and run the parameterized example:

```bash
# Run with basic parameters
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "machine learning"}'

# Run with custom parameters
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "space exploration", "target_language": "yoda"}'
```

#### 2. Understanding Data Flow
Learn how data flows between steps:
- `$inputs.search_query` → Input to first step
- `$steps.stepName.outputs.fieldName` → Output from previous steps
- `$response.body.field` → API response data

#### 3. Create Your Own Parameterized Workflow
Modify the example or create a new one that:
- Takes user inputs
- Uses those inputs in API calls
- Chains multiple steps together
- Produces meaningful outputs

### Phase 4: Real-World Integration (90 minutes)

#### 1. Multi-API Workflow with Authentication
Study the real-world integration example:

```bash
# Set up your API credentials first
export NEWS_API_KEY="your-news-api-key"
export DISCORD_BOT_TOKEN="your-discord-bot-token"

# Run the workflow
arazzo-runner execute-workflow workflows/03-real-world-integration.arazzo.yaml \
  --workflow-id newsToDiscord \
  --inputs '{"discord_channel_id": "your-channel-id", "news_category": "technology"}'
```

#### 2. Authentication Patterns
Learn about different auth methods:
- API keys in headers (`X-API-Key: ${API_KEY}`)
- Bearer tokens (`Authorization: Bearer ${TOKEN}`)
- Query parameter auth (`?api_key=${KEY}`)

#### 3. Build Your Own Integration
Create a workflow that:
- Uses at least 2 different APIs
- Requires authentication
- Processes data between steps
- Produces a useful result

### Phase 5: Error Handling and Debugging (60 minutes)

#### 1. Robust Workflows
Examine the error handling example:

```bash
# Run workflow with error handling
arazzo-runner execute-workflow workflows/04-error-handling.arazzo.yaml \
  --workflow-id robustDataFetch
```

#### 2. Debugging Techniques
Learn to debug workflows:

```bash
# Run with verbose logging
arazzo-runner --log-level DEBUG execute-workflow workflow.arazzo.yaml --workflow-id myWorkflow

# Test individual operations
arazzo-runner execute-operation \
  --arazzo-path workflow.arazzo.yaml \
  --operation-id problematicOperation

# Generate example commands
arazzo-runner generate-example workflow.arazzo.yaml --workflow-id myWorkflow
```

#### 3. Common Issues and Solutions
- Authentication failures → Check env vars and API credentials
- Parameter errors → Validate workflow structure and inputs
- Network issues → Test individual operations
- YAML syntax → Use linter to validate structure

### Phase 6: Advanced Patterns (Optional, 90+ minutes)

#### 1. Conditional Logic
Create workflows with conditional execution:
- Steps that run only under certain conditions
- Different processing paths based on data
- Fallback mechanisms for failures

#### 2. Parallel Execution
Design workflows with parallel steps:
- Independent API calls that can run simultaneously
- Data aggregation from multiple sources
- Performance optimization through concurrency

#### 3. Complex Data Processing
Build workflows that:
- Transform data between different formats
- Aggregate information from multiple sources
- Implement business logic through step sequencing

## Deliverables

### Minimum Viable Product
- [ ] **3 working workflows** covering basic, parameterized, and error handling patterns
- [ ] **Environment setup** with proper authentication
- [ ] **Documentation** explaining each workflow's purpose and usage
- [ ] **Test execution** proof (screenshots or logs)

### Enhanced Version
- [ ] **5+ workflows** including real-world integrations
- [ ] **Advanced patterns** (conditional logic, parallel execution)
- [ ] **Custom operations** for specific use cases
- [ ] **Comprehensive testing** across different scenarios

### Professional Quality
- [ ] **Production-ready workflows** with robust error handling
- [ ] **Reusable patterns** that others can adapt
- [ ] **Performance optimization** for complex workflows
- [ ] **Contribution to examples** in Arazzo Engine repository

## Testing Your Workflows

### Basic Functionality Tests
```bash
# Test each workflow individually
for workflow in workflows/*.arazzo.yaml; do
  echo "Testing $workflow..."
  arazzo-runner list-workflows "$workflow"
done

# Validate workflow structure
arazzo-runner describe-workflow your-workflow.arazzo.yaml --workflow-id yourWorkflow
```

### Integration Tests
```bash
# Test with real API credentials
arazzo-runner execute-workflow real-world-workflow.arazzo.yaml \
  --workflow-id yourWorkflow \
  --inputs '{"real": "parameters"}'

# Test error scenarios
arazzo-runner execute-workflow error-handling-workflow.arazzo.yaml \
  --workflow-id robustWorkflow \
  --inputs '{"invalid": "data"}'
```

### Performance Tests
```bash
# Time workflow execution
time arazzo-runner execute-workflow your-workflow.arazzo.yaml --workflow-id yourWorkflow

# Test with verbose logging to identify bottlenecks
arazzo-runner --log-level DEBUG execute-workflow your-workflow.arazzo.yaml --workflow-id yourWorkflow
```

## Common Challenges & Solutions

### Workflow Design Issues
**Challenge**: Steps executing in wrong order
**Solution**: 
- Use `dependsOn` to specify execution order
- Check that step dependencies are correctly specified
- Use `arazzo-runner describe-workflow` to visualize dependencies

**Challenge**: Data not flowing between steps
**Solution**:
- Verify output expressions: `$steps.stepName.outputs.fieldName`
- Check that previous steps actually produce the expected outputs
- Use `--log-level DEBUG` to see intermediate values

### Authentication Problems
**Challenge**: "401 Unauthorized" errors
**Solution**:
- Verify environment variables are set: `echo $API_KEY`
- Check `arazzo-runner show-env-mappings` output
- Test credentials manually with curl
- Ensure token format matches API requirements

### Performance Issues
**Challenge**: Workflows taking too long
**Solution**:
- Identify bottleneck steps with timing logs
- Consider parallel execution for independent steps
- Optimize API calls (batch requests, pagination)
- Add timeouts to prevent hanging

## Extension Ideas

### For Workflow Builders
- **Template Library**: Create reusable workflow templates
- **Validation Pipeline**: Workflows that test API specifications
- **Data Transformation**: Complex data processing pipelines
- **Monitoring Workflows**: Health checks and status reporting

### For Integration Specialists  
- **Multi-Platform Publishing**: Content to multiple social media platforms
- **Data Synchronization**: Keep multiple systems in sync
- **Notification Workflows**: Alert systems across multiple channels
- **Backup and Archive**: Automated data backup workflows

## Submission Guidelines

### File Structure
```
arazzo-basics-project/
├── README.md
├── .env.example
├── requirements.txt
├── workflows/
│   ├── 01-hello-world.arazzo.yaml
│   ├── 02-parameterized.arazzo.yaml
│   ├── 03-real-world-integration.arazzo.yaml
│   ├── 04-error-handling.arazzo.yaml
│   └── 05-your-custom-workflow.arazzo.yaml
├── examples/
│   ├── basic-usage.md
│   └── troubleshooting.md
├── screenshots/
│   └── workflow-execution.png
└── docs/
    └── workflow-design-guide.md
```

### Quality Criteria
- **Functionality**: All workflows execute successfully
- **Documentation**: Clear explanations and examples
- **Error Handling**: Robust failure management
- **Real-world Value**: Solve actual problems
- **Code Quality**: Well-structured, readable YAML

## Getting Help

### Quick Debugging Commands
```bash
# Check Arazzo Runner installation
arazzo-runner --version

# Test environment setup
arazzo-runner show-env-mappings workflow.arazzo.yaml

# Minimal workflow test
echo 'arazzo: 1.0.0
info: {title: Test, version: 1.0.0}
workflows:
  - workflowId: test
    steps:
      - stepId: ping
        operationRef: "#/operations/ping"
operations:
  - operationId: ping
    method: GET
    url: https://httpbin.org/get' > test.arazzo.yaml

arazzo-runner execute-workflow test.arazzo.yaml --workflow-id test
```

### Support Resources
- **Arazzo Runner CLI Docs**: [CLI Reference](../../cli/arazzo-runner.md)
- **Official Examples**: [Arazzo Engine Examples](https://github.com/jentic/arazzo-engine/tree/main/runner/examples)
- **Discord Support**: #summer-hackathon channel for real-time help

Remember: Start simple with basic workflows, then progressively add complexity. The goal is to understand the patterns and principles that make workflows robust and reusable!