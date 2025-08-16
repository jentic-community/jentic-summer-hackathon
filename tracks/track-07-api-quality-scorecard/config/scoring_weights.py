"""Scoring weights and quality thresholds configuration."""

from pydantic import BaseModel, Field, validator
from typing import Dict


class ScoringWeights(BaseModel):
    """Configurable weights for scoring categories."""
    
    documentation: float = Field(0.25, ge=0.0, le=1.0)
    schemas: float = Field(0.25, ge=0.0, le=1.0)
    errors: float = Field(0.20, ge=0.0, le=1.0)
    usability: float = Field(0.20, ge=0.0, le=1.0)
    authentication: float = Field(0.10, ge=0.0, le=1.0)
    
    @validator('authentication')
    def validate_weights_sum(cls, v, values):
        """Ensure all weights sum to 1.0."""
        total = sum(values.values()) + v
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for easy access."""
        return {
            "documentation": self.documentation,
            "schemas": self.schemas,
            "errors": self.errors,
            "usability": self.usability,
            "authentication": self.authentication
        }


class QualityThresholds(BaseModel):
    """Quality assessment thresholds."""
    
    min_description_length: int = Field(10, ge=1)
    good_description_length: int = Field(50, ge=10)
    excellent_description_length: int = Field(100, ge=50)
    
    max_parameters_per_operation: int = Field(10, ge=1)
    max_nested_schema_depth: int = Field(5, ge=1)
    
    min_error_status_codes: int = Field(3, ge=1)
    required_error_codes: list = Field(default_factory=lambda: ["400", "401", "404", "500"])
    
    min_coverage_excellent: float = Field(0.95, ge=0.0, le=1.0)
    min_coverage_good: float = Field(0.80, ge=0.0, le=1.0)
    min_coverage_acceptable: float = Field(0.60, ge=0.0, le=1.0)
    
    score_excellent: int = Field(90, ge=0, le=100)
    score_good: int = Field(80, ge=0, le=100)
    score_acceptable: int = Field(70, ge=0, le=100)
    score_needs_improvement: int = Field(60, ge=0, le=100)
    
    @validator('good_description_length')
    def validate_description_lengths(cls, v, values):
        """Ensure description length thresholds are in order."""
        if 'min_description_length' in values and v <= values['min_description_length']:
            raise ValueError("good_description_length must be greater than min_description_length")
        return v
    
    @validator('excellent_description_length')
    def validate_excellent_length(cls, v, values):
        """Ensure excellent length is greater than good length."""
        if 'good_description_length' in values and v <= values['good_description_length']:
            raise ValueError("excellent_description_length must be greater than good_description_length")
        return v
    
    def get_quality_grade(self, score: int) -> str:
        """Get quality grade based on score.
        
        Parameters
        ----------
        score : int
            The quality score to evaluate.
            
        Returns
        -------
        str
            Quality grade (A, B, C, D, or F).
        """
        if score >= self.score_excellent:
            return "A"
        elif score >= self.score_good:
            return "B"
        elif score >= self.score_acceptable:
            return "C"
        elif score >= self.score_needs_improvement:
            return "D"
        else:
            return "F"
    
    def get_quality_label(self, score: int) -> str:
        """Get descriptive quality label based on score.
        
        Parameters
        ----------
        score : int
            The quality score to evaluate.
            
        Returns
        -------
        str
            Quality label description.
        """
        if score >= self.score_excellent:
            return "Excellent"
        elif score >= self.score_good:
            return "Good"
        elif score >= self.score_acceptable:
            return "Acceptable"
        elif score >= self.score_needs_improvement:
            return "Needs Improvement"
        else:
            return "Poor"


class CategoryWeights(BaseModel):
    """Detailed weights for subcategories within each main category."""
    
    documentation_operation_descriptions: float = Field(0.32, ge=0.0, le=1.0)
    documentation_parameter_descriptions: float = Field(0.28, ge=0.0, le=1.0)
    documentation_examples: float = Field(0.20, ge=0.0, le=1.0)
    documentation_summary_quality: float = Field(0.20, ge=0.0, le=1.0)
    
    schemas_request_schemas: float = Field(0.32, ge=0.0, le=1.0)
    schemas_response_schemas: float = Field(0.32, ge=0.0, le=1.0)
    schemas_parameter_types: float = Field(0.20, ge=0.0, le=1.0)
    schemas_required_fields: float = Field(0.16, ge=0.0, le=1.0)
    
    errors_error_responses: float = Field(0.40, ge=0.0, le=1.0)
    errors_error_schemas: float = Field(0.30, ge=0.0, le=1.0)
    errors_status_coverage: float = Field(0.20, ge=0.0, le=1.0)
    errors_examples: float = Field(0.10, ge=0.0, le=1.0)
    
    usability_operation_naming: float = Field(0.30, ge=0.0, le=1.0)
    usability_discoverability: float = Field(0.25, ge=0.0, le=1.0)
    usability_complexity: float = Field(0.25, ge=0.0, le=1.0)
    usability_consistency: float = Field(0.20, ge=0.0, le=1.0)
    
    auth_security_schemes: float = Field(0.40, ge=0.0, le=1.0)
    auth_examples: float = Field(0.30, ge=0.0, le=1.0)
    auth_scope_definitions: float = Field(0.20, ge=0.0, le=1.0)
    auth_flow_docs: float = Field(0.10, ge=0.0, le=1.0)