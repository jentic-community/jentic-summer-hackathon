"""Pydantic models for API Quality Scorecard data structures."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from .types import (
    ScoreCategory, 
    RecommendationType, 
    SeverityLevel, 
    HTTPMethod,
    OpenAPIVersion
)


class ParameterInfo(BaseModel):
    """Information about an API parameter."""
    
    name: str
    location: str = Field(..., description="Parameter location: query, path, header, cookie")
    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = False
    has_example: bool = False
    has_constraints: bool = False


class ResponseInfo(BaseModel):
    """Information about an API response."""
    
    status_code: str
    description: Optional[str] = None
    has_schema: bool = False
    has_example: bool = False
    content_types: List[str] = Field(default_factory=list)


class SchemaInfo(BaseModel):
    """Information about a schema definition."""
    
    name: str
    type: Optional[str] = None
    properties_count: int = 0
    required_fields: List[str] = Field(default_factory=list)
    has_description: bool = False
    has_examples: bool = False
    nested_depth: int = 0


class OperationInfo(BaseModel):
    """Information about an API operation."""
    
    operation_id: Optional[str] = None
    method: HTTPMethod
    path: str
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    parameters: List[ParameterInfo] = Field(default_factory=list)
    responses: List[ResponseInfo] = Field(default_factory=list)
    has_request_body: bool = False
    request_body_schema: Optional[str] = None
    security_requirements: List[str] = Field(default_factory=list)
    
    @property
    def parameter_count(self) -> int:
        """Total number of parameters for this operation."""
        return len(self.parameters)
    
    @property
    def has_error_responses(self) -> bool:
        """Check if operation documents error responses."""
        return any(resp.status_code.startswith(('4', '5')) for resp in self.responses)


class OpenAPISpec(BaseModel):
    """Parsed OpenAPI specification data."""
    
    version: OpenAPIVersion
    title: str
    description: Optional[str] = None
    version_info: str = "1.0.0"
    operations: List[OperationInfo] = Field(default_factory=list)
    schemas: List[SchemaInfo] = Field(default_factory=list)
    security_schemes: Dict[str, Any] = Field(default_factory=dict)
    servers: List[Dict[str, str]] = Field(default_factory=list)
    tags: List[Dict[str, str]] = Field(default_factory=list)
    
    @property
    def total_operations(self) -> int:
        """Total number of operations in the API."""
        return len(self.operations)
    
    @property
    def total_parameters(self) -> int:
        """Total number of parameters across all operations."""
        return sum(op.parameter_count for op in self.operations)


class CategoryScores(BaseModel):
    """Scores for each quality category."""
    
    documentation: int = Field(ge=0, le=25, description="Documentation quality score")
    schemas: int = Field(ge=0, le=25, description="Schema completeness score")
    errors: int = Field(ge=0, le=20, description="Error handling score")
    usability: int = Field(ge=0, le=20, description="Agent usability score")
    authentication: int = Field(ge=0, le=10, description="Authentication clarity score")
    
    @property
    def total(self) -> int:
        """Calculate total score across all categories."""
        return (
            self.documentation + 
            self.schemas + 
            self.errors + 
            self.usability + 
            self.authentication
        )


class Recommendation(BaseModel):
    """A recommendation for API improvement."""
    
    type: RecommendationType
    category: ScoreCategory
    severity: SeverityLevel
    title: str
    description: str
    operation_id: Optional[str] = None
    parameter_name: Optional[str] = None
    suggested_fix: Optional[str] = None
    impact_score: int = Field(ge=0, le=10, description="Potential impact of fixing this issue")


class AnalysisMetrics(BaseModel):
    """Detailed metrics from the analysis."""
    
    total_operations: int = 0
    operations_with_descriptions: int = 0
    total_parameters: int = 0
    parameters_with_descriptions: int = 0
    total_responses: int = 0
    responses_with_schemas: int = 0
    error_responses_documented: int = 0
    operations_with_examples: int = 0
    operations_with_operation_ids: int = 0
    security_schemes_count: int = 0
    
    @property
    def description_coverage_operations(self) -> float:
        """Percentage of operations with descriptions."""
        if self.total_operations == 0:
            return 0.0
        return (self.operations_with_descriptions / self.total_operations) * 100
    
    @property
    def description_coverage_parameters(self) -> float:
        """Percentage of parameters with descriptions."""
        if self.total_parameters == 0:
            return 0.0
        return (self.parameters_with_descriptions / self.total_parameters) * 100
    
    @property
    def schema_coverage_responses(self) -> float:
        """Percentage of responses with schemas."""
        if self.total_responses == 0:
            return 0.0
        return (self.responses_with_schemas / self.total_responses) * 100


class ScoringResult(BaseModel):
    """Complete scoring result for an API specification."""
    
    overall_score: int = Field(ge=0, le=100, description="Overall quality score")
    category_scores: CategoryScores
    metrics: AnalysisMetrics
    recommendations: List[Recommendation] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    spec_info: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('overall_score')
    def validate_overall_score(cls, v, values):
        """Ensure overall score matches category total."""
        if 'category_scores' in values:
            expected = values['category_scores'].total
            if v != expected:
                return expected
        return v
    
    @property
    def quality_grade(self) -> str:
        """Get quality grade based on overall score."""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"
    
    @property
    def critical_issues_count(self) -> int:
        """Count of critical severity recommendations."""
        return len([r for r in self.recommendations if r.severity == SeverityLevel.CRITICAL])
    
    @property
    def high_issues_count(self) -> int:
        """Count of high severity recommendations."""
        return len([r for r in self.recommendations if r.severity == SeverityLevel.HIGH])