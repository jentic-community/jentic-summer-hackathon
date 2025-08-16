"""Documentation quality analysis module."""

from typing import List
from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel
from config.settings import get_settings
from analyzer.base import BaseScoringModule, CategoryResult


class DocumentationAnalyzer(BaseScoringModule):
    """Analyzer for documentation quality scoring (25 points total)."""
    
    def __init__(self):
        super().__init__(ScoreCategory.DOCUMENTATION, 25)
        self.settings = get_settings()
    
    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze documentation quality across operations and parameters.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
            
        Returns
        -------
        CategoryResult
            Analysis result with documentation quality score.
        """
        operation_desc_score = self._score_operation_descriptions(spec)
        parameter_desc_score = self._score_parameter_descriptions(spec)
        examples_score = self._score_examples(spec)
        summary_quality_score = self._score_summary_quality(spec)
        
        total_score = (
            operation_desc_score +
            parameter_desc_score +
            examples_score +
            summary_quality_score
        )
        
        details = {
            "operation_descriptions": operation_desc_score,
            "parameter_descriptions": parameter_desc_score,
            "examples": examples_score,
            "summary_quality": summary_quality_score,
            "operations_analyzed": len(spec.operations),
            "parameters_analyzed": spec.total_parameters
        }
        
        issues = self._identify_issues(spec)
        
        return CategoryResult(
            category=self.category,
            score=total_score,
            max_score=self.max_score,
            details=details,
            issues=issues
        )
    
    def _score_operation_descriptions(self, spec: OpenAPISpec) -> int:
        """Score operation description quality (8 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for operation descriptions.
        """
        if not spec.operations:
            return 8
        
        good_descriptions = 0
        for operation in spec.operations:
            desc_quality = self.assess_text_quality(
                operation.description,
                self.settings.min_description_length,
                self.settings.good_description_length
            )
            if desc_quality["score"] >= 2:
                good_descriptions += 1
        
        coverage = good_descriptions / len(spec.operations)
        
        if coverage >= 0.95:
            return 8
        elif coverage >= 0.80:
            return 6
        elif coverage >= 0.60:
            return 4
        elif coverage >= 0.40:
            return 2
        else:
            return 0
    
    def _score_parameter_descriptions(self, spec: OpenAPISpec) -> int:
        """Score parameter description quality (7 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for parameter descriptions.
        """
        total_params = spec.total_parameters
        if total_params == 0:
            return 7
        
        good_descriptions = 0
        for operation in spec.operations:
            for param in operation.parameters:
                desc_quality = self.assess_text_quality(
                    param.description,
                    self.settings.min_description_length,
                    self.settings.good_description_length
                )
                if desc_quality["score"] >= 2:
                    good_descriptions += 1
        
        coverage = good_descriptions / total_params
        
        if coverage >= 0.90:
            return 7
        elif coverage >= 0.75:
            return 5
        elif coverage >= 0.50:
            return 3
        elif coverage >= 0.25:
            return 1
        else:
            return 0
    
    def _score_examples(self, spec: OpenAPISpec) -> int:
        """Score example provision quality (5 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for examples.
        """
        if not spec.operations:
            return 5
        
        operations_with_examples = 0
        for operation in spec.operations:
            has_request_example = any(param.has_example for param in operation.parameters)
            has_response_example = any(resp.has_example for resp in operation.responses)
            
            if has_request_example and has_response_example:
                operations_with_examples += 1
            elif has_request_example or has_response_example:
                operations_with_examples += 0.5
        
        coverage = operations_with_examples / len(spec.operations)
        
        if coverage >= 0.75:
            return 5
        elif coverage >= 0.50:
            return 3
        elif coverage >= 0.25:
            return 1
        else:
            return 0
    
    def _score_summary_quality(self, spec: OpenAPISpec) -> int:
        """Score summary and tag quality (5 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for summary quality.
        """
        score = 0
        
        api_desc_quality = self.assess_text_quality(
            spec.description,
            20,
            100
        )
        if api_desc_quality["score"] >= 2:
            score += 2
        
        operations_with_summaries = sum(
            1 for op in spec.operations 
            if op.summary and len(op.summary.strip()) >= 10
        )
        
        if spec.operations:
            summary_coverage = operations_with_summaries / len(spec.operations)
            if summary_coverage >= 0.80:
                score += 2
            elif summary_coverage >= 0.50:
                score += 1
        
        if len(spec.tags) > 0:
            score += 1
        
        return min(score, 5)
    
    def _identify_issues(self, spec: OpenAPISpec) -> List[str]:
        """Identify specific documentation issues.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        List[str]
            List of identified issues.
        """
        issues = []
        
        operations_without_desc = [
            op.operation_id or f"{op.method.value.upper()} {op.path}"
            for op in spec.operations
            if not op.description or len(op.description.strip()) < self.settings.min_description_length
        ]
        
        if operations_without_desc:
            issues.append(f"{len(operations_without_desc)} operations lack adequate descriptions")
        
        params_without_desc = sum(
            1 for op in spec.operations
            for param in op.parameters
            if not param.description or len(param.description.strip()) < self.settings.min_description_length
        )
        
        if params_without_desc > 0:
            issues.append(f"{params_without_desc} parameters lack descriptions")
        
        operations_without_examples = sum(
            1 for op in spec.operations
            if not any(resp.has_example for resp in op.responses)
        )
        
        if operations_without_examples > 0:
            issues.append(f"{operations_without_examples} operations lack response examples")
        
        if not spec.description:
            issues.append("API lacks overall description")
        
        return issues
    
    def get_recommendations(self, result: CategoryResult, spec: OpenAPISpec) -> List[Recommendation]:
        """Generate recommendations for improving documentation quality.
        
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
        recommendations = []
        
        for operation in spec.operations:
            op_id = operation.operation_id or f"{operation.method.value.upper()} {operation.path}"
            
            if not operation.description or len(operation.description.strip()) < self.settings.min_description_length:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add description to {op_id}",
                        description=f"Operation {op_id} lacks a proper description. Add a clear description explaining what this operation does.",
                        severity=SeverityLevel.MEDIUM,
                        operation_id=operation.operation_id,
                        suggested_fix=f"Add a description field with at least {self.settings.min_description_length} characters explaining the operation's purpose.",
                        impact_score=6
                    )
                )
            
            for param in operation.parameters:
                if not param.description or len(param.description.strip()) < self.settings.min_description_length:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Add description to parameter '{param.name}'",
                            description=f"Parameter '{param.name}' in {op_id} lacks a description. This makes it difficult for agents to understand how to use this parameter.",
                            severity=SeverityLevel.LOW,
                            operation_id=operation.operation_id,
                            parameter_name=param.name,
                            suggested_fix="Add a description explaining what this parameter is for and what values are expected.",
                            impact_score=4
                        )
                    )
            
            if not any(resp.has_example for resp in operation.responses):
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add response examples to {op_id}",
                        description=f"Operation {op_id} lacks response examples. Examples help agents understand the expected response format.",
                        severity=SeverityLevel.LOW,
                        operation_id=operation.operation_id,
                        suggested_fix="Add example responses for at least the successful response codes.",
                        impact_score=5
                    )
                )
        
        if not spec.description:
            recommendations.append(
                self.create_recommendation(
                    title="Add API description",
                    description="The API lacks an overall description. This makes it difficult to understand the API's purpose and scope.",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix="Add a comprehensive description in the info.description field explaining what the API does and its main use cases.",
                    impact_score=7
                )
            )
        
        return recommendations