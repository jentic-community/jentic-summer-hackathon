"""Core data models and types for API Quality Scorecard."""

from .models import (
    ScoringResult,
    CategoryScores,
    AnalysisMetrics,
    Recommendation,
    OpenAPISpec,
    OperationInfo,
    ParameterInfo,
    ResponseInfo,
    SchemaInfo
)
from .types import (
    ScoreCategory,
    RecommendationType,
    SeverityLevel,
    OutputFormat
)
from .exceptions import (
    ScorecardError,
    ParseError,
    ValidationError,
    AnalysisError
)

__all__ = [
    "ScoringResult",
    "CategoryScores", 
    "AnalysisMetrics",
    "Recommendation",
    "OpenAPISpec",
    "OperationInfo",
    "ParameterInfo",
    "ResponseInfo",
    "SchemaInfo",
    "ScoreCategory",
    "RecommendationType",
    "SeverityLevel",
    "OutputFormat",
    "ScorecardError",
    "ParseError",
    "ValidationError",
    "AnalysisError"
]