"""Error handling analysis module."""

from typing import List, Set
from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel
from config.settings import get_settings
from analyzer.base import BaseScoringModule, CategoryResult


class ErrorAnalyzer(BaseScoringModule):
    """Analyzer for error handling scoring (20 points total)."""
    
    def __init__(self):
        super().__init__(ScoreCategory.ERRORS, 20)
        self.settings = get_settings()
        self.common_error_codes = {'400', '401', '403', '404', '409', '422', '429', '500', '502', '503'}
        self.required_error_codes = {'400', '401', '404', '500'}
    
    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze error handling completeness across operations.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
            
        Returns
        -------
        CategoryResult
            Analysis result with error handling score.
        """
        error_responses_score = self._score_error_responses(spec)
        error_schemas_score = self._score_error_schemas(spec)
        status_coverage_score = self._score_status_coverage(spec)
        error_examples_score = self._score_error_examples(spec)
        
        total_score = (
            error_responses_score +
            error_schemas_score +
            status_coverage_score +
            error_examples_score
        )
        
        details = {
            "error_responses": error_responses_score,
            "error_schemas": error_schemas_score,
            "status_coverage": status_coverage_score,
            "error_examples": error_examples_score,
            "operations_with_errors": sum(1 for op in spec.operations if op.has_error_responses),
            "total_error_responses": sum(
                len([r for r in op.responses if r.status_code.startswith(('4', '5'))])
                for op in spec.operations
            )
        }
        
        issues = self._identify_issues(spec)
        
        return CategoryResult(
            category=self.category,
            score=total_score,
            max_score=self.max_score,
            details=details,
            issues=issues
        )
    
    def _score_error_responses(self, spec: OpenAPISpec) -> int:
        """Score error response documentation (8 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for error response documentation.
        """
        if not spec.operations:
            return 8
        
        operations_with_errors = sum(1 for op in spec.operations if op.has_error_responses)
        operations_with_comprehensive_errors = 0
        
        for operation in spec.operations:
            error_codes = {
                resp.status_code for resp in operation.responses
                if resp.status_code.startswith(('4', '5'))
            }
            
            has_client_error = any(code.startswith('4') for code in error_codes)
            has_server_error = any(code.startswith('5') for code in error_codes)
            has_required_codes = len(error_codes.intersection(self.required_error_codes)) >= 2
            
            if has_client_error and has_server_error and has_required_codes:
                operations_with_comprehensive_errors += 1
        
        if len(spec.operations) == 0:
            return 8
        
        basic_coverage = operations_with_errors / len(spec.operations)
        comprehensive_coverage = operations_with_comprehensive_errors / len(spec.operations)
        
        if comprehensive_coverage >= 0.80:
            return 8
        elif basic_coverage >= 0.80:
            return 6
        elif basic_coverage >= 0.60:
            return 4
        elif basic_coverage >= 0.40:
            return 2
        else:
            return 0
    
    def _score_error_schemas(self, spec: OpenAPISpec) -> int:
        """Score error response schema definitions (6 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for error schemas.
        """
        total_error_responses = sum(
            len([r for r in op.responses if r.status_code.startswith(('4', '5'))])
            for op in spec.operations
        )
        
        if total_error_responses == 0:
            return 6
        
        error_responses_with_schemas = sum(
            1 for op in spec.operations
            for resp in op.responses
            if resp.status_code.startswith(('4', '5')) and resp.has_schema
        )
        
        coverage = error_responses_with_schemas / total_error_responses
        
        if coverage >= 0.90:
            return 6
        elif coverage >= 0.70:
            return 4
        elif coverage >= 0.50:
            return 2
        else:
            return 0
    
    def _score_status_coverage(self, spec: OpenAPISpec) -> int:
        """Score HTTP status code coverage (4 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for status code coverage.
        """
        if not spec.operations:
            return 4
        
        operations_with_good_coverage = 0
        
        for operation in spec.operations:
            status_codes = {resp.status_code for resp in operation.responses}
            
            has_success = any(code.startswith('2') for code in status_codes)
            has_client_error = any(code.startswith('4') for code in status_codes)
            has_server_error = any(code.startswith('5') for code in status_codes)
            
            required_coverage = len(status_codes.intersection(self.required_error_codes))
            
            if has_success and has_client_error and has_server_error and required_coverage >= 2:
                operations_with_good_coverage += 1
        
        coverage = operations_with_good_coverage / len(spec.operations)
        
        if coverage >= 0.75:
            return 4
        elif coverage >= 0.50:
            return 2
        else:
            return 0
    
    def _score_error_examples(self, spec: OpenAPISpec) -> int:
        """Score error response examples (2 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for error examples.
        """
        total_error_responses = sum(
            len([r for r in op.responses if r.status_code.startswith(('4', '5'))])
            for op in spec.operations
        )
        
        if total_error_responses == 0:
            return 2
        
        error_responses_with_examples = sum(
            1 for op in spec.operations
            for resp in op.responses
            if resp.status_code.startswith(('4', '5')) and resp.has_example
        )
        
        coverage = error_responses_with_examples / total_error_responses
        
        if coverage >= 0.50:
            return 2
        elif coverage >= 0.25:
            return 1
        else:
            return 0
    
    def _identify_issues(self, spec: OpenAPISpec) -> List[str]:
        """Identify specific error handling issues.
        
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
        
        operations_without_errors = [
            op.operation_id or f"{op.method.value.upper()} {op.path}"
            for op in spec.operations
            if not op.has_error_responses
        ]
        
        if operations_without_errors:
            issues.append(f"{len(operations_without_errors)} operations lack error response documentation")
        
        operations_missing_required_errors = []
        for operation in spec.operations:
            error_codes = {
                resp.status_code for resp in operation.responses
                if resp.status_code.startswith(('4', '5'))
            }
            
            missing_required = self.required_error_codes - error_codes
            if missing_required and operation.has_error_responses:
                op_id = operation.operation_id or f"{operation.method.value.upper()} {operation.path}"
                operations_missing_required_errors.append(f"{op_id} (missing: {', '.join(missing_required)})")
        
        if operations_missing_required_errors:
            issues.append(f"{len(operations_missing_required_errors)} operations missing common error codes")
        
        error_responses_without_schemas = sum(
            1 for op in spec.operations
            for resp in op.responses
            if resp.status_code.startswith(('4', '5')) and not resp.has_schema
        )
        
        if error_responses_without_schemas > 0:
            issues.append(f"{error_responses_without_schemas} error responses lack schema definitions")
        
        return issues
    
    def get_recommendations(self, result: CategoryResult, spec: OpenAPISpec) -> List[Recommendation]:
        """Generate recommendations for improving error handling.
        
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
            
            if not operation.has_error_responses:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add error responses to {op_id}",
                        description=f"Operation {op_id} lacks error response documentation. This makes it difficult for agents to handle failures gracefully.",
                        severity=SeverityLevel.HIGH,
                        operation_id=operation.operation_id,
                        suggested_fix="Add common error responses like 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), and 500 (Internal Server Error).",
                        impact_score=8
                    )
                )
                continue
            
            error_codes = {
                resp.status_code for resp in operation.responses
                if resp.status_code.startswith(('4', '5'))
            }
            
            missing_required = self.required_error_codes - error_codes
            if missing_required:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add missing error codes to {op_id}",
                        description=f"Operation {op_id} is missing common error response codes: {', '.join(missing_required)}. These are important for proper error handling.",
                        severity=SeverityLevel.MEDIUM,
                        operation_id=operation.operation_id,
                        suggested_fix=f"Add response definitions for status codes: {', '.join(missing_required)}.",
                        impact_score=7
                    )
                )
            
            for response in operation.responses:
                if response.status_code.startswith(('4', '5')) and not response.has_schema:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Add schema to error response {response.status_code} in {op_id}",
                            description=f"Error response {response.status_code} in {op_id} lacks a schema definition. This makes it difficult for agents to parse error details.",
                            severity=SeverityLevel.MEDIUM,
                            operation_id=operation.operation_id,
                            suggested_fix="Define a schema for the error response that includes fields like 'error', 'message', and optionally 'details'.",
                            impact_score=6
                        )
                    )
                
                if response.status_code.startswith(('4', '5')) and not response.has_example:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Add example to error response {response.status_code} in {op_id}",
                            description=f"Error response {response.status_code} in {op_id} would benefit from an example to show the expected error format.",
                            severity=SeverityLevel.LOW,
                            operation_id=operation.operation_id,
                            suggested_fix="Add an example showing what the error response looks like, including typical error messages.",
                            impact_score=4
                        )
                    )
        
        operations_with_too_many_errors = [
            op for op in spec.operations
            if len([r for r in op.responses if r.status_code.startswith(('4', '5'))]) > 8
        ]
        
        for operation in operations_with_too_many_errors:
            op_id = operation.operation_id or f"{operation.method.value.upper()} {operation.path}"
            error_count = len([r for r in operation.responses if r.status_code.startswith(('4', '5'))])
            
            recommendations.append(
                self.create_recommendation(
                    title=f"Simplify error responses in {op_id}",
                    description=f"Operation {op_id} defines {error_count} error responses, which may be excessive. Consider consolidating similar error cases.",
                    severity=SeverityLevel.LOW,
                    operation_id=operation.operation_id,
                    suggested_fix="Review error responses and consolidate similar cases. Focus on the most common error scenarios.",
                    impact_score=3
                )
            )
        
        return recommendations