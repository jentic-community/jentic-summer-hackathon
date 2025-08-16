# Track 05 – OpenAPI Minifier

**Goal**: Build a tool that extracts minimal OpenAPI specifications from large, comprehensive API specs by keeping only the operations and schemas needed for specific use cases.

**Time Estimate**: 3-5 hours  
**Difficulty**: Intermediate  
**Perfect for**: Developers interested in API optimization, schema analysis, and tooling development

## What You'll Build

A smart minification tool that:
- **Analyzes large OpenAPI specifications** (10,000+ lines)
- **Identifies required operations** based on user-specified tasks
- **Extracts minimal schemas** with only necessary components
- **Generates optimized specs** that are 80-95% smaller
- **Validates output** to ensure correctness

**Your deliverable**: A tool that can take a massive Jira API spec (10,000 lines) and extract just the "create issue" functionality (400 lines) while maintaining all necessary schemas and authentication.

## Prerequisites

### Technical Requirements
- Python 3.11+
- Understanding of OpenAPI/Swagger specifications
- Basic knowledge of JSON/YAML processing
- Familiarity with graph traversal algorithms (helpful)

### Knowledge Prerequisites
- Understanding of API specification structure
- Basic schema validation concepts
- JSON path expressions (helpful)
- Dependency graph concepts (helpful)

## The Problem

Modern API specifications are **massive and complex**:
- **Jira API**: ~10,000 lines with 200+ operations
- **GitHub API**: ~15,000 lines with 300+ operations  
- **Salesforce API**: ~50,000+ lines with 500+ operations

But AI agents typically need only **1-5 specific operations**:
- "Create a Jira issue" (needs ~5% of the full spec)
- "Send a Slack message" (needs ~2% of the full spec)
- "Get weather data" (needs ~10% of the full spec)

**The challenge**: Extract exactly what's needed while maintaining API correctness.

## Getting Started (30 minutes)

### 1. Environment Setup
```bash
# Create project directory
mkdir openapi-minifier
cd openapi-minifier

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install starter dependencies
pip install -r requirements.txt
```

### 2. Understand the Structure
Your minifier will have these components:
- **Parser**: Load and analyze OpenAPI specs
- **Analyzer**: Find dependencies between operations and schemas
- **Extractor**: Build minimal specs with required components
- **Validator**: Ensure output specs are correct

### 3. Study the Examples
```bash
# Look at example large API specs
ls examples/large-specs/

# See what minified output should look like
ls examples/minified-output/

# Run the test suite to understand expected behavior
python test_minifier.py
```

## Your Implementation Tasks

### Phase 1: Basic Minification (90 minutes)

#### Task 1: Build the OpenAPI Parser
Create a parser that can:
- Load OpenAPI specs from YAML/JSON files
- Navigate the specification structure
- Identify all operations (paths + methods)
- Extract schema definitions

**Deliverable**: A parser that can load and understand OpenAPI specs.

**Files to implement**:
- `minifier/parser.py` - OpenAPI parsing logic
- Test with: `python test_minifier.py test_parser`

#### Task 2: Implement Operation Selection
Build logic that can:
- Match user requests to specific operations
- Support different selection methods:
  - By operation ID: `"createIssue"`
  - By path + method: `"POST /rest/api/3/issue"`
  - By description search: `"create a new issue"`

**Deliverable**: A system that can find the right operations from user input.

#### Task 3: Basic Schema Extraction
Implement dependency tracking that:
- Finds all schemas used by selected operations
- Includes request body schemas
- Includes response schemas  
- Includes parameter schemas

**Deliverable**: A function that returns all schemas needed for specific operations.

### Phase 2: Smart Dependency Resolution (90 minutes)

#### Task 4: Build Dependency Graph
Create a system that:
- Maps all schema references (`$ref`)
- Builds a dependency graph of schemas
- Handles nested dependencies (schema A uses schema B uses schema C)
- Detects circular references

**Deliverable**: A dependency resolver that finds all required schemas transitively.

#### Task 5: Component Optimization
Implement smart extraction that:
- Keeps only used properties from schemas
- Removes unused `allOf`/`oneOf`/`anyOf` branches
- Strips unnecessary examples and descriptions (optional)
- Preserves authentication and server information

**Deliverable**: Optimized extraction that goes beyond basic dependency following.

### Phase 3: Advanced Features (60+ minutes)

#### Task 6: Multiple Operations Support
Extend your tool to handle:
- Multiple operations in a single minified spec
- Shared schemas between operations
- Optimal schema reuse to minimize output size

#### Task 7: Validation and Quality Assurance
Implement validation that:
- Ensures output specs are valid OpenAPI
- Verifies all references resolve correctly
- Checks that operations are still functional
- Provides quality metrics (size reduction, completeness)

### Phase 4: Polish and CLI (Optional, 60 minutes)

#### Task 8: Command-Line Interface
Build a CLI tool that supports:
- Different input/output formats (YAML/JSON)
- Multiple selection methods
- Batch processing
- Configuration options

#### Task 9: Advanced Analysis
Add features like:
- Unused schema detection in original specs
- Complexity analysis and recommendations
- Performance benchmarking
- Integration with OpenAPI validation tools

## Provided Starter Framework

### Core Classes Structure
```python
# minifier/spec_minifier.py - Main class you'll implement
class OpenAPIMinifier:
    def __init__(self):
        # TODO: Initialize parser, analyzer, extractor
        pass
    
    def minify(self, spec_path: str, operations: List[str]) -> dict:
        # TODO: Main minification logic
        pass
    
    def analyze_dependencies(self, spec: dict, operations: List[str]) -> set:
        # TODO: Find all required schemas and components
        pass
```

### Test Framework
```python
# test_minifier.py - Tests your implementation should pass
def test_basic_minification():
    # Test with simple spec and single operation
    pass

def test_dependency_resolution():
    # Test complex nested schema dependencies
    pass

def test_multiple_operations():
    # Test with multiple operations sharing schemas
    pass
```

### Example Data
- **Large API specs** for testing (Jira, GitHub, etc.)
- **Expected output examples** showing correct minification
- **Test cases** with known good inputs/outputs

## Implementation Guidance

### Understanding OpenAPI Structure
```yaml
# Key sections you'll work with:
openapi: 3.0.0
info: { ... }
servers: [ ... ]
paths:
  /api/endpoint:
    post:
      operationId: "createSomething"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateRequest"
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/CreateResponse"
components:
  schemas:
    CreateRequest: { ... }
    CreateResponse: { ... }
  securitySchemes: { ... }
```

### Dependency Resolution Strategy
1. **Start with selected operations**
2. **Find direct schema references** in request/response bodies
3. **Recursively resolve** all `$ref` dependencies
4. **Include security schemes** used by operations
5. **Preserve server and info** sections

### Common Challenges
- **Circular references** between schemas
- **Conditional schemas** (oneOf/anyOf/allOf)
- **External references** to other files
- **Polymorphic schemas** with inheritance
- **Security scheme dependencies**

### Size Optimization Techniques
- **Remove unused properties** from schemas
- **Simplify complex schemas** when possible
- **Strip documentation** (descriptions, examples) if requested
- **Merge similar schemas** when safe
- **Remove unused security schemes**

## Testing Your Implementation

### Basic Functionality Tests
```bash
# Test parser
python test_minifier.py test_parser

# Test operation selection
python test_minifier.py test_operation_selection

# Test dependency resolution
python test_minifier.py test_dependency_resolution

# Test complete minification
python test_minifier.py test_minification
```

### Real-World Tests
```bash
# Test with large Jira spec
python minify.py examples/large-specs/jira-api.yaml --operations "createIssue"

# Test with multiple operations
python minify.py examples/large-specs/github-api.yaml --operations "createRepo,addCollaborator"

# Validate output
python validate_output.py output/minified-spec.yaml
```

### Quality Metrics
Your implementation should achieve:
- **Size reduction**: 80-95% smaller than original
- **Correctness**: All references resolve in output spec
- **Completeness**: Selected operations remain fully functional
- **Performance**: Process large specs in <30 seconds

## Deliverables

### Minimum Viable Product
- [ ] **Working minifier** that can extract single operations
- [ ] **Basic dependency resolution** for required schemas
- [ ] **Valid OpenAPI output** that passes validation
- [ ] **Command-line interface** for basic usage
- [ ] **Test suite** demonstrating functionality

### Enhanced Implementation
- [ ] **Multiple operations support** with shared schema optimization
- [ ] **Advanced dependency resolution** handling complex cases
- [ ] **Size optimization** beyond basic extraction
- [ ] **Quality metrics** and analysis reporting
- [ ] **Error handling** with helpful user feedback

### Advanced Implementation
- [ ] **Intelligent schema simplification**
- [ ] **Batch processing capabilities**
- [ ] **Integration with OpenAPI ecosystems**
- [ ] **Performance optimizations** for very large specs
- [ ] **Plugin architecture** for custom extraction rules

## Success Criteria

Your implementation succeeds when:
1. **Large APIs become manageable** - 10,000 line specs become 500 lines
2. **Output specs are functionally equivalent** for selected operations
3. **All references resolve correctly** in minified specs
4. **Tool is easy to use** with clear command-line interface
5. **Performance is acceptable** for real-world API specs

## Real-World Impact

This tool addresses a real problem:
- **Faster agent loading** - smaller specs load 10x faster
- **Reduced token usage** - LLMs process smaller specs more efficiently
- **Better focus** - agents see only relevant functionality
- **Easier debugging** - developers can understand minimal specs
- **Cost savings** - less data transfer and processing

## Extension Ideas

Once you have a working basic implementation:
- **API specification analytics** - analyze unused operations across APIs
- **Automatic operation clustering** - group related operations intelligently
- **Version comparison** - track what changes between API versions
- **Documentation generation** - create focused docs from minified specs
- **Integration testing** - verify minified specs work with real APIs
- **Schema optimization** - simplify complex schemas while preserving semantics

## Getting Help

### Quick Testing
```bash
# Validate your parser
python -c "from minifier.parser import OpenAPIParser; parser = OpenAPIParser(); spec = parser.load('examples/simple-spec.yaml'); print('✅ Parser works')"

# Test basic minification
python minify.py examples/simple-spec.yaml --operations "getUser" --output test-output.yaml
```

### Support Resources
- **OpenAPI Specification**: [spec.openapis.org](https://spec.openapis.org/oas/v3.0.3)
- **JSON Schema**: Understanding schema dependencies
- **Discord Support**: #summer-hackathon for real-time help

Remember: **Start with simple specs and single operations**, then work up to complex scenarios. The goal is to make massive API specs manageable for AI agents and developers!