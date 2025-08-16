"""Agent usability analysis module."""

from typing import List, Dict, Set
import re
from collections import Counter
from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel
from config.settings import get_settings
from analyzer.base import BaseScoringModule, CategoryResult


class UsabilityAnalyzer(BaseScoringModule):
    """Analyzer for agent usability scoring (20 points total)."""

    def __init__(self):
        super().__init__(ScoreCategory.USABILITY, 20)
        self.settings = get_settings()

    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze agent usability across operations and organization.

        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.

        Returns
        -------
        CategoryResult
            Analysis result with usability score.
        """
        operation_naming_score = self._score_operation_naming(spec)
        discoverability_score = self._score_discoverability(spec)
        complexity_score = self._score_complexity(spec)
        consistency_score = self._score_consistency(spec)

        total_score = (
            operation_naming_score + discoverability_score + complexity_score + consistency_score
        )

        details = {
            "operation_naming": operation_naming_score,
            "discoverability": discoverability_score,
            "complexity": complexity_score,
            "consistency": consistency_score,
            "operations_with_operation_ids": sum(1 for op in spec.operations if op.operation_id),
            "average_parameters_per_operation": (
                spec.total_parameters / len(spec.operations) if spec.operations else 0
            ),
            "tags_used": len(spec.tags),
        }

        issues = self._identify_issues(spec)

        return CategoryResult(
            category=self.category,
            score=total_score,
            max_score=self.max_score,
            details=details,
            issues=issues,
        )

    def _score_operation_naming(self, spec: OpenAPISpec) -> int:
        """Score operation naming quality (6 points max).

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        int
            Score for operation naming.
        """
        if not spec.operations:
            return 6

        operations_with_ids = sum(1 for op in spec.operations if op.operation_id)
        good_naming_count = 0

        for operation in spec.operations:
            if not operation.operation_id:
                continue

            naming_quality = self._assess_operation_id_quality(
                operation.operation_id, operation.method.value, operation.path
            )
            if naming_quality["score"] >= 2:
                good_naming_count += 1

        id_coverage = operations_with_ids / len(spec.operations)
        naming_quality = good_naming_count / operations_with_ids if operations_with_ids > 0 else 0

        if id_coverage >= 0.95 and naming_quality >= 0.80:
            return 6
        elif id_coverage >= 0.80 and naming_quality >= 0.70:
            return 4
        elif id_coverage >= 0.60:
            return 2
        else:
            return 0

    def _score_discoverability(self, spec: OpenAPISpec) -> int:
        """Score API organization and discoverability (5 points max).

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        int
            Score for discoverability.
        """
        score = 0

        if len(spec.tags) > 0:
            score += 2

            operations_with_tags = sum(1 for op in spec.operations if op.tags)
            if spec.operations and operations_with_tags / len(spec.operations) >= 0.80:
                score += 1

        if spec.operations:
            operations_with_summaries = sum(1 for op in spec.operations if op.summary)
            summary_coverage = operations_with_summaries / len(spec.operations)

            if summary_coverage >= 0.80:
                score += 2
            elif summary_coverage >= 0.50:
                score += 1

        return min(score, 5)

    def _score_complexity(self, spec: OpenAPISpec) -> int:
        """Score operation complexity (5 points max).

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        int
            Score for complexity management.
        """
        if not spec.operations:
            return 5

        complex_operations = sum(
            1
            for op in spec.operations
            if op.parameter_count > self.settings.max_parameters_per_operation
        )

        very_complex_operations = sum(
            1
            for op in spec.operations
            if op.parameter_count > self.settings.max_parameters_per_operation * 1.5
        )

        complexity_ratio = complex_operations / len(spec.operations)
        very_complex_ratio = very_complex_operations / len(spec.operations)

        if very_complex_ratio > 0.20:
            return 0
        elif complexity_ratio > 0.30:
            return 1
        elif complexity_ratio > 0.15:
            return 3
        else:
            return 5

    def _score_consistency(self, spec: OpenAPISpec) -> int:
        """Score naming and pattern consistency (4 points max).

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        int
            Score for consistency.
        """
        if not spec.operations:
            return 4

        naming_consistency = self._assess_naming_consistency(spec)
        path_consistency = self._assess_path_consistency(spec)

        consistency_score = 0

        if naming_consistency >= 0.80:
            consistency_score += 2
        elif naming_consistency >= 0.60:
            consistency_score += 1

        if path_consistency >= 0.80:
            consistency_score += 2
        elif path_consistency >= 0.60:
            consistency_score += 1

        return consistency_score

    def _assess_operation_id_quality(
        self, operation_id: str, method: str, path: str
    ) -> Dict[str, any]:
        """Assess the quality of an operation ID.

        Parameters
        ----------
        operation_id : str
            Operation ID to assess.
        method : str
            HTTP method.
        path : str
            API path.

        Returns
        -------
        Dict[str, any]
            Assessment results.
        """
        issues = []
        score = 3

        if not operation_id:
            return {"score": 0, "issues": ["Missing operation ID"]}

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", operation_id):
            issues.append("Operation ID should use camelCase or snake_case")
            score -= 1

        method_verbs = {
            "get": ["get", "fetch", "retrieve", "list", "find"],
            "post": ["create", "add", "post", "submit"],
            "put": ["update", "replace", "put"],
            "patch": ["update", "modify", "patch"],
            "delete": ["delete", "remove", "destroy"],
        }

        expected_verbs = method_verbs.get(method.lower(), [])
        if expected_verbs and not any(verb in operation_id.lower() for verb in expected_verbs):
            issues.append(f"Operation ID should indicate {method.upper()} action")
            score -= 1

        if len(operation_id) < 3:
            issues.append("Operation ID too short")
            score -= 1
        elif len(operation_id) > 50:
            issues.append("Operation ID too long")
            score -= 1

        return {"score": max(0, score), "issues": issues}

    def _assess_naming_consistency(self, spec: OpenAPISpec) -> float:
        """Assess naming consistency across the API.

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        float
            Consistency score (0.0 to 1.0).
        """
        if not spec.operations:
            return 1.0

        operation_ids = [op.operation_id for op in spec.operations if op.operation_id]
        if not operation_ids:
            return 0.0

        camel_case_count = sum(1 for op_id in operation_ids if self._is_camel_case(op_id))
        snake_case_count = sum(1 for op_id in operation_ids if self._is_snake_case(op_id))

        total_consistent = max(camel_case_count, snake_case_count)
        return total_consistent / len(operation_ids)

    def _assess_path_consistency(self, spec: OpenAPISpec) -> float:
        """Assess path structure consistency.

        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.

        Returns
        -------
        float
            Consistency score (0.0 to 1.0).
        """
        if not spec.operations:
            return 1.0

        paths = [op.path for op in spec.operations]

        kebab_case_count = sum(1 for path in paths if self._uses_kebab_case(path))
        snake_case_count = sum(1 for path in paths if self._uses_snake_case_paths(path))
        camel_case_count = sum(1 for path in paths if self._uses_camel_case_paths(path))

        total_consistent = max(kebab_case_count, snake_case_count, camel_case_count)
        return total_consistent / len(paths)

    def _is_camel_case(self, text: str) -> bool:
        """Check if text uses camelCase."""
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", text) and re.search(r"[A-Z]", text))

    def _is_snake_case(self, text: str) -> bool:
        """Check if text uses snake_case."""
        return bool(re.match(r"^[a-z][a-z0-9_]*$", text) and "_" in text)

    def _uses_kebab_case(self, path: str) -> bool:
        """Check if path uses kebab-case."""
        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        return all("-" in part and part.islower() for part in path_parts if len(part) > 3)

    def _uses_snake_case_paths(self, path: str) -> bool:
        """Check if path uses snake_case."""
        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        return all("_" in part and part.islower() for part in path_parts if len(part) > 3)

    def _uses_camel_case_paths(self, path: str) -> bool:
        """Check if path uses camelCase."""
        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        return all(self._is_camel_case(part) for part in path_parts if len(part) > 3)

    def _identify_issues(self, spec: OpenAPISpec) -> List[str]:
        """Identify specific usability issues.

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

        operations_without_ids = sum(1 for op in spec.operations if not op.operation_id)
        if operations_without_ids > 0:
            issues.append(f"{operations_without_ids} operations lack operation IDs")

        complex_operations = [
            op.operation_id or f"{op.method.value.upper()} {op.path}"
            for op in spec.operations
            if op.parameter_count > self.settings.max_parameters_per_operation
        ]

        if complex_operations:
            issues.append(f"{len(complex_operations)} operations have too many parameters")

        operations_without_tags = sum(1 for op in spec.operations if not op.tags)
        if operations_without_tags > 0:
            issues.append(f"{operations_without_tags} operations lack tags for organization")

        if len(spec.tags) == 0:
            issues.append("API lacks tag definitions for organization")

        naming_consistency = self._assess_naming_consistency(spec)
        if naming_consistency < 0.70:
            issues.append("Inconsistent operation ID naming conventions")

        return issues

    def get_recommendations(
        self, result: CategoryResult, spec: OpenAPISpec
    ) -> List[Recommendation]:
        """Generate recommendations for improving agent usability.

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

            if not operation.operation_id:
                suggested_id = self._suggest_operation_id(operation.method.value, operation.path)
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add operation ID to {op_id}",
                        description=f"Operation {op_id} lacks an operation ID, making it harder for agents to reference this operation programmatically.",
                        severity=SeverityLevel.MEDIUM,
                        operation_id=operation.operation_id,
                        suggested_fix=f"Add operationId field, suggested: '{suggested_id}'",
                        impact_score=7,
                    )
                )
            else:
                naming_quality = self._assess_operation_id_quality(
                    operation.operation_id, operation.method.value, operation.path
                )
                if naming_quality["score"] < 2:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Improve operation ID naming for {operation.operation_id}",
                            description=f"Operation ID '{operation.operation_id}' has naming issues: {', '.join(naming_quality['issues'])}",
                            severity=SeverityLevel.LOW,
                            operation_id=operation.operation_id,
                            suggested_fix="Use clear, consistent naming that indicates the operation's purpose and follows camelCase or snake_case conventions.",
                            impact_score=5,
                        )
                    )

            if operation.parameter_count > self.settings.max_parameters_per_operation:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Reduce parameter complexity in {op_id}",
                        description=f"Operation {op_id} has {operation.parameter_count} parameters, which may be too complex for agents to handle effectively.",
                        severity=SeverityLevel.MEDIUM,
                        operation_id=operation.operation_id,
                        suggested_fix="Consider grouping related parameters into request body objects or splitting into multiple simpler operations.",
                        impact_score=6,
                    )
                )

            if not operation.tags:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add tags to {op_id}",
                        description=f"Operation {op_id} lacks tags, making it harder to organize and discover related operations.",
                        severity=SeverityLevel.LOW,
                        operation_id=operation.operation_id,
                        suggested_fix="Add appropriate tags that group this operation with related functionality.",
                        impact_score=4,
                    )
                )

        if len(spec.tags) == 0:
            recommendations.append(
                self.create_recommendation(
                    title="Add tag definitions",
                    description="The API lacks tag definitions, which help organize operations and improve discoverability.",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix="Define tags in the top-level 'tags' array with names and descriptions for each functional area.",
                    impact_score=6,
                )
            )

        naming_consistency = self._assess_naming_consistency(spec)
        if naming_consistency < 0.70:
            recommendations.append(
                self.create_recommendation(
                    title="Improve naming consistency",
                    description="Operation IDs use inconsistent naming conventions, which can confuse agents and developers.",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix="Standardize on either camelCase or snake_case for all operation IDs throughout the API.",
                    impact_score=6,
                )
            )

        return recommendations

    def _suggest_operation_id(self, method: str, path: str) -> str:
        """Suggest an operation ID based on method and path.

        Parameters
        ----------
        method : str
            HTTP method.
        path : str
            API path.

        Returns
        -------
        str
            Suggested operation ID.
        """
        method_prefixes = {
            "get": "get",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete",
        }

        prefix = method_prefixes.get(method.lower(), method.lower())

        path_parts = [part for part in path.split("/") if part and not part.startswith("{")]
        if path_parts:
            resource = path_parts[-1]
            if resource.endswith("s") and method.lower() == "get":
                prefix = "list"

            resource_name = resource.replace("-", "").replace("_", "").title()
            return f"{prefix}{resource_name}"

        return f"{prefix}Resource"
