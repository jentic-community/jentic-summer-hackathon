# Basic Usage Examples

This document provides examples of how to use the Arazzo workflows in this track.

## Prerequisites

Make sure you have:
1. Installed dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Activated your virtual environment

## Running Workflows

### 1. Hello World Workflow

The simplest workflow to test your setup:

```bash
# Basic execution
arazzo-runner execute-workflow workflows/01-hello-world.arazzo.yaml --workflow-id helloWorld

# With debug logging
arazzo-runner --log-level DEBUG execute-workflow workflows/01-hello-world.arazzo.yaml --workflow-id helloWorld
```

**Expected Output:**
```json
{
  "workflow_id": "helloWorld",
  "status": "completed",
  "outputs": {
    "current_time": "2025-01-15T14:30:00Z",
    "timezone": "UTC",
    "day_of_week": 1,
    "ip_address": "203.0.113.42",
    "country": "United States",
    "city": "San Francisco",
    "region": "California"
  }
}
```

### 2. Parameterized Workflow

Workflow that accepts inputs and demonstrates data flow:

```bash
# Basic search and translation
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "artificial intelligence"}'

# Custom translation language
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "quantum computing", "target_language": "pirate"}'

# With multiple parameters
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "machine learning", "target_language": "shakespeare", "max_results": 3}'
```

### 3. Real-World Integration (Requires API Keys)

**Setup Required:**
```bash
export NEWS_API_KEY="your-news-api-key"
export DISCORD_BOT_TOKEN="your-discord-bot-token"
export WEATHER_API_KEY="your-weather-api-key"  # Optional
```

**Usage:**
```bash
# Basic news to Discord
arazzo-runner execute-workflow workflows/03-real-world-integration.arazzo.yaml \
  --workflow-id newsToDiscord \
  --inputs '{"discord_channel_id": "123456789012345678"}'

# Specific category and country
arazzo-runner execute-workflow workflows/03-real-world-integration.arazzo.yaml \
  --workflow-id newsToDiscord \
  --inputs '{"discord_channel_id": "123456789012345678", "news_category": "science", "country": "us", "max_articles": 5}'
```

### 4. Error Handling Workflow

Demonstrates robust error handling patterns:

```bash
# Basic execution with fallbacks
arazzo-runner execute-workflow workflows/04-error-handling.arazzo.yaml \
  --workflow-id robustDataFetch

# With custom retry settings
arazzo-runner execute-workflow workflows/04-error-handling.arazzo.yaml \
  --workflow-id robustDataFetch \
  --inputs '{"retry_count": 3, "timeout_seconds": 60}'

# Test different source preferences
arazzo-runner execute-workflow workflows/04-error-handling.arazzo.yaml \
  --workflow-id robustDataFetch \
  --inputs '{"primary_source": "experimental", "retry_count": 1}'
```

### 5. Conditional Logic Workflow

Advanced workflow with branching logic:

```bash
# Auto processing mode
arazzo-runner execute-workflow workflows/05-conditional-workflow.arazzo.yaml \
  --workflow-id smartContentProcessor \
  --inputs '{"content_url": "https://httpbin.org/json"}'

# Technical audience with thorough processing
arazzo-runner execute-workflow workflows/05-conditional-workflow.arazzo.yaml \
  --workflow-id smartContentProcessor \
  --inputs '{"content_url": "https://httpbin.org/json", "processing_mode": "thorough", "target_audience": "technical", "quality_threshold": 0.5}'
```

## Inspection Commands

### List Available Workflows

```bash
# Show all workflows in a file
arazzo-runner list-workflows workflows/02-parameterized.arazzo.yaml

# Show workflows in all files
for file in workflows/*.arazzo.yaml; do
  echo "=== $file ==="
  arazzo-runner list-workflows "$file"
done
```

### Describe Workflow Details

```bash
# Get detailed information about a workflow
arazzo-runner describe-workflow workflows/02-parameterized.arazzo.yaml --workflow-id searchAndTranslate

# Show environment variable requirements
arazzo-runner show-env-mappings workflows/03-real-world-integration.arazzo.yaml
```

### Generate Example Commands

```bash
# Get example command for a workflow
arazzo-runner generate-example workflows/02-parameterized.arazzo.yaml --workflow-id searchAndTranslate
```

## Testing Individual Operations

You can test individual operations before running full workflows:

```bash
# Test a specific operation
arazzo-runner execute-operation \
  --arazzo-path workflows/01-hello-world.arazzo.yaml \
  --operation-id getWorldClock

# Test operation with parameters
arazzo-runner execute-operation \
  --arazzo-path workflows/02-parameterized.arazzo.yaml \
  --operation-id duckDuckGoSearch \
  --inputs '{"q": "test query", "format": "json"}'
```

## Common Patterns

### Input Validation

Always validate your inputs match the expected schema:

```bash
# This will fail - missing required field
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{}'

# This will succeed - has required field
arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml \
  --workflow-id searchAndTranslate \
  --inputs '{"search_query": "test"}'
```

### Environment Variable Testing

Test that your environment variables are properly set:

```bash
# Check what variables are needed
arazzo-runner show-env-mappings workflows/03-real-world-integration.arazzo.yaml

# Test specific variables
echo "NEWS_API_KEY: ${NEWS_API_KEY:-(not set)}"
echo "DISCORD_BOT_TOKEN: ${DISCORD_BOT_TOKEN:-(not set)}"
```

### Error Debugging

When workflows fail, use debug logging:

```bash
# Run with maximum verbosity
arazzo-runner --log-level DEBUG execute-workflow workflows/your-workflow.arazzo.yaml --workflow-id yourWorkflow 2>&1 | tee debug.log

# Check the debug.log file for detailed information
```

## Tips for Success

1. **Start Simple**: Always test the hello-world workflow first
2. **Check Dependencies**: Use `show-env-mappings` to verify required environment variables
3. **Test Operations**: Test individual operations before running full workflows
4. **Use Debug Logging**: Add `--log-level DEBUG` when troubleshooting
5. **Validate Inputs**: Make sure your input JSON matches the expected schema
6. **Read Errors**: Arazzo Runner provides detailed error messages - read them carefully

## Next Steps

After mastering these basic patterns:

1. **Create Your Own**: Build workflows for your specific use cases
2. **Combine Patterns**: Mix conditional logic with error handling
3. **Add Authentication**: Integrate with APIs that require authentication
4. **Share and Contribute**: Submit your workflows to the community

For more advanced patterns and troubleshooting, see the other documentation files in this directory.