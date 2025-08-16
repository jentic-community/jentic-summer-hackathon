# Test Examples for OpenAPI Validator

This document provides examples of valid and invalid OpenAPI specifications for testing your validator. Create these files in your `test-specs/` directory.

## Valid Specifications

### test-specs/valid/minimal-valid.yaml
```yaml
openapi: 3.0.0
info:
  title: Minimal Valid API
  version: 1.0.0
paths: {}
```

### test-specs/valid/complete-example.yaml
```yaml
openapi: 3.0.0
info:
  title: Complete Example API
  description: A well-documented API for testing
  version: 1.2.3
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      description: Retrieve a paginated list of users with optional filtering
      tags:
        - Users
      parameters:
        - name: limit
          in: query
          description: Maximum number of users to return
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: List of users retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer
              example:
                users:
                  - id: 1
                    name: "John Doe"
                    email: "john@example.com"
                total: 150
        '400':
          description: Invalid request parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    post:
      operationId: createUser
      summary: Create a new user
      description: Create a new user account with provided information
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            example:
              name: "Jane Smith"
              email: "jane@example.com"
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid user data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - name
        - email
      properties:
        id:
          type: integer
          description: Unique user identifier
        name:
          type: string
          description: Full name of the user
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
          description: User's email address
    
    CreateUserRequest:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
    
    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: string
          description: Error code
        message:
          type: string
          description: Human-readable error message

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []

tags:
  - name: Users
    description: User management operations
```

## Invalid Specifications

### test-specs/invalid/missing-openapi-version.yaml
```yaml
# Missing openapi field - should cause error
info:
  title: Invalid API
  version: 1.0.0
paths: {}
```

### test-specs/invalid/missing-info-version.yaml
```yaml
openapi: 3.0.0
info:
  title: Invalid API
  # Missing version field - should cause error
paths: {}
```

### test-specs/invalid/old-openapi-version.yaml
```yaml
openapi: 2.0  # Unsupported version - should cause error
info:
  title: Old API
  version: 1.0.0
paths: {}
```

### test-specs/invalid/invalid-reference.yaml
```yaml
openapi: 3.0.0
info:
  title: Invalid Reference API
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NonExistentSchema'  # Invalid reference
components:
  schemas: {}
```

### test-specs/invalid/malformed-json.json
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Malformed API",
    "version": "1.0.0"
  },
  "paths": {
    // This comment makes it invalid JSON
  }
}
```

## Semantic Issues (Valid syntax, questionable semantics)

### test-specs/edge-cases/get-with-body.yaml
```yaml
openapi: 3.0.0
info:
  title: Questionable Design API
  version: 1.0.0
paths:
  /search:
    get:
      summary: Search with body
      requestBody:  # Questionable: GET with request body
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Search results
```

### test-specs/edge-cases/post-without-body.yaml
```yaml
openapi: 3.0.0
info:
  title: Questionable Design API
  version: 1.0.0
paths:
  /users:
    post:
      summary: Create user without body
      # Missing requestBody for POST - questionable
      responses:
        '201':
          description: User created
```

### test-specs/edge-cases/missing-error-responses.yaml
```yaml
openapi: 3.0.0
info:
  title: Incomplete Error Handling API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
        # Missing 4xx and 5xx responses - incomplete
```

## Agent-Ready Issues

### test-specs/edge-cases/poor-documentation.yaml
```yaml
openapi: 3.0.0
info:
  title: Poorly Documented API
  version: 1.0.0
paths:
  /data:
    get:
      summary: Get data  # Too vague
      # Missing operationId
      # Missing detailed description
      responses:
        '200':
          description: OK  # Too vague
          content:
            application/json:
              schema:
                type: object  # No properties defined
```

### test-specs/edge-cases/missing-examples.yaml
```yaml
openapi: 3.0.0
info:
  title: No Examples API
  version: 1.0.0
paths:
  /users:
    post:
      operationId: createUser
      summary: Create user
      description: Creates a new user account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
              # Missing examples
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                type: object
                # Missing examples
```

## Real-World Test Cases

### test-specs/real-world/github-subset.yaml
```yaml
# Simplified version of GitHub API for testing
openapi: 3.0.0
info:
  title: GitHub API (Subset)
  version: 1.0.0
  description: Simplified GitHub API for testing

servers:
  - url: https://api.github.com

paths:
  /user:
    get:
      operationId: getAuthenticatedUser
      summary: Get the authenticated user
      responses:
        '200':
          description: Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  /repos/{owner}/{repo}:
    get:
      operationId: getRepo
      summary: Get a repository
      parameters:
        - name: owner
          in: path
          required: true
          schema:
            type: string
        - name: repo
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Repository'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        login:
          type: string
        name:
          type: string
    
    Repository:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        full_name:
          type: string
        private:
          type: boolean

  securitySchemes:
    BearerToken:
      type: http
      scheme: bearer

security:
  - BearerToken: []
```

## Test File Organization

```
test-specs/
├── valid/
│   ├── minimal-valid.yaml
│   ├── complete-example.yaml
│   └── real-world-subset.yaml
├── invalid/
│   ├── missing-openapi-version.yaml
│   ├── missing-info-version.yaml
│   ├── old-openapi-version.yaml
│   ├── invalid-reference.yaml
│   └── malformed-json.json
├── edge-cases/
│   ├── get-with-body.yaml
│   ├── post-without-body.yaml
│   ├── missing-error-responses.yaml
│   ├── poor-documentation.yaml
│   └── missing-examples.yaml
└── real-world/
    ├── github-subset.yaml
    ├── stripe-subset.yaml
    └── petstore-official.yaml
```

## Expected Validation Results

### For Valid Specs
- **minimal-valid.yaml**: No errors, might have warnings about missing documentation
- **complete-example.yaml**: Should pass all validation levels

### For Invalid Specs
- **missing-openapi-version.yaml**: Syntax error - missing required field
- **invalid-reference.yaml**: Syntax error - unresolved reference
- **malformed-json.json**: Syntax error - invalid JSON

### For Edge Cases
- **get-with-body.yaml**: Semantic warning about GET with request body
- **poor-documentation.yaml**: Agent-ready warnings about insufficient documentation
- **missing-examples.yaml**: Agent-ready info suggestions about adding examples

Use these test cases to verify your validator correctly identifies issues at each validation level!