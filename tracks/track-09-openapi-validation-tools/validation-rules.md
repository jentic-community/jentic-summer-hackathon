# Validation Rules Reference

This document outlines the validation rules you should implement for each validation level. Use this as a guide for building your validator.

## Syntax Validation Rules

### Required Fields
- [ ] **OpenAPI version field** - Must be present and start with "3."
- [ ] **Info object** - Must contain title and version
- [ ] **Paths object** - Must be present (can be empty)

### Structure Validation
- [ ] **Valid JSON/YAML** - Document must parse correctly
- [ ] **JSON Schema compliance** - Must conform to OpenAPI 3.0+ schema
- [ ] **Reference resolution** - All $ref pointers must resolve
- [ ] **No circular references** - Detect and report circular $ref chains

### Data Type Validation
- [ ] **Field types** - All fields must have correct types (string, object, array, etc.)
- [ ] **Enum values** - Enumerated values must be from allowed sets
- [ ] **Format validation** - email, uri, date-time formats must be valid

## Semantic Validation Rules

### HTTP Method Appropriateness
- [ ] **GET methods** - Should not have request bodies
- [ ] **DELETE methods** - Should not have request bodies
- [ ] **POST methods** - Should have request body for creation operations
- [ ] **PUT/PATCH methods** - Should have request body for updates

### Status Code Validation
- [ ] **Success responses** - 2xx status codes should be documented
- [ ] **Client errors** - 4xx status codes for invalid requests
- [ ] **Server errors** - 5xx status codes for server failures
- [ ] **Method-appropriate codes** - POST should have 201, DELETE should have 204

### Parameter Validation
- [ ] **Required parameters** - Properly marked as required
- [ ] **Path parameters** - All path parameters must be defined
- [ ] **Parameter types** - Types should match usage patterns
- [ ] **No duplicate parameters** - Same parameter not defined multiple times

### Schema Consistency
- [ ] **Referenced schemas exist** - All schema references resolve
- [ ] **Type consistency** - Fields with same name have consistent types
- [ ] **Required field validation** - Required fields are actually defined
- [ ] **Reasonable constraints** - min/max values make sense

## Agent-Ready Validation Rules

### Operation Documentation
- [ ] **Operation IDs** - All operations should have unique operationId
- [ ] **Clear descriptions** - Operations have detailed, helpful descriptions
- [ ] **Parameter descriptions** - All parameters have clear descriptions
- [ ] **Summary quality** - Summaries are concise but informative

### Schema Completeness
- [ ] **Request body schemas** - Complete schemas for request bodies
- [ ] **Response schemas** - Schemas for all response types
- [ ] **Example values** - Realistic examples provided
- [ ] **Property descriptions** - Schema properties have descriptions

### Error Handling
- [ ] **Error responses** - Common error scenarios documented
- [ ] **Error schemas** - Error responses have structured schemas
- [ ] **Status code coverage** - Comprehensive status code documentation
- [ ] **Error examples** - Examples of error responses

### Naming Conventions
- [ ] **Consistent naming** - Parameters use consistent naming patterns
- [ ] **Clear operation IDs** - operationId follows naming conventions
- [ ] **Logical grouping** - Related operations are properly tagged
- [ ] **Path structure** - URL paths follow RESTful conventions

## Implementation Guidelines

### Rule Severity Levels

**Error (Breaks functionality)**:
```python
{
    'type': 'missing_required_field',
    'severity': 'error',
    'message': 'Missing required field: openapi',
    'location': 'root',
    'fix_suggestion': 'Add openapi: "3.0.0" to the root level'
}
```

**Warning (Problematic but valid)**:
```python
{
    'type': 'questionable_design', 
    'severity': 'warning',
    'message': 'GET operation should not have request body',
    'location': 'paths./users.get',
    'fix_suggestion': 'Remove requestBody or change to POST method'
}
```

**Info (Suggestions for improvement)**:
```python
{
    'type': 'improvement_suggestion',
    'severity': 'info', 
    'message': 'Consider adding examples for better documentation',
    'location': 'paths./users.get.responses.200',
    'fix_suggestion': 'Add example response data'
}
```

### Validation Rule Structure

Each validation rule should follow this pattern:

```python
def validate_rule_name(spec: dict, context: dict = None) -> List[ValidationResult]:
    """
    Validate specific rule against OpenAPI specification.
    
    Args:
        spec: The OpenAPI specification dictionary
        context: Additional context for validation
        
    Returns:
        List of validation results (errors, warnings, info)
    """
    results = []
    
    # TODO: Implement validation logic
    # 1. Check condition
    # 2. If violation found, create result
    # 3. Add location and fix suggestion
    
    return results
```

### Location Path Format

Use JSON path notation for precise error locations:

- `root` - Root level
- `info.title` - Info object title field
- `paths./users.get` - GET operation on /users path  
- `paths./users.get.parameters[0]` - First parameter of GET /users
- `components.schemas.User.properties.name` - Name property of User schema

### Fix Suggestions

Provide actionable fix suggestions:

**Good suggestions**:
- "Add openapi: '3.0.0' to the root level"
- "Change HTTP method from GET to POST for operations with request bodies"
- "Add description field with at least 10 characters"

**Poor suggestions**:
- "Fix this error"
- "Invalid specification"
- "Check the documentation"

## Rule Categories by Validation Level

### Level 1: Syntax Only
- Required fields validation
- JSON Schema compliance
- Reference resolution
- Basic structure validation

### Level 2: Syntax + Semantics  
- All Level 1 rules
- HTTP method appropriateness
- Status code validation
- Parameter consistency
- Schema relationship validation

### Level 3: Agent-Ready (All rules)
- All Level 1 & 2 rules  
- Operation documentation completeness
- Schema description requirements
- Example value validation
- Naming convention compliance

## Custom Rule Configuration

Support configuration files for custom rules:

```yaml
# validation-config.yaml
rules:
  syntax:
    required_fields: error
    reference_resolution: error
    
  semantic:
    get_with_body: warning
    missing_error_responses: warning
    
  agent_ready:
    missing_operation_id: warning
    insufficient_description: error
    missing_examples: info

# Rule-specific settings
settings:
  min_description_length: 20
  required_status_codes: [200, 400, 500]
  naming_convention: camelCase
```

## Testing Your Rules

### Test Case Structure

For each rule, create test cases:

```python
def test_rule_name():
    # Valid case - should pass
    valid_spec = {...}
    results = validate_rule_name(valid_spec)
    assert len(results) == 0
    
    # Invalid case - should fail
    invalid_spec = {...}
    results = validate_rule_name(invalid_spec)
    assert len(results) == 1
    assert results[0]['severity'] == 'error'
```

### Edge Cases to Test

- Empty specifications
- Minimal valid specifications  
- Complex nested structures
- Large specifications with many operations
- Specifications with external references
- Malformed JSON/YAML

## Performance Considerations

### Optimization Strategies
- **Early exit** - Stop validation on critical errors
- **Caching** - Cache parsed schemas and references
- **Lazy evaluation** - Only validate needed parts
- **Progress reporting** - Show progress for large specs

### Memory Management
- **Streaming** - Process large files in chunks
- **Reference cleanup** - Clear resolved references after use
- **Result batching** - Don't store all results in memory

Remember: Start with basic rules and build complexity gradually. Focus on the most common and impactful validation issues first!