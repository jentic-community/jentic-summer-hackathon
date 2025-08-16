"""Type definitions and enums for API Quality Scorecard."""

from enum import Enum
from typing import Literal


class ScoreCategory(str, Enum):
    """Categories for API quality scoring."""
    
    DOCUMENTATION = "documentation"
    SCHEMAS = "schemas"
    ERRORS = "errors"
    USABILITY = "usability"
    AUTHENTICATION = "authentication"


class RecommendationType(str, Enum):
    """Types of recommendations for API improvement."""
    
    MISSING_DESCRIPTION = "missing_description"
    INCOMPLETE_SCHEMA = "incomplete_schema"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    POOR_NAMING = "poor_naming"
    MISSING_EXAMPLES = "missing_examples"
    COMPLEX_OPERATION = "complex_operation"
    MISSING_AUTH_DOCS = "missing_auth_docs"
    INCONSISTENT_PATTERNS = "inconsistent_patterns"


class SeverityLevel(str, Enum):
    """Severity levels for issues and recommendations."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class OutputFormat(str, Enum):
    """Supported output formats for reports."""
    
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"


class HTTPMethod(str, Enum):
    """HTTP methods for API operations."""
    
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"
    TRACE = "trace"


class OpenAPIVersion(str, Enum):
    """Supported OpenAPI specification versions."""
    
    V3_0 = "3.0"
    V3_1 = "3.1"


ScoreCategoryType = Literal[
    "documentation",
    "schemas", 
    "errors",
    "usability",
    "authentication"
]

OutputFormatType = Literal["html", "json", "markdown"]