# AI News Summarizer Workflow Guide

## Overview

The AI News Summarizer is a custom Arazzo workflow that demonstrates real-world API integration by combining multiple services to create intelligent news summaries. This workflow showcases advanced Arazzo patterns including multi-API coordination, authentication, error handling, and conditional logic.

## What It Does

1. **Fetches Latest News** - Retrieves current news articles from NewsAPI
2. **Validates Data** - Ensures we received valid news data
3. **Prepares Content** - Formats articles for AI processing
4. **Generates AI Summary** - Uses OpenAI GPT to create intelligent summaries
5. **Creates Final Report** - Formats the results with metadata
6. **Handles Errors** - Provides graceful error handling and reporting

## Key Features

### ✅ Multi-API Integration
- **NewsAPI** for fetching current news articles
- **OpenAI API** for generating AI-powered summaries
- **HTTPBin** for data validation and formatting (simulated services)

### ✅ Authentication Patterns
- **API Key Authentication** with NewsAPI (`X-API-Key` header)
- **Bearer Token Authentication** with OpenAI (`Authorization: Bearer` header)
- **Environment Variable Management** for secure credential handling

### ✅ Advanced Workflow Patterns
- **Conditional Execution** - Steps run based on validation results
- **Error Handling** - Dedicated error path with meaningful reporting
- **Data Flow** - Complex parameter passing between steps
- **Dependency Management** - Proper step ordering with `dependsOn`

### ✅ Parameterization
- **Configurable Inputs** - News category, article count, summary style
- **Default Values** - Sensible defaults for all parameters
- **Input Validation** - Enum constraints and type checking

## Usage Examples

### Basic Usage
```bash
# Run with default parameters (technology news, 3 articles, concise summary)
arazzo-runner execute-workflow workflows/06-ai-news-summarizer.arazzo.yaml \
  --workflow-id aiNewsSummarizer
```

### Custom Parameters
```bash
# Business news with detailed summaries for technical audience
arazzo-runner execute-workflow workflows/06-ai-news-summarizer.arazzo.yaml \
  --workflow-id aiNewsSummarizer \
  --inputs '{
    "news_category": "business",
    "max_articles": 5,
    "summary_style": "detailed",
    "target_audience": "technical"
  }'
```

### Science News with Bullet Points
```bash
arazzo-runner execute-workflow workflows/06-ai-news-summarizer.arazzo.yaml \
  --workflow-id aiNewsSummarizer \
  --inputs '{
    "news_category": "science",
    "max_articles": 2,
    "summary_style": "bullet-points",
    "target_audience": "academic"
  }'
```

## Input Parameters

| Parameter | Type | Default | Description | Options |
|-----------|------|---------|-------------|---------|
| `news_category` | string | "technology" | Category of news to fetch | business, entertainment, general, health, science, sports, technology |
| `max_articles` | integer | 3 | Number of articles to process | 1-5 |
| `summary_style` | string | "concise" | AI summary style | concise, detailed, bullet-points, executive |
| `target_audience` | string | "general" | Target audience for summary | general, technical, business, academic |

## Workflow Steps Explained

### 1. fetchLatestNews
- **Purpose**: Retrieves current news articles from NewsAPI
- **Authentication**: Uses `NEWS_API_KEY` environment variable
- **Parameters**: Category, page size, country code
- **Outputs**: Articles array, total results, API status

### 2. validateNewsData
- **Purpose**: Validates that we received valid news data
- **Dependencies**: fetchLatestNews
- **Logic**: Checks article count and data structure
- **Outputs**: Validation status, article count, validation message

### 3. prepareArticlesForAI
- **Purpose**: Formats articles for optimal AI processing
- **Dependencies**: validateNewsData
- **Condition**: Only runs if validation passed
- **Outputs**: Formatted content, article titles, word count

### 4. generateAISummary
- **Purpose**: Creates AI-powered summary using OpenAI GPT
- **Authentication**: Uses `OPENAI_API_KEY` environment variable
- **Dependencies**: prepareArticlesForAI
- **Parameters**: Content, style, audience, token limits
- **Outputs**: AI summary, token usage, model information

### 5. createFinalReport
- **Purpose**: Formats final report with metadata
- **Dependencies**: generateAISummary
- **Logic**: Combines original articles, AI summary, and processing metadata
- **Outputs**: Formatted report, metadata, success status

### 6. handleError
- **Purpose**: Handles validation or processing failures
- **Dependencies**: validateNewsData
- **Condition**: Only runs if validation failed
- **Outputs**: Error report, recommendations, failure status

## Error Handling

The workflow includes comprehensive error handling:

- **Validation Failures**: If news fetching fails or returns invalid data
- **API Errors**: Graceful handling of NewsAPI or OpenAI API failures
- **Conditional Logic**: Error path only executes when needed
- **Meaningful Messages**: Detailed error reports with recommendations

## Authentication Requirements

### Required Environment Variables
```bash
# NewsAPI key (get from https://newsapi.org)
NEWS_API_KEY=your_news_api_key_here

# OpenAI API key (get from https://platform.openai.com)
OPENAI_API_KEY=your_openai_api_key_here
```

### Setting Up API Keys
1. **NewsAPI**: Sign up at https://newsapi.org for free tier
2. **OpenAI**: Create account at https://platform.openai.com
3. **Environment**: Add keys to `.env` file in track directory

## Expected Outputs

### Successful Execution
```json
{
  "workflow_id": "aiNewsSummarizer",
  "status": "completed",
  "outputs": {
    "final_report": "Formatted report with AI summary",
    "report_metadata": {
      "category": "technology",
      "article_count": 3,
      "tokens_used": 245,
      "model_used": "gpt-4",
      "style": "concise",
      "audience": "general"
    },
    "success": true
  }
}
```

### Error Case
```json
{
  "workflow_id": "aiNewsSummarizer",
  "status": "completed",
  "outputs": {
    "error_report": "Failed to fetch valid news articles",
    "recommendations": ["Check API key", "Try different category"],
    "success": false
  }
}
```

## Troubleshooting

### Common Issues

**"401 Unauthorized" from NewsAPI**
- Check `NEWS_API_KEY` environment variable is set
- Verify API key is valid and not expired
- Ensure you haven't exceeded rate limits

**"401 Unauthorized" from OpenAI**
- Check `OPENAI_API_KEY` environment variable is set
- Verify API key format (starts with 'sk-')
- Ensure you have sufficient credits

**"No articles found"**
- Try different news category
- Check if NewsAPI is experiencing issues
- Verify country code and parameters

### Debug Commands
```bash
# Check environment variables
arazzo-runner show-env-mappings workflows/06-ai-news-summarizer.arazzo.yaml

# Run with debug logging
arazzo-runner --log-level DEBUG execute-workflow \
  workflows/06-ai-news-summarizer.arazzo.yaml \
  --workflow-id aiNewsSummarizer

# Test individual operations
arazzo-runner execute-operation \
  --arazzo-path workflows/06-ai-news-summarizer.arazzo.yaml \
  --operation-id getTopHeadlines
```

## Real-World Applications

This workflow pattern can be adapted for:

- **Content Curation**: Automated content aggregation and summarization
- **Business Intelligence**: Market news analysis and reporting
- **Research Assistance**: Academic paper summarization
- **Social Media**: Automated posting of news summaries
- **Internal Communications**: Company news digests
- **Competitive Analysis**: Industry trend monitoring

## Technical Achievements

This workflow demonstrates mastery of:

1. **Multi-API Orchestration** - Coordinating NewsAPI and OpenAI
2. **Authentication Patterns** - Multiple auth methods in one workflow
3. **Error Handling** - Robust failure management and reporting
4. **Conditional Logic** - Smart execution paths based on data
5. **Data Transformation** - Processing data between different API formats
6. **Parameter Management** - Flexible, configurable workflow inputs
7. **Real-World Value** - Solving actual content summarization needs

## Next Steps

To extend this workflow:

1. **Add More APIs** - Weather, stock prices, social media
2. **Enhance AI Processing** - Sentiment analysis, topic extraction
3. **Output Formats** - Email, Slack, Discord integration
4. **Scheduling** - Automated daily/hourly execution
5. **Personalization** - User preferences and filtering
6. **Analytics** - Track usage and performance metrics

This workflow serves as a foundation for building sophisticated API orchestration solutions using Arazzo.