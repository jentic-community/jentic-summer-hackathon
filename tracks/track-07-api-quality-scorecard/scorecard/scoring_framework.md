# Scoring Framework for API Quality Scorecard

This document defines the detailed scoring criteria for evaluating OpenAPI specifications for agent-readiness.

## Overview

The scorecard evaluates APIs across 5 main dimensions with a total of 100 points:

| Category | Points | Description |
|----------|---------|-------------|
| Documentation Quality | 25 | Clarity and completeness of descriptions |
| Schema Completeness | 25 | Request/response schema definitions |
| Error Handling | 20 | Error response documentation |
| Agent Usability | 20 | Naming, discoverability, complexity |
| Authentication Clarity | 10 | Auth documentation and examples |

## Detailed Scoring Criteria

### 1. Documentation Quality (25 points)

#### Operation Descriptions (8 points)
- **4 points**: All operations have clear, detailed descriptions (>50 chars)
- **3 points**: Most operations (80%+) have good descriptions
- **2 points**: Some operations (60%+) have descriptions
- **1 point**: Few operations (40%+) have descriptions
- **0 points**: Most operations lack descriptions

#### Parameter Descriptions (7 points)
- **4 points**: All parameters have clear descriptions
- **3 points**: 90%+ parameters have descriptions
- **2 points**: 75%+ parameters have descriptions
- **1 point**: 50%+ parameters have descriptions
- **0 points**: Most parameters lack descriptions

#### Examples Provided (5 points)
- **3 points**: Request and response examples for all operations
- **2 points**: Examples for most operations (75%+)
- **1 point**: Examples for some operations (50%+)
- **0 points**: Few or no examples provided

#### Summary and Tag Quality (5 points)
- **3 points**: Clear summaries and well-organized tags
- **2 points**: Good summaries, decent tag organization
- **1 point**: Basic summaries or tags present
- **0 points**: Poor or missing summaries/tags

### 2. Schema Completeness (25 points)

#### Request Body Schemas (8 points)
- **4 points**: All request bodies have complete, typed schemas
- **3 points**: Most request bodies (90%+) have good schemas
- **2 points**: Some request bodies (75%+) have schemas
- **1 point**: Few request bodies (50%+) have schemas
- **0 points**: Most request bodies lack proper schemas

#### Response Schemas (8 points)
- **4 points**: All responses (including errors) have schemas
- **3 points**: Most responses (90%+) have schemas
- **2 points**: Success responses have schemas, some errors
- **1 point**: Only main success responses have schemas
- **0 points**: Few or no response schemas

#### Parameter Type Definitions (5 points)
- **3 points**: All parameters have proper types and constraints
- **2 points**: Most parameters (85%+) properly typed
- **1 point**: Some parameters (70%+) properly typed
- **0 points**: Many parameters lack proper typing

#### Required Fields Specification (4 points)
- **2 points**: Required fields clearly marked in all schemas
- **1 point**: Required fields marked in most schemas
- **0 points**: Required fields poorly specified

### 3. Error Handling (20 points)

#### Error Response Documentation (8 points)
- **4 points**: All operations document 4xx and 5xx responses
- **3 points**: Most operations document common errors
- **2 points**: Some operations document errors
- **1 point**: Few operations document errors
- **0 points**: Poor error response documentation

#### Error Response Schemas (6 points)
- **3 points**: All error responses have structured schemas
- **2 points**: Most error responses have schemas
- **1 point**: Some error responses have schemas
- **0 points**: Error responses lack schemas

#### Status Code Coverage (4 points)
- **2 points**: Comprehensive status codes (400, 401, 403, 404, 500, etc.)
- **1 point**: Basic status codes covered
- **0 points**: Minimal status code coverage

#### Error Examples (2 points)
- **1 point**: Error response examples provided
- **0 points**: No error examples

### 4. Agent Usability (20 points)

#### Operation Naming (6 points)
- **3 points**: Clear, consistent operationId naming convention
- **2 points**: Good operationId naming with minor issues
- **1 point**: Basic operationId naming
- **0 points**: Poor or missing operationId naming

#### API Organization and Discoverability (5 points)
- **3 points**: Excellent tag organization, clear grouping
- **2 points**: Good organization with logical grouping
- **1 point**: Basic organization present
- **0 points**: Poor organization, hard to navigate

#### Operation Complexity (5 points)
- **3 points**: Operations have reasonable complexity (≤10 parameters)
- **2 points**: Most operations reasonably complex
- **1 point**: Some complex operations present
- **0 points**: Many overly complex operations

#### Naming Consistency (4 points)
- **2 points**: Consistent parameter and schema naming
- **1 point**: Mostly consistent naming
- **0 points**: Inconsistent naming patterns

### 5. Authentication Clarity (10 points)

#### Security Scheme Documentation (4 points)
- **2 points**: Complete security schemes with descriptions
- **1 point**: Basic security schemes documented
- **0 points**: Poor or missing security documentation

#### Authentication Examples (3 points)
- **2 points**: Clear authentication examples and flows
- **1 point**: Basic authentication guidance
- **0 points**: No authentication examples

#### OAuth Scope Definitions (2 points)
- **1 point**: Well-defined OAuth scopes (if applicable)
- **0 points**: Poor or missing scope definitions

#### Auth Flow Documentation (1 point)
- **1 point**: Clear authentication flow documentation
- **0 points**: Unclear authentication process

## Scoring Implementation Guidelines

### Calculation Methods

1. **Count-based scoring**: For criteria based on coverage percentages
   ```python
   score = (covered_items / total_items) * max_points
   ```

2. **Quality-based scoring**: For subjective criteria
   ```python
   # Use heuristics like:
   # - Description length (min 10, good 50+ characters)
   # - Keyword presence (action words, clear language)
   # - Example completeness
   ```

3. **Threshold-based scoring**: For binary criteria
   ```python
   score = max_points if meets_threshold else 0
   ```

### Common Evaluation Patterns

#### Text Quality Assessment
- **Length**: Minimum character thresholds
- **Clarity**: Presence of action words, clear language
- **Completeness**: Coverage of key information

#### Schema Quality Assessment
- **Type Coverage**: All fields have appropriate types
- **Constraint Definition**: Min/max, format, pattern constraints
- **Example Provision**: Realistic example values

#### Coverage Assessment
- **Operation Coverage**: Percentage of operations meeting criteria
- **Parameter Coverage**: Percentage of parameters documented
- **Response Coverage**: Percentage of responses with schemas

## Implementation Tips

### Data Collection
```python
def collect_metrics(spec):
    return {
        'total_operations': count_operations(spec),
        'operations_with_descriptions': count_described_operations(spec),
        'total_parameters': count_parameters(spec),
        'parameters_with_descriptions': count_described_parameters(spec),
        # ... more metrics
    }
```

### Score Calculation
```python
def calculate_category_score(metrics, category_weights):
    total_score = 0
    for criterion, weight in category_weights.items():
        criterion_score = evaluate_criterion(metrics, criterion)
        total_score += criterion_score * weight
    return total_score
```

### Quality Thresholds
- **Excellent**: 90-100 points
- **Good**: 80-89 points  
- **Acceptable**: 70-79 points
- **Needs Improvement**: 60-69 points
- **Poor**: Below 60 points

## Customization Options

The scoring framework should be configurable:

```python
SCORING_WEIGHTS = {
    'documentation': 0.25,
    'schemas': 0.25,
    'errors': 0.20,
    'usability': 0.20,
    'auth': 0.10
}

QUALITY_THRESHOLDS = {
    'min_description_length': 10,
    'good_description_length': 50,
    'max_parameters_per_operation': 10,
    'min_error_status_codes': 3
}
```

This allows users to adjust scoring based on their specific needs and use cases.