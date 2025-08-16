"""Authentication clarity analysis module."""

from typing import List, Dict, Any
from core.models import OpenAPISpec, Recommendation
from core.types import ScoreCategory, SeverityLevel
from config.settings import get_settings
from analyzer.base import BaseScoringModule, CategoryResult


class AuthenticationAnalyzer(BaseScoringModule):
    """Analyzer for authentication clarity scoring (10 points total)."""
    
    def __init__(self):
        super().__init__(ScoreCategory.AUTHENTICATION, 10)
        self.settings = get_settings()
    
    def analyze(self, spec: OpenAPISpec) -> CategoryResult:
        """Analyze authentication documentation clarity.
        
        Parameters
        ----------
        spec : OpenAPISpec
            Parsed OpenAPI specification to analyze.
            
        Returns
        -------
        CategoryResult
            Analysis result with authentication clarity score.
        """
        security_schemes_score = self._score_security_schemes(spec)
        auth_examples_score = self._score_auth_examples(spec)
        scope_definitions_score = self._score_scope_definitions(spec)
        auth_flow_docs_score = self._score_auth_flow_docs(spec)
        
        total_score = (
            security_schemes_score +
            auth_examples_score +
            scope_definitions_score +
            auth_flow_docs_score
        )
        
        details = {
            "security_schemes": security_schemes_score,
            "auth_examples": auth_examples_score,
            "scope_definitions": scope_definitions_score,
            "auth_flow_docs": auth_flow_docs_score,
            "security_schemes_count": len(spec.security_schemes),
            "operations_with_security": sum(1 for op in spec.operations if op.security_requirements)
        }
        
        issues = self._identify_issues(spec)
        
        return CategoryResult(
            category=self.category,
            score=total_score,
            max_score=self.max_score,
            details=details,
            issues=issues
        )
    
    def _score_security_schemes(self, spec: OpenAPISpec) -> int:
        """Score security scheme completeness (4 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for security schemes.
        """
        if not spec.security_schemes:
            return 0
        
        score = 0
        well_documented_schemes = 0
        
        for scheme_name, scheme in spec.security_schemes.items():
            if not isinstance(scheme, dict):
                continue
            
            scheme_score = 0
            
            if 'type' in scheme:
                scheme_score += 1
            
            if 'description' in scheme and len(scheme.get('description', '').strip()) >= 20:
                scheme_score += 1
            
            scheme_type = scheme.get('type', '')
            if scheme_type == 'oauth2':
                if 'flows' in scheme:
                    scheme_score += 1
            elif scheme_type == 'http':
                if 'scheme' in scheme:
                    scheme_score += 1
            elif scheme_type == 'apiKey':
                if 'name' in scheme and 'in' in scheme:
                    scheme_score += 1
            
            if scheme_score >= 2:
                well_documented_schemes += 1
        
        if len(spec.security_schemes) > 0:
            coverage = well_documented_schemes / len(spec.security_schemes)
            if coverage >= 0.80:
                score = 4
            elif coverage >= 0.60:
                score = 3
            elif coverage >= 0.40:
                score = 2
            else:
                score = 1
        
        return score
    
    def _score_auth_examples(self, spec: OpenAPISpec) -> int:
        """Score authentication examples and guidance (3 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for authentication examples.
        """
        if not spec.security_schemes:
            return 3
        
        score = 0
        schemes_with_examples = 0
        
        for scheme_name, scheme in spec.security_schemes.items():
            if not isinstance(scheme, dict):
                continue
            
            has_example = False
            
            description = scheme.get('description', '')
            if 'example' in description.lower() or 'curl' in description.lower():
                has_example = True
            
            scheme_type = scheme.get('type', '')
            if scheme_type == 'http' and scheme.get('scheme') == 'bearer':
                if 'bearer' in description.lower() or 'token' in description.lower():
                    has_example = True
            
            if has_example:
                schemes_with_examples += 1
        
        if len(spec.security_schemes) > 0:
            coverage = schemes_with_examples / len(spec.security_schemes)
            if coverage >= 0.75:
                score = 3
            elif coverage >= 0.50:
                score = 2
            elif coverage >= 0.25:
                score = 1
        
        return score
    
    def _score_scope_definitions(self, spec: OpenAPISpec) -> int:
        """Score OAuth scope definitions (2 points max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for scope definitions.
        """
        oauth_schemes = [
            scheme for scheme in spec.security_schemes.values()
            if isinstance(scheme, dict) and scheme.get('type') == 'oauth2'
        ]
        
        if not oauth_schemes:
            return 2
        
        well_defined_scopes = 0
        
        for scheme in oauth_schemes:
            flows = scheme.get('flows', {})
            if not flows:
                continue
            
            has_good_scopes = False
            for flow_name, flow in flows.items():
                if not isinstance(flow, dict):
                    continue
                
                scopes = flow.get('scopes', {})
                if isinstance(scopes, dict) and len(scopes) > 0:
                    scope_descriptions = [desc for desc in scopes.values() if isinstance(desc, str) and len(desc.strip()) >= 10]
                    if len(scope_descriptions) >= len(scopes) * 0.75:
                        has_good_scopes = True
                        break
            
            if has_good_scopes:
                well_defined_scopes += 1
        
        if len(oauth_schemes) > 0:
            coverage = well_defined_scopes / len(oauth_schemes)
            if coverage >= 0.80:
                return 2
            elif coverage >= 0.50:
                return 1
        
        return 0
    
    def _score_auth_flow_docs(self, spec: OpenAPISpec) -> int:
        """Score authentication flow documentation (1 point max).
        
        Parameters
        ----------
        spec : OpenAPISpec
            Specification to analyze.
            
        Returns
        -------
        int
            Score for auth flow documentation.
        """
        if not spec.security_schemes:
            return 1
        
        has_flow_docs = False
        
        for scheme_name, scheme in spec.security_schemes.items():
            if not isinstance(scheme, dict):
                continue
            
            description = scheme.get('description', '')
            if len(description) >= 50:
                flow_keywords = ['flow', 'authenticate', 'authorization', 'token', 'login', 'grant']
                if any(keyword in description.lower() for keyword in flow_keywords):
                    has_flow_docs = True
                    break
            
            if scheme.get('type') == 'oauth2':
                flows = scheme.get('flows', {})
                for flow_name, flow in flows.items():
                    if isinstance(flow, dict):
                        if 'authorizationUrl' in flow or 'tokenUrl' in flow:
                            has_flow_docs = True
                            break
        
        return 1 if has_flow_docs else 0
    
    def _identify_issues(self, spec: OpenAPISpec) -> List[str]:
        """Identify specific authentication issues.
        
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
        
        if not spec.security_schemes:
            issues.append("No security schemes defined")
            return issues
        
        schemes_without_descriptions = [
            name for name, scheme in spec.security_schemes.items()
            if isinstance(scheme, dict) and (
                'description' not in scheme or 
                len(scheme.get('description', '').strip()) < 10
            )
        ]
        
        if schemes_without_descriptions:
            issues.append(f"{len(schemes_without_descriptions)} security schemes lack adequate descriptions")
        
        incomplete_oauth_schemes = []
        for name, scheme in spec.security_schemes.items():
            if isinstance(scheme, dict) and scheme.get('type') == 'oauth2':
                flows = scheme.get('flows', {})
                if not flows:
                    incomplete_oauth_schemes.append(name)
                else:
                    for flow_name, flow in flows.items():
                        if isinstance(flow, dict):
                            scopes = flow.get('scopes', {})
                            if not scopes or not isinstance(scopes, dict):
                                incomplete_oauth_schemes.append(f"{name} ({flow_name})")
        
        if incomplete_oauth_schemes:
            issues.append(f"Incomplete OAuth2 configurations: {', '.join(incomplete_oauth_schemes)}")
        
        operations_without_security = sum(
            1 for op in spec.operations 
            if not op.security_requirements
        )
        
        if operations_without_security > 0:
            issues.append(f"{operations_without_security} operations lack security requirements")
        
        return issues
    
    def get_recommendations(self, result: CategoryResult, spec: OpenAPISpec) -> List[Recommendation]:
        """Generate recommendations for improving authentication clarity.
        
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
        
        if not spec.security_schemes:
            recommendations.append(
                self.create_recommendation(
                    title="Add security scheme definitions",
                    description="The API lacks security scheme definitions, making it unclear how agents should authenticate requests.",
                    severity=SeverityLevel.HIGH,
                    suggested_fix="Define security schemes in components.securitySchemes section (e.g., Bearer token, API key, OAuth2).",
                    impact_score=9
                )
            )
            return recommendations
        
        for scheme_name, scheme in spec.security_schemes.items():
            if not isinstance(scheme, dict):
                continue
            
            if 'description' not in scheme or len(scheme.get('description', '').strip()) < 20:
                recommendations.append(
                    self.create_recommendation(
                        title=f"Add description to security scheme '{scheme_name}'",
                        description=f"Security scheme '{scheme_name}' lacks a comprehensive description explaining how to use it.",
                        severity=SeverityLevel.MEDIUM,
                        suggested_fix="Add a detailed description explaining how to obtain and use this authentication method, including examples.",
                        impact_score=6
                    )
                )
            
            scheme_type = scheme.get('type', '')
            if scheme_type == 'oauth2':
                flows = scheme.get('flows', {})
                if not flows:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Define OAuth2 flows for '{scheme_name}'",
                            description=f"OAuth2 security scheme '{scheme_name}' lacks flow definitions.",
                            severity=SeverityLevel.HIGH,
                            suggested_fix="Add flows section with appropriate OAuth2 flow types (authorizationCode, implicit, password, clientCredentials).",
                            impact_score=8
                        )
                    )
                else:
                    for flow_name, flow in flows.items():
                        if isinstance(flow, dict):
                            scopes = flow.get('scopes', {})
                            if not scopes or not isinstance(scopes, dict):
                                recommendations.append(
                                    self.create_recommendation(
                                        title=f"Define scopes for OAuth2 flow '{flow_name}' in '{scheme_name}'",
                                        description=f"OAuth2 flow '{flow_name}' lacks scope definitions, making it unclear what permissions are available.",
                                        severity=SeverityLevel.MEDIUM,
                                        suggested_fix="Add scopes object with scope names and descriptions explaining what each scope allows.",
                                        impact_score=7
                                    )
                                )
                            else:
                                poorly_described_scopes = [
                                    scope for scope, desc in scopes.items()
                                    if not isinstance(desc, str) or len(desc.strip()) < 10
                                ]
                                
                                if poorly_described_scopes:
                                    recommendations.append(
                                        self.create_recommendation(
                                            title=f"Improve scope descriptions in '{scheme_name}' {flow_name} flow",
                                            description=f"Scopes {', '.join(poorly_described_scopes)} lack adequate descriptions.",
                                            severity=SeverityLevel.LOW,
                                            suggested_fix="Add clear descriptions for each scope explaining what permissions it grants.",
                                            impact_score=5
                                        )
                                    )
            
            elif scheme_type == 'http':
                if 'scheme' not in scheme:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Specify HTTP scheme for '{scheme_name}'",
                            description=f"HTTP security scheme '{scheme_name}' lacks scheme specification (basic, bearer, etc.).",
                            severity=SeverityLevel.HIGH,
                            suggested_fix="Add 'scheme' field specifying the HTTP authentication scheme (e.g., 'bearer', 'basic').",
                            impact_score=8
                        )
                    )
            
            elif scheme_type == 'apiKey':
                missing_fields = []
                if 'name' not in scheme:
                    missing_fields.append('name')
                if 'in' not in scheme:
                    missing_fields.append('in')
                
                if missing_fields:
                    recommendations.append(
                        self.create_recommendation(
                            title=f"Complete API key scheme '{scheme_name}' definition",
                            description=f"API key security scheme '{scheme_name}' is missing required fields: {', '.join(missing_fields)}.",
                            severity=SeverityLevel.HIGH,
                            suggested_fix=f"Add missing fields: {', '.join(missing_fields)}. Specify the parameter name and location (header, query, cookie).",
                            impact_score=8
                        )
                    )
        
        operations_without_security = [
            op.operation_id or f"{op.method.value.upper()} {op.path}"
            for op in spec.operations
            if not op.security_requirements
        ]
        
        if operations_without_security:
            recommendations.append(
                self.create_recommendation(
                    title="Add security requirements to operations",
                    description=f"{len(operations_without_security)} operations lack security requirements, making it unclear if they require authentication.",
                    severity=SeverityLevel.MEDIUM,
                    suggested_fix="Add security requirements to operations that need authentication, or explicitly mark public operations with an empty security array.",
                    impact_score=6
                )
            )
        
        schemes_without_examples = [
            name for name, scheme in spec.security_schemes.items()
            if isinstance(scheme, dict) and not self._has_usage_examples(scheme)
        ]
        
        if schemes_without_examples:
            recommendations.append(
                self.create_recommendation(
                    title="Add authentication examples",
                    description=f"Security schemes {', '.join(schemes_without_examples)} would benefit from usage examples.",
                    severity=SeverityLevel.LOW,
                    suggested_fix="Add examples in the description showing how to use each authentication method (e.g., curl commands, header formats).",
                    impact_score=5
                )
            )
        
        return recommendations
    
    def _has_usage_examples(self, scheme: Dict[str, Any]) -> bool:
        """Check if security scheme has usage examples.
        
        Parameters
        ----------
        scheme : Dict[str, Any]
            Security scheme definition.
            
        Returns
        -------
        bool
            True if scheme has usage examples.
        """
        description = scheme.get('description', '').lower()
        example_indicators = ['example', 'curl', 'authorization:', 'bearer ', 'api-key:', 'x-api-key']
        return any(indicator in description for indicator in example_indicators)