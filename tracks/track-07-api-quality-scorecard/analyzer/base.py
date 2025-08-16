"""Base classes for scoring modules."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel


class CategoryResult(BaseModel):
    """Result from analyzing a specific category."""
    
    category: ScoreCategory
    score: int
    max_score: int
    details: Dict[str, Any] = {}
    issues: List[str] = []
    recommendations: List[Recommendation] = []
    
    @property
    def percentage(self) -> float:
        """Calculate percentage score for this category."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100


class BaseScoringModule(ABC):
    """Abstract base class for all scoring modules."""
    
    def __init__(self, category: ScoreCategory, max_score: int):
        self.category = category
        self.max_score = max_score
    
    @abstractmethod
    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze specification for this category.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
            
        Returns
        -------
        CategoryResult
            Analysis result with score and recommendations.
        """
        pass
    
    @abstractmethod
    def get_recommendations(self, result: CategoryResult, spec: OpenAPISpec) -> List[Recommendation]:
        """Generate recommendations based on analysis result.
        
        Parameters
        ----------
        result : CategoryResult
            Analysis result from this module.
        spec : OpenAPISpec
            Original specification for context.
            
        Returns
        -------
        List[Recommendation]
            List of actionable recommendations.
        """
        pass
    
    def create_recommendation(
        self,
        title: str,
        description: str,
        severity: SeverityLevel,
        operation_id: str = None,
        parameter_name: str = None,
        suggested_fix: str = None,
        impact_score: int = 5
    ) -> Recommendation:
        """Create a recommendation with consistent formatting.
        
        Parameters
        ----------
        title : str
            Brief title for the recommendation.
        description : str
            Detailed description of the issue.
        severity : SeverityLevel
            Severity level of the issue.
        operation_id : str, optional
            Related operation ID if applicable.
        parameter_name : str, optional
            Related parameter name if applicable.
        suggested_fix : str, optional
            Suggested fix for the issue.
        impact_score : int, optional
            Impact score from 1-10, by default 5.
            
        Returns
        -------
        Recommendation
            Formatted recommendation object.
        """
        from core.types import RecommendationType
        
        rec_type_map = {
            "description": RecommendationType.MISSING_DESCRIPTION,
            "schema": RecommendationType.INCOMPLETE_SCHEMA,
            "error": RecommendationType.MISSING_ERROR_HANDLING,
            "naming": RecommendationType.POOR_NAMING,
            "example": RecommendationType.MISSING_EXAMPLES,
            "complex": RecommendationType.COMPLEX_OPERATION,
            "auth": RecommendationType.MISSING_AUTH_DOCS,
            "consistency": RecommendationType.INCONSISTENT_PATTERNS
        }
        
        rec_type = RecommendationType.MISSING_DESCRIPTION
        for keyword, rtype in rec_type_map.items():
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                rec_type = rtype
                break
        
        return Recommendation(
            type=rec_type,
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            operation_id=operation_id,
            parameter_name=parameter_name,
            suggested_fix=suggested_fix,
            impact_score=max(1, min(10, impact_score))
        )
    
    def calculate_coverage_score(self, covered: int, total: int, max_points: int) -> int:
        """Calculate score based on coverage percentage.
        
        Parameters
        ----------
        covered : int
            Number of items that meet the criteria.
        total : int
            Total number of items.
        max_points : int
            Maximum points for this criterion.
            
        Returns
        -------
        int
            Calculated score.
        """
        if total == 0:
            return max_points
        
        coverage = covered / total
        return int(coverage * max_points)
    
    def assess_text_quality(self, text: str, min_length: int = 10, good_length: int = 50) -> Dict[str, Any]:
        """Assess the quality of descriptive text.
        
        Parameters
        ----------
        text : str
            Text to assess.
        min_length : int, optional
            Minimum acceptable length, by default 10.
        good_length : int, optional
            Length considered good quality, by default 50.
            
        Returns
        -------
        Dict[str, Any]
            Assessment results including length, quality indicators.
        """
        if not text or not isinstance(text, str):
            return {
                "length": 0,
                "quality": "missing",
                "score": 0,
                "issues": ["No description provided"]
            }
        
        text = text.strip()
        length = len(text)
        issues = []
        
        if length < min_length:
            quality = "poor"
            score = 1
            issues.append(f"Description too short ({length} chars, min {min_length})")
        elif length < good_length:
            quality = "acceptable"
            score = 2
        else:
            quality = "good"
            score = 3
        
        if text.lower() == text:
            issues.append("Description should use proper capitalization")
        
        if not text.endswith('.'):
            issues.append("Description should end with proper punctuation")
        
        return {
            "length": length,
            "quality": quality,
            "score": score,
            "issues": issues
        }