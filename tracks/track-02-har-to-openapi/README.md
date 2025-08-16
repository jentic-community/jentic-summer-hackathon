# Track 02 – HAR → OpenAPI

**Goal**: Reverse engineer undocumented APIs by capturing HTTP traffic and converting it to OpenAPI specifications.

**Time Estimate**: 2-4 hours  
**Difficulty**: Beginner to Intermediate  
**Perfect for**: Developers interested in API discovery, reverse engineering, and expanding Jentic's API catalog

## What You'll Build

A systematic approach and/or tooling to:
- Capture real API traffic using HAR (HTTP Archive) files
- Analyze and sanitize the captured data
- Convert HTTP requests/responses into valid OpenAPI 3.0+ specifications
- Submit high-quality API specs to Jentic Public APIs

**Example outcome**: Transform a hidden property search API into a documented, usable OpenAPI spec that AI agents can discover and execute.

## Prerequisites

### Technical Skills
- Basic understanding of HTTP (requests, responses, headers)
- Familiarity with JSON and YAML formats
- Browser developer tools usage
- Command-line comfort

### Tools & Accounts
- **Web Browser** with developer tools (Chrome, Firefox, Safari, Edge)
- **Text Editor** capable of handling JSON/YAML
- **Jentic Account** (for understanding API standards)
- **Python 3.11+** (for validation and scripting)

### Knowledge Prerequisites
- Understanding of REST APIs
- Basic familiarity with OpenAPI/Swagger
- Awareness of data privacy and security concerns

## Target APIs for Practice

### Beginner-Friendly Targets
- **Figshare** - Research article metadata (partially documented)
- **OpenStreetMap Nominatim** - Geocoding service
- **JSONPlaceholder** - Test REST API

### Intermediate Targets
- **Property websites** - Search and listing APIs
- **News aggregators** - Article search and content
- **E-commerce sites** - Product search and details
- **Social platforms** - Public post feeds

### Advanced Targets
- **Government data portals** - Complex query APIs
- **Financial data services** - Market data feeds
- **Specialized databases** - Academic, scientific, or industry-specific

## Step-by-Step Walkthrough

### Phase 1: Preparation and Planning (30 minutes)

#### 1. Choose Your Target API
Select a website that likely has hidden API endpoints:

**Good candidates**:
- Sites with real-time search results
- Platforms that load content without page refresh
- Services with filtering/sorting functionality
- Websites with "infinite scroll" or pagination

**Avoid**:
- Sites that explicitly prohibit API access in terms of service
- Heavily protected or authentication-required endpoints
- Sites with complex anti-bot measures

#### 2. Set Up Your Environment
```bash
# Create project directory
mkdir har-to-openapi-project
cd har-to-openapi-project

# Set up Python environment for validation
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install validation tools
pip install -r requirements.txt
```

### Phase 2: HAR Capture (45 minutes)

#### 1. Prepare Browser for Capture
1. **Open browser in incognito/private mode** (clean slate)
2. **Open Developer Tools** (F12)
3. **Navigate to Network tab**
4. **Enable settings**:
   - "Preserve log" ✓
   - "Disable cache" ✓ (optional, for consistent behavior)
5. **Clear any existing entries**

#### 2. Strategic Capture Session
Plan your capture to get comprehensive data:

```
Session Plan Example (for property site):
1. Load homepage (get base structure)
2. Perform simple search (basic search API)
3. Apply filters (filter API patterns)
4. Sort results (sorting parameters)
5. Paginate through results (pagination patterns)
6. View individual listing (detail API)
7. Perform different search (validate patterns)
```

#### 3. Execute Capture
1. **Start recording** in Network tab
2. **Follow your session plan systematically**
3. **Take notes** as you go:
   - Which actions trigger API calls
   - What parameters change between requests
   - Which responses contain useful data
4. **Save HAR file**: Right-click in Network → "Save all as HAR with content"

### Phase 3: HAR Analysis and Sanitization (60 minutes)

#### 1. Identify API Patterns
Use the provided analysis tool:

```bash
# Analyze your HAR file
python tools/har_analyzer.py capture.har

# Generate OpenAPI skeleton
python tools/har_analyzer.py capture.har --output api-skeleton.yaml
```

#### 2. Sanitize Sensitive Data
**Critical step**: Remove all sensitive information:

```bash
# Sanitize the HAR file
python tools/sanitizer.py capture.har capture_sanitized.har

# Review the sanitized file manually
# Check for any remaining sensitive data
```

#### 3. Extract Core API Information
Document your findings:
- Base URL and authentication requirements
- Discovered endpoints and their purposes
- Parameter patterns and data types
- Response structures and examples

### Phase 4: OpenAPI Specification Creation (90 minutes)

#### 1. Create Basic OpenAPI Structure
Start with the skeleton generated by the analyzer, then enhance it:

```yaml
openapi: 3.0.0
info:
  title: "Discovered API"
  description: "API specification reverse-engineered from HAR analysis"
  version: "1.0.0"
  x-jentic-source-url: "https://example.com"

servers:
  - url: "https://api.example.com"
    description: "Production API server"

paths:
  # Add your discovered endpoints here
  
components:
  schemas:
    # Define your data models here
```

#### 2. Document Each Endpoint
For each discovered API pattern, create detailed documentation with:
- Clear operation IDs and descriptions
- Comprehensive parameter definitions
- Detailed response schemas
- Error response handling
- Realistic examples

#### 3. Validate Your Specification
```bash
# Validate OpenAPI syntax
python -c "
from openapi_spec_validator import validate_spec
import yaml
with open('openapi.yaml') as f:
    spec = yaml.safe_load(f)
validate_spec(spec)
print('✅ OpenAPI specification is valid!')
"
```

### Phase 5: Testing and Refinement (45 minutes)

#### 1. Create Test Workflow
Test your spec with Arazzo Runner:

```yaml
# test-workflow.arazzo.yaml
arazzo: 1.0.0
info:
  title: Test Discovered API
  version: 1.0.0

workflows:
  - workflowId: testAPI
    description: Test the discovered API endpoints
    steps:
      - stepId: search
        operationRef: 'openapi.yaml#/operations/searchItems'
        parameters:
          query: "test"
```

#### 2. Manual Testing
```bash
# Test individual endpoints
arazzo-runner execute-operation \
  --openapi-path openapi.yaml \
  --operation-id searchItems \
  --inputs '{"query": "test"}'
```

#### 3. Iterate and Improve
Based on testing results:
- Fix validation errors
- Update parameter descriptions
- Add missing response fields
- Improve error handling documentation

## Deliverables

### Minimum Viable Product
- [ ] **Sanitized HAR file** with evidence of API discovery
- [ ] **Valid OpenAPI 3.0+ specification** for at least 2 endpoints
- [ ] **Documentation** explaining the discovery process
- [ ] **Basic validation** showing the spec works

### Enhanced Version
- [ ] **Comprehensive API coverage** (5+ endpoints)
- [ ] **Test workflow** demonstrating API usage
- [ ] **Analysis script** for automated HAR processing
- [ ] **Detailed documentation** with examples and troubleshooting

### Professional Quality
- [ ] **Production-ready OpenAPI spec** with complete schemas
- [ ] **Automated conversion tooling** for similar APIs
- [ ] **Security analysis** and best practices documentation
- [ ] **Contribution to Jentic Public APIs** repository

## Common Challenges & Solutions

### Discovery Challenges
**Challenge**: Website doesn't use traditional REST APIs
**Solutions**:
- Look for GraphQL endpoints (single `/graphql` endpoint)
- Check for WebSocket connections (real-time data)
- Examine POST requests with JSON payloads
- Consider server-sent events or other patterns

### Technical Challenges
**Challenge**: Complex authentication flows
**Solutions**:
- Document the full OAuth/login sequence
- Look for refresh token patterns
- Check for CSRF tokens or nonces
- Consider session-based auth as alternative

### Quality Challenges
**Challenge**: Incomplete or unclear documentation
**Solutions**:
- Test edge cases manually to understand behavior
- Look at multiple examples to identify patterns
- Use schema inference tools for complex objects
- Ask for community feedback on your analysis

## Extension Ideas

### For Tool Builders
- **Generic HAR Converter** - Tool that converts any HAR to OpenAPI
- **Pattern Recognition** - ML-based endpoint pattern detection
- **Schema Inference** - Automatically generate schemas from response data

### For API Hunters
- **Specialized Converters** - Focus on specific industries (e-commerce, news, etc.)
- **Multi-site Analysis** - Compare similar APIs across different sites
- **Historical Analysis** - Track API changes over time

## Submission Guidelines

### File Structure
```
har-to-openapi-project/
├── README.md                 # Project documentation
├── discovery-report.md       # Analysis and findings
├── captures/
│   ├── raw-capture.har      # Original HAR file
│   └── sanitized-capture.har # Cleaned HAR file
├── specs/
│   ├── api-spec.yaml        # Final OpenAPI specification
│   └── test-workflow.arazzo.yaml # Test workflow
├── tools/
│   ├── har_analyzer.py      # Analysis scripts
│   ├── sanitizer.py         # Data cleaning tools
│   └── validator.py         # Validation utilities
└── examples/
    ├── sample-requests.md   # Example API calls
    └── response-samples/    # Example responses
```

### Quality Criteria
- **Completeness**: Spec covers main functionality discovered
- **Accuracy**: Spec matches actual API behavior
- **Documentation**: Clear descriptions and examples
- **Security**: All sensitive data properly sanitized
- **Validation**: Spec passes OpenAPI validation
- **Usefulness**: API provides real value for agents/developers

## Getting Help

### Debugging HAR Capture
```bash
# Check HAR file structure
python -c "
import json
with open('capture.har') as f:
    har = json.load(f)
print(f'Entries: {len(har[\"log\"][\"entries\"])}')
"

# Find API-like requests
python tools/har_analyzer.py capture.har
```

### Support Channels
- **Technical Issues**: Discord #summer-hackathon with HAR files and error messages
- **API Discovery**: Share findings and get feedback on discovered patterns
- **OpenAPI Questions**: Get help with specification writing

Remember: The goal is to expand the universe of APIs available to AI agents. Every API you discover and document makes the ecosystem more powerful for everyone!