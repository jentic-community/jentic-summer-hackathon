# Track 08 – Chrome Extension for API Discovery

**Goal**: Build a browser extension that automatically discovers and generates OpenAPI specifications from any website by analyzing network traffic and API calls.

**Time Estimate**: 4-6 hours  
**Difficulty**: Beginner to Intermediate  
**Perfect for**: Web developers interested in browser APIs, reverse engineering, and making hidden APIs discoverable

## What You'll Build

A Chrome extension that:
- **Monitors network requests** on any website
- **Identifies API patterns** from HTTP traffic
- **Generates OpenAPI specifications** automatically
- **Exports results** for use with Jentic and other tools
- **Provides a simple UI** for users to trigger discovery

**Your deliverable**: A working Chrome extension that users can install and use to discover APIs on any website with a single click.

## Prerequisites

### Technical Requirements
- Basic understanding of JavaScript and web APIs
- Familiarity with Chrome extension development (helpful but not required)
- Understanding of HTTP requests and responses
- Basic knowledge of JSON and API structures

### Knowledge Prerequisites
- Understanding of REST APIs and HTTP methods
- Basic familiarity with OpenAPI/Swagger format
- Knowledge of browser developer tools
- No advanced programming experience required

## The Problem

Many websites use **undocumented APIs** that could be useful:
- **Internal APIs** that power web applications
- **Mobile APIs** that aren't publicly documented  
- **AJAX endpoints** that handle dynamic content
- **Search and filtering APIs** that process user queries
- **Data APIs** that fetch content without page refreshes

**Your extension will make these APIs discoverable and usable.**

## Getting Started (30 minutes)

### 1. Project Setup
```bash
# Create project directory
mkdir chrome-api-discovery
cd chrome-api-discovery

# Create basic extension structure
mkdir -p src/
mkdir -p icons/
mkdir -p popup/
mkdir -p background/
mkdir -p content/
```

### 2. Understanding Chrome Extension Architecture
Your extension will have these components:

**Manifest v3 Structure**:
- **Background script** - Monitors network requests
- **Content script** - Interacts with web pages
- **Popup UI** - User interface for starting discovery
- **Storage** - Saves discovered API patterns

### 3. Test Your Development Setup
```bash
# Start with a basic extension
# Load extension in Chrome:
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked" and select your project folder
```

## Your Implementation Tasks

### Phase 1: Basic Extension Framework (90 minutes)

#### Task 1: Create Extension Manifest
Build the manifest.json that defines your extension:
- Extension metadata and permissions
- Background script registration
- Content script injection
- Network request monitoring permissions

**Deliverable**: Working extension that loads in Chrome.

**File to create**: `manifest.json`

#### Task 2: Build Popup Interface  
Create a simple user interface:
- Button to start/stop API discovery
- Display of discovered endpoints
- Export functionality for OpenAPI specs
- Status indicators and progress feedback

**Deliverable**: Functional popup that communicates with background script.

**Files to create**: 
- `popup/popup.html`
- `popup/popup.js` 
- `popup/popup.css`

#### Task 3: Implement Network Monitoring
Set up background script to monitor network traffic:
- Listen to all HTTP requests
- Filter for API-like requests (JSON, XML, etc.)
- Store request/response data
- Identify patterns and endpoints

**Deliverable**: Background script that captures API traffic.

**File to create**: `background/background.js`

### Phase 2: API Pattern Recognition (120 minutes)

#### Task 4: Request Analysis Engine
Build logic to identify API patterns:

**HTTP Method Detection**:
- Identify REST operations (GET, POST, PUT, DELETE)
- Classify request types (data fetch, form submission, etc.)
- Detect authentication patterns

**Endpoint Pattern Recognition**:
- Extract base URLs and path patterns
- Identify parameter patterns in URLs
- Group related endpoints by functionality

**Data Structure Analysis**:
- Analyze JSON request/response structures
- Identify common schema patterns  
- Extract parameter types and formats

**Deliverable**: Engine that can identify and classify API patterns.

#### Task 5: Content Analysis
Enhance analysis with page context:
- Identify what user actions trigger API calls
- Correlate UI elements with API endpoints
- Extract meaningful operation descriptions
- Detect authentication requirements

**Deliverable**: Context-aware API discovery.

**File to create**: `content/content.js`

### Phase 3: OpenAPI Generation (90 minutes)

#### Task 6: OpenAPI Spec Builder
Create logic to generate valid OpenAPI specifications:

**Basic Structure Generation**:
- Create OpenAPI 3.0+ compliant structure
- Generate info section with discovered metadata
- Build servers array from detected base URLs
- Organize paths by discovered endpoints

**Schema Inference**:
- Analyze JSON payloads to infer schemas
- Generate request body schemas
- Create response schemas with examples
- Define parameter schemas with types

**Documentation Enhancement**:
- Generate operation descriptions from context
- Create meaningful operation IDs
- Add tags for logical grouping
- Include examples from captured traffic

**Deliverable**: Function that converts discovered APIs to OpenAPI specs.

#### Task 7: Export and Integration
Implement export functionality:
- Generate downloadable OpenAPI files
- Validate generated specifications
- Provide integration options with Jentic
- Support multiple export formats (YAML/JSON)

**Deliverable**: Complete export workflow for discovered APIs.

## Testing Your Extension

### Basic Functionality Tests
```bash
# Test extension loading
1. Load extension in Chrome developer mode
2. Verify popup opens and displays UI
3. Check background script loads without errors
4. Confirm content script injection works

# Test network monitoring
1. Navigate to a website with AJAX calls
2. Start API discovery in popup
3. Verify network requests are captured
4. Check discovered endpoints appear in UI
```

### API Discovery Tests
Test with websites that have clear API patterns:

**Good Test Sites**:
- **GitHub** - Repository APIs, user APIs
- **Reddit** - Post and comment APIs  
- **News sites** - Article loading APIs
- **E-commerce** - Product search APIs
- **Social media** - Content feed APIs

**Test Process**:
1. Enable extension on test site
2. Perform user actions (search, navigate, etc.)
3. Review discovered API endpoints
4. Export OpenAPI specification
5. Validate generated spec with online tools

### Edge Case Testing
```bash
# Test with challenging scenarios
- Sites with authentication requirements
- Sites with complex parameter structures
- Sites with GraphQL endpoints
- Sites with WebSocket connections
- Sites with rate limiting
```

## Deliverables

### Minimum Viable Product
- [ ] **Working Chrome extension** that installs and runs
- [ ] **Network traffic monitoring** captures HTTP requests
- [ ] **Basic API discovery** identifies endpoints and methods
- [ ] **Simple export** generates basic OpenAPI specs
- [ ] **User interface** allows starting/stopping discovery

### Enhanced Implementation
- [ ] **Smart pattern recognition** identifies API structures
- [ ] **Context-aware discovery** correlates UI actions with APIs
- [ ] **Schema inference** generates detailed request/response schemas
- [ ] **Quality validation** ensures generated specs are valid
- [ ] **Integration options** with Jentic and other tools

### Professional Quality
- [ ] **Advanced analysis** handles complex API patterns
- [ ] **Batch processing** discovers multiple APIs simultaneously
- [ ] **Historical tracking** saves and compares discoveries
- [ ] **Sharing capabilities** exports to cloud services
- [ ] **Performance optimization** for large-scale discovery

## Common Challenges & Solutions

### Chrome Extension Development
**Challenge**: Understanding Chrome extension architecture
**Solutions**:
- Start with official Chrome extension documentation
- Use simple examples to understand message passing
- Test each component (popup, background, content) separately
- Use Chrome DevTools for debugging

### Network Request Analysis
**Challenge**: Filtering relevant API calls from all network traffic
**Solutions**:
- Focus on XHR and Fetch requests initially
- Filter by content type (application/json, etc.)
- Look for consistent URL patterns
- Ignore static assets (images, CSS, JS files)

### OpenAPI Generation Quality
**Challenge**: Creating meaningful and accurate specifications
**Solutions**:
- Start with basic structure, add sophistication gradually
- Use captured request/response data as examples
- Validate generated specs with online validators
- Focus on most common API patterns first

## Extension Architecture

### File Structure
```
chrome-api-discovery/
├── manifest.json              # Extension configuration
├── icons/
│   ├── icon16.png            # Extension icons
│   ├── icon48.png
│   └── icon128.png
├── popup/
│   ├── popup.html            # Popup interface
│   ├── popup.js              # Popup logic
│   └── popup.css             # Popup styling
├── background/
│   └── background.js         # Network monitoring
├── content/
│   └── content.js            # Page interaction
├── lib/
│   ├── api-analyzer.js       # API pattern analysis
│   ├── openapi-generator.js  # OpenAPI spec generation
│   └── utils.js              # Utility functions
└── README.md
```

### Key Components

**Manifest.json**:
- Defines extension permissions
- Specifies background and content scripts
- Declares popup and icon resources

**Background Script**:
- Monitors network requests via webRequest API
- Stores discovered API data
- Handles communication with popup

**Content Script**:
- Observes user interactions on web pages
- Provides context for API discovery
- Communicates findings to background script

**Popup Interface**:
- Provides user controls for discovery
- Displays discovered APIs
- Handles export functionality

## Getting Help

### Development Setup
```javascript
// Test basic extension functionality
console.log('Extension loaded');

// Test network request monitoring
chrome.webRequest.onCompleted.addListener(
  function(details) {
    console.log('Request captured:', details.url);
  },
  {urls: ["<all_urls>"]},
  ["responseHeaders"]
);
```

### Debugging Tips
- Use Chrome DevTools to debug popup and content scripts
- Check chrome://extensions/ for extension errors
- Use background page DevTools for background script debugging
- Test with simple websites before complex ones

### Support Resources
- **Chrome Extension Documentation**: Official developer guides
- **WebRequest API**: Network monitoring documentation
- **OpenAPI Specification**: Format documentation and examples
- **Discord Support**: #summer-hackathon for real-time help

## Extension Permissions

Your extension will need these permissions:

```json
{
  "permissions": [
    "webRequest",           // Monitor network requests
    "storage",             // Store discovered APIs
    "activeTab",           // Access current tab
    "scripting"            // Inject content scripts
  ],
  "host_permissions": [
    "<all_urls>"           // Access all websites
  ]
}
```

## Security Considerations

- **Data Privacy**: Don't store sensitive information
- **User Consent**: Clear about what data is collected
- **Secure Storage**: Use Chrome storage APIs appropriately
- **Permission Scope**: Request minimal necessary permissions

## Extension Publishing (Optional)

If you want to share your extension:
1. Create developer account on Chrome Web Store
2. Package extension as .zip file
3. Submit for review with proper description
4. Include privacy policy and usage instructions

## Success Criteria

Your extension succeeds when:
1. **Users can easily discover APIs** on any website
2. **Generated OpenAPI specs are valid** and useful
3. **Extension is reliable** and doesn't break websites
4. **User interface is intuitive** and responsive
5. **Results integrate well** with existing API tools

## Real-World Impact

This extension addresses important needs:
- **API Discoverability**: Makes hidden APIs accessible
- **Documentation Generation**: Creates specs for undocumented APIs
- **Developer Productivity**: Speeds up API integration
- **Ecosystem Growth**: Expands available APIs for agents and developers

Remember: **Start with basic network monitoring**, validate the approach with simple sites, then add sophisticated analysis. The goal is to create a practical tool that genuinely helps developers discover and use APIs!