# Example Prompts for Testing

This file contains example prompts to get you started. Copy these and test them with `python test_prompt.py "prompt text here"`.

## Simple Information Retrieval

### Weather Queries
```
What's the current weather in San Francisco?
```
```
Get the weather forecast for London for the next 3 days
```

### Research and Articles
```
Find the latest 3 research papers about artificial intelligence on Figshare
```
```
Search for recent articles about climate change from reliable news sources
```

### Translation
```
Translate "Hello, how are you today?" to Spanish
```
```
Translate this text to Yoda speak: "The force is strong with you"
```

## Multi-Step Workflows

### Research and Share
```
Find the latest AI research papers on Figshare, summarize the top 3, and prepare a brief report
```
```
Search for today's top technology news and create a summary suitable for sharing on social media
```

### Content Processing
```
Search for articles about renewable energy, summarize them, and translate the summary to French
```
```
Find information about the latest space missions and create a brief, engaging summary
```

## Communication Tasks

### Notifications and Messaging
```
Create a professional email summary of today's important tech news
```
```
Prepare a Discord message announcing the latest developments in quantum computing
```

## Advanced Prompts

### Conditional Logic
```
Check the weather in New York. If it's raining, suggest indoor activities. If it's sunny, suggest outdoor activities.
```
```
Find the latest research papers on machine learning. If there are more than 5 results, summarize just the top 3. Otherwise, summarize all of them.
```

### Conversational Context
```
Based on our previous conversation, provide an update on the topics we discussed
```
```
Remember my interest in sustainable technology and find recent developments in that area
```

## Error Testing Prompts

### Intentional Edge Cases
```
Find information about a completely made-up topic that doesn't exist
```
```
Search for articles published tomorrow (future date)
```
```
Translate an empty string to every language
```

## Creative and Fun Prompts

### Entertainment
```
Find interesting facts about space and present them as a fun quiz
```
```
Create a short story based on today's technology news headlines
```

### Learning and Education
```
Explain quantum computing in simple terms suitable for a 10-year-old
```
```
Find the most interesting scientific discovery this week and explain why it matters
```

## Performance Testing

### Quick Tasks (< 30 seconds expected)
```
What's 2+2?
```
```
Translate "hello" to French
```

### Medium Tasks (30-60 seconds expected)
```
Summarize the latest news about renewable energy
```
```
Find and explain the most recent breakthrough in medical research
```

### Complex Tasks (1-2 minutes expected)
```
Research the current state of autonomous vehicles, find recent developments, and create a comprehensive summary with pros and cons
```
```
Find information about climate change solutions, analyze different approaches, and present a balanced overview
```

## Usage Tips

1. **Start Simple**: Begin with basic prompts to verify your setup
2. **Add Complexity Gradually**: Build up to more complex multi-step workflows  
3. **Test Variations**: Try different phrasings for the same task
4. **Document Results**: Keep notes on what works well and what doesn't
5. **Share Successes**: Add your best prompts to the collection

## Creating Your Own Prompts

### Good Prompt Characteristics
- **Clear intent**: Specific about desired outcome
- **Realistic scope**: Achievable with available APIs
- **Good context**: Provides necessary background information
- **Format guidance**: Specifies how results should be presented

### Prompt Templates

**Information Retrieval**:
```
Find [specific topic] from [source/timeframe] and [present format]
```

**Multi-step Processing**:
```
[Step 1: gather], then [Step 2: process], finally [Step 3: deliver]
```

**Conditional Logic**:
```
Check [condition]. If [scenario A], then [action A]. If [scenario B], then [action B].
```

Remember: The best prompts are specific, testable, and useful for real-world scenarios!