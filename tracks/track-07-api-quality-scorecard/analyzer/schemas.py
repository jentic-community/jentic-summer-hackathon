"""Schema completeness analysis module."""

from typing import List
from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel
from config.settings import get_settings
from analyzer.base import BaseScoringModule, CategoryResult


class SchemaAnalyzer(BaseScoringModule):
    """Analyzer for schema completeness scoring (25 points total)."""
    
    def __init__(self):
        super().__init__(ScoreCategory.SCHEMAS, 25)
        self.settings = get_settings()
    
    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze schema completeness across requests and responses.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
            
        Returns
        -------
        CategoryResult
            Analysis result with schema completeness score.
        """
        request_schema_score = self._score_request_schemas(spec)
        response_schema_score = self._score_response_schemas(spec)
        parameter_types_score = self._score_parameter_types(spec)
        required_fields_score = self._score_required_fields(spec)
        
        total_score = (
            request_schema_score +
            response_schema_score +
            parameter_types_score +
            required_fields_score
        )
        
        details = {
            "request_schemas": request_schema_score,
            "response_schemas": response_schema_score,
            "parameter_types": parameter_types_score,
            "required_fields": required_fields_score,
            "operations_with_request_body": sum(1 for op in spec.operations if op.has_request_body),
            "total_responses": sum(len(op.responses) for op in spec.operations),
            "total_schemas": len(spec.schemas)
        }
        
        issues = self._identify_issues(spec)
        
        return CategoryResult(
            category=self.category,
            score=total_score,
            max_score=self.max_score,
            details=details,
            issues=issues
        )
    
    def _score_request_schemas(self, spec: OpenAPISpec) -> int:
        """Score request body schema completeness (8 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for request schemas.
        """
        operations_with_request_body = [op for op in spec.operations if op.has_request_body]
        
        if not operations_with_request_body:
            return 8
        
        operations_with_schema = sum(
            1 for op in operations_with_request_body
            if op.request_body_schema
        )
        
        coverage = operations_with_schema / len(operations_with_request_body)
        
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
    
    def _score_response_schemas(self, spec: OpenAPISpec) -> int:
        """Score response schema completeness (8 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for response schemas.
        """
        total_responses = sum(len(op.responses) for op in spec.operations)
        
        if total_responses == 0:
            return 8
        
        responses_with_schemas = sum(
            1 for op in spec.operations
            for resp in op.responses
            if resp.has_schema
        )
        
        coverage = responses_with_schemas / total_responses
        
        if coverage >= 0.90:
            return 8
        elif coverage >= 0.75:
            return 6
        elif coverage >= 0.50:
            return 4
        elif coverage >= 0.25:
            return 2
        else:
            return 0
    
    def _score_parameter_types(self, spec: OpenAPISpec) -> int:
        """Score parameter type definitions (5 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for parameter types.
        """
        total_params = spec.total_parameters
        
        if total_params == 0:
            return 5
        
        params_with_types = sum(
            1 for op in spec.operations
            for param in op.parameters
            if param.type
        )
        
        params_with_constraints = sum(
            1 for op in spec.operations
            for param in op.parameters
            if param.has_constraints
        )
        
        type_coverage = params_with_types / total_params
        constraint_coverage = params_with_constraints / total_params
        
        type_score = 3 if type_coverage >= 0.85 else (2 if type_coverage >= 0.70 else 1)
        constraint_score = 2 if constraint_coverage >= 0.50 else (1 if constraint_coverage >= 0.25 else 0)
        
        return min(type_score + constraint_score, 5)
    
    def _score_required_fields(self, spec: OpenAPISpec) -> int:
        """Score required field specifications (4 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for required field specifications.
        """
        if not spec.schemas:
            return 4
        
        schemas_with_required = sum(
            1 for schema in spec.schemas
            if schema.required_fields
        )
        
        path_params_properly_required = sum(
            1 for op in spec.operations
            for param in op.parameters
            if param.location == 'path' and param.required
        )
        
        path_params_total = sum(
            1 for op in spec.operations
            for param in op.parameters
            if param.location == 'path'
        )
        
        schema_score = 2 if len(spec.schemas) == 0 or schemas_with_required / len(spec.schemas) >= 0.75 else 1
        path_param_score = 2 if path_params_total == 0 or path_params_properly_required == path_params_total else 0
        
        return min(schema_score + path_param_score, 4)
    
    def _identify_issues(self, spec: OpenAPISpec) -> List[str]:
        """Identify specific schema completeness issues.
        
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
        
        operations_missing_request_schema = [
            op.operation_id or f"{op.method.value.upper()} {op.path}"
            for op in spec.operations
            if op.has_request_body and not op.request_body_schema
        ]
        
        if operations_missing_request_schema:
            issues.append(f"{len(operations_missing_request_schema)} operations with request bodies lack schemas")
        
        responses_without_schemas = sum(
            1 for op in spec.operations
            for resp in op.responses
            if not resp.has_schema and resp.status_code.startswith('2')
        )
        
        if responses_without_schemas > 0:
            issues.append(f"{responses_without_schemas} success responses lack schemas")
        
        params_without_types = sum(
            1 for op in spec.operations
            for param in op.parameters
            if not param.type
        )
        
        if params_without_types > 0:
            issues.append(f"{params_without_types} parameters lack type definitions")
        
        path_params_not_required = [
            f"{param.name} in {op.operation_id or op.path}"
            for op in spec.operations
            for param in op.parameters
            if param.location == 'path' and not param.required
        ]
        
        if path_params_not_required:
            issues.append(f"{len(path_params_not_required)} path parameters not marked as required")
        
        return issues
    
    def get_recommendations(self, result: CategoryResult, spec: OpenAPISpec) -> List[Recommendation]:
        """Generate recommendations for improving schema completeness.
        
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
            
            if operation.has_request_body and not operation.request_body_schema:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add request body schema to {op_id}",
                        description=f"Operation {op_id} accepts a request body but lacks a schema definition. This makes it difficult for agents to construct valid requests.",
                        severity=SeverityLevel.HIGH,
                        operation_id=operation.operation_id,
                        suggested_fix="Define a schema for the request body in the requestBody.content section.",
                        impact_score=8
                    )
                )
            
            for response in operation.responses:
                if response.status_code.startswith('2') and not response.has_schema:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Add response schema to {op_id} ({response.status_code})",
                            description=f"Success response {response.status_code} in {op_id} lacks a schema definition. This makes it difficult for agents to understand the response structure.",
                            severity=SeverityLevel.MEDIUM,
                            operation_id=operation.operation_id,
                            suggested_fix=f"Add a schema definition for the {response.status_code} response.",
                            impact_score=7
                        )
                    )
            
            for param in operation.parameters:
                if not param.type:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Add type to parameter '{param.name}'",
                            description=f"Parameter '{param.name}' in {op_id} lacks a type definition. This creates ambiguity about what values are expected.",
                            severity=SeverityLevel.MEDIUM,
                            operation_id=operation.operation_id,
                            parameter_name=param.name,
                            suggested_fix="Add a type field (string, integer, boolean, etc.) to the parameter schema.",
                            impact_score=6
                        )
                    )
                
                if param.location == 'path' and not param.required:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Mark path parameter '{param.name}' as required",
                            description=f"Path parameter '{param.name}' in {op_id} should be marked as required since path parameters are always mandatory.",
                            severity=SeverityLevel.HIGH,
                            operation_id=operation.operation_id,
                            parameter_name=param.name,
                            suggested_fix="Set the 'required' field to true for this path parameter.",
                            impact_score=8
                        )
                    )
                
                if param.type and not param.has_constraints:
                    if param.type in ['string', 'integer', 'number']:
                        recommendations.append(
                            self.create_recommendation(
                                title=f"Add constraints to parameter '{param.name}'",
                                description=f"Parameter '{param.name}' in {op_id} would benefit from validation constraints (min/max length, format, etc.).",
                                severity=SeverityLevel.LOW,
                                operation_id=operation.operation_id,
                                parameter_name=param.name,
                                suggested_fix="Add appropriate constraints like minLength, maxLength, minimum, maximum, or format.",
                                impact_score=4
                            )
                        )
        
        schemas_without_required = [
            schema.name for schema in spec.schemas
            if schema.properties_count > 0 and not schema.required_fields
        ]
        
        for schema_name in schemas_without_required:
            recommendations.append(
                self.create_recommendation(
                    title=f"Define required fields for schema '{schema_name}'",
                    description=f"Schema '{schema_name}' has properties but no required fields specified. This makes it unclear which fields are mandatory.",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix="Add a 'required' array listing the mandatory fields for this schema.",
                    impact_score=6
                )
            )
        
        return recommendations