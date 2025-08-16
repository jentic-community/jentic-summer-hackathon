"""Main quality analyzer that orchestrates all scoring modules."""

from typing import List
from datetime import datetime

from core.models import OpenAPISpec, ScoringResult, CategoryScores, AnalysisMetrics
from core.types import ScoreCategory
from core.exceptions import AnalysisError
from config.settings import get_settings
from analyzer.base import BaseScoringModule
from analyzer.documentation import DocumentationAnalyzer
from analyzer.schemas import SchemaAnalyzer
from analyzer.errors import ErrorAnalyzer
from analyzer.usability import UsabilityAnalyzer
from analyzer.authentication import AuthenticationAnalyzer


class QualityAnalyzer:
    """Main analyzer that coordinates all scoring modules and generates final results."""
    
    def __init__(self):
        self.settings = get_settings()
        self.analyzers: List[BaseScoringModule] = [
            DocumentationAnalyzer(),
            SchemaAnalyzer(),
            ErrorAnalyzer(),
            UsabilityAnalyzer(),
            AuthenticationAnalyzer()
        ]
    
    def analyze(self, spec: OpenAPISpec, detailed: bool = False) -> ScoringResult:
        """Perform comprehensive quality analysis of OpenAPI specification.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
        detailed : bool, optional
            Whether to include detailed analysis, by default False.
            
        Returns
        -------
        ScoringResult
            Complete scoring result with all category scores and recommendations.
            
        Raises
        ------
        AnalysisError
            If analysis fails for any category.
        """
        try:
            category_results = {}
            all_recommendations = []
            
            for analyzer in self.analyzers:
                result = analyzer.analyze(spec)
                category_results[analyzer.category] = result
                
                recommendations = analyzer.get_recommendations(result, spec)
                all_recommendations.extend(recommendations)
            
            category_scores = CategoryScores(
                documentation=category_results[ScoreCategory.DOCUMENTATION].score,
                schemas=category_results[ScoreCategory.SCHEMAS].score,
                errors=category_results[ScoreCategory.ERRORS].score,
                usability=category_results[ScoreCategory.USABILITY].score,
                authentication=category_results[ScoreCategory.AUTHENTICATION].score
            )
            
            metrics = self._calculate_metrics(spec, category_results)
            
            scoring_result = ScoringResult(
                overall_score=category_scores.total,
                category_scores=category_scores,
                metrics=metrics,
                recommendations=all_recommendations,
                analysis_timestamp=datetime.now(),
                spec_info={
                    "title": spec.title,
                    "version": spec.version_info,
                    "openapi_version": spec.version.value,
                    "total_operations": spec.total_operations,
                    "total_schemas": len(spec.schemas)
                }
            )
            
            if detailed:
                scoring_result.spec_info.update({
                    "category_details": {
                        cat.value: {
                            "score": result.score,
                            "max_score": result.max_score,
                            "percentage": result.percentage,
                            "details": result.details,
                            "issues": result.issues
                        }
                        for cat, result in category_results.items()
                    }
                })
            
            return scoring_result
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {e}")
    
    def _calculate_metrics(self, spec: OpenAPISpec, category_results: dict) -> AnalysisMetrics:
        """Calculate detailed analysis metrics.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Original specification.
        category_results : dict
            Results from all category analyzers.
            
        Returns
        -------
        AnalysisMetrics
            Calculated metrics for the analysis.
        """
        operations_with_descriptions = sum(
            1 for op in spec.operations 
            if op.description and len(op.description.strip()) >= self.settings.min_description_length
        )
        
        parameters_with_descriptions = sum(
            1 for op in spec.operations 
            for param in op.parameters 
            if param.description and len(param.description.strip()) >= self.settings.min_description_length
        )
        
        total_responses = sum(len(op.responses) for op in spec.operations)
        responses_with_schemas = sum(
            1 for op in spec.operations 
            for resp in op.responses 
            if resp.has_schema
        )
        
        error_responses_documented = sum(
            1 for op in spec.operations 
            for resp in op.responses 
            if resp.status_code.startswith(('4', '5'))
        )
        
        operations_with_examples = sum(
            1 for op in spec.operations 
            for resp in op.responses 
            if resp.has_example
        )
        
        operations_with_operation_ids = sum(
            1 for op in spec.operations 
            if op.operation_id
        )
        
        return AnalysisMetrics(
            total_operations=spec.total_operations,
            operations_with_descriptions=operations_with_descriptions,
            total_parameters=spec.total_parameters,
            parameters_with_descriptions=parameters_with_descriptions,
            total_responses=total_responses,
            responses_with_schemas=responses_with_schemas,
            error_responses_documented=error_responses_documented,
            operations_with_examples=operations_with_examples,
            operations_with_operation_ids=operations_with_operation_ids,
            security_schemes_count=len(spec.security_schemes)
        )
    
    def get_analyzer_by_category(self, category: ScoreCategory) -> BaseScoringModule:
        """Get analyzer instance for specific category.
        
        Parameters
        ----------
        category : ScoreCategory
            Category to get analyzer for.
            
        Returns
        -------
        BaseScoringModule
            Analyzer instance for the category.
            
        Raises
        ------
        AnalysisError
            If no analyzer found for category.
        """
        for analyzer in self.analyzers:
            if analyzer.category == category:
                return analyzer
        
        raise AnalysisError(f"No analyzer found for category: {category}")
    
    def analyze_category(self, spec: OpenAPISpec, category: ScoreCategory) -> dict:
        """Analyze single category and return detailed results.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
        category : ScoreCategory
            Category to analyze.
            
        Returns
        -------
        dict
            Detailed analysis results for the category.
            
        Raises
        ------
        AnalysisError
            If category analysis fails.
        """
        try:
            analyzer = self.get_analyzer_by_category(category)
            result = analyzer.analyze(spec)
            recommendations = analyzer.get_recommendations(result, spec)
            
            return {
                "category": category.value,
                "score": result.score,
                "max_score": result.max_score,
                "percentage": result.percentage,
                "details": result.details,
                "issues": result.issues,
                "recommendations": [rec.dict() for rec in recommendations]
            }
            
        except Exception as e:
            raise AnalysisError(f"Failed to analyze category {category}: {e}", category.value)