"""JSON formatter for machine-readable reports."""

import json
from typing import Dict, Any
from core.models import ScoringResult
from reporting.formatters.base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output suitable for programmatic consumption."""
    
    def format(self, result: ScoringResult, detailed: bool = False) -> str:
        """Format scoring result as JSON.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to format.
        detailed : bool, optional
            Whether to include detailed information, by default False.
            
        Returns
        -------
        str
            JSON formatted report.
        """
        data = self._prepare_json_data(result, detailed)
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    
    def get_file_extension(self) -> str:
        """Get file extension for JSON format.
        
        Returns
        -------
        str
            File extension 'json'.
        """
        return 'json'
    
    def get_content_type(self) -> str:
        """Get MIME content type for JSON.
        
        Returns
        -------
        str
            JSON content type.
        """
        return 'application/json'
    
    def _prepare_json_data(self, result: ScoringResult, detailed: bool) -> Dict[str, Any]:
        """Prepare data structure for JSON serialization.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to convert.
        detailed : bool
            Whether to include detailed information.
            
        Returns
        -------
        Dict[str, Any]
            JSON-serializable data structure.
        """
        data = {
            'scorecard_version': '1.0.0',
            'analysis_timestamp': result.analysis_timestamp.isoformat(),
            'overall_score': result.overall_score,
            'quality_grade': result.quality_grade,
            'category_scores': {
                'documentation': {
                    'score': result.category_scores.documentation,
                    'max_score': 25,
                    'percentage': round((result.category_scores.documentation / 25) * 100, 1)
                },
                'schemas': {
                    'score': result.category_scores.schemas,
                    'max_score': 25,
                    'percentage': round((result.category_scores.schemas / 25) * 100, 1)
                },
                'errors': {
                    'score': result.category_scores.errors,
                    'max_score': 20,
                    'percentage': round((result.category_scores.errors / 20) * 100, 1)
                },
                'usability': {
                    'score': result.category_scores.usability,
                    'max_score': 20,
                    'percentage': round((result.category_scores.usability / 20) * 100, 1)
                },
                'authentication': {
                    'score': result.category_scores.authentication,
                    'max_score': 10,
                    'percentage': round((result.category_scores.authentication / 10) * 100, 1)
                }
            },
            'metrics': {
                'total_operations': result.metrics.total_operations,
                'operations_with_descriptions': result.metrics.operations_with_descriptions,
                'total_parameters': result.metrics.total_parameters,
                'parameters_with_descriptions': result.metrics.parameters_with_descriptions,
                'total_responses': result.metrics.total_responses,
                'responses_with_schemas': result.metrics.responses_with_schemas,
                'error_responses_documented': result.metrics.error_responses_documented,
                'operations_with_examples': result.metrics.operations_with_examples,
                'operations_with_operation_ids': result.metrics.operations_with_operation_ids,
                'security_schemes_count': result.metrics.security_schemes_count,
                'coverage_metrics': {
                    'description_coverage_operations': round(result.metrics.description_coverage_operations, 1),
                    'description_coverage_parameters': round(result.metrics.description_coverage_parameters, 1),
                    'schema_coverage_responses': round(result.metrics.schema_coverage_responses, 1)
                }
            },
            'spec_info': {
                'title': result.spec_info.get('title', 'Unknown API'),
                'version': result.spec_info.get('version', '1.0.0'),
                'openapi_version': result.spec_info.get('openapi_version', '3.0'),
                'total_operations': result.spec_info.get('total_operations', 0),
                'total_schemas': result.spec_info.get('total_schemas', 0)
            },
            'summary': {
                'critical_issues': result.critical_issues_count,
                'high_issues': result.high_issues_count,
                'total_recommendations': len(result.recommendations)
            }
        }
        
        if detailed:
            data['recommendations'] = [
                {
                    'type': rec.type.value,
                    'category': rec.category.value,
                    'severity': rec.severity.value,
                    'title': rec.title,
                    'description': rec.description,
                    'operation_id': rec.operation_id,
                    'parameter_name': rec.parameter_name,
                    'suggested_fix': rec.suggested_fix,
                    'impact_score': rec.impact_score
                }
                for rec in result.recommendations
            ]
            
            if 'category_details' in result.spec_info:
                data['category_details'] = result.spec_info['category_details']
        else:
            data['recommendations'] = {
                'critical': [
                    {
                        'title': rec.title,
                        'description': rec.description,
                        'suggested_fix': rec.suggested_fix
                    }
                    for rec in result.recommendations
                    if rec.severity.value == 'critical'
                ],
                'high': [
                    {
                        'title': rec.title,
                        'description': rec.description,
                        'suggested_fix': rec.suggested_fix
                    }
                    for rec in result.recommendations
                    if rec.severity.value == 'high'
                ][:5]
            }
        
        return data
    
    def format_compact(self, result: ScoringResult) -> str:
        """Format as compact JSON for API responses.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to format.
            
        Returns
        -------
        str
            Compact JSON string.
        """
        data = {
            'score': result.overall_score,
            'grade': result.quality_grade,
            'categories': {
                'documentation': result.category_scores.documentation,
                'schemas': result.category_scores.schemas,
                'errors': result.category_scores.errors,
                'usability': result.category_scores.usability,
                'authentication': result.category_scores.authentication
            },
            'issues': {
                'critical': result.critical_issues_count,
                'high': result.high_issues_count
            },
            'timestamp': result.analysis_timestamp.isoformat()
        }
        
        return json.dumps(data, separators=(',', ':'), default=str)