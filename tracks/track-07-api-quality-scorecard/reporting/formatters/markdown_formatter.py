"""Markdown formatter for documentation-friendly reports."""

from typing import List
from core.models import ScoringResult, Recommendation
from core.types import SeverityLevel
from reporting.formatters.base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Formatter for Markdown output suitable for documentation."""
    
    def format(self, result: ScoringResult, detailed: bool = False) -> str:
        """Format scoring result as Markdown.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to format.
        detailed : bool, optional
            Whether to include detailed information, by default False.
            
        Returns
        -------
        str
            Markdown formatted report.
        """
        sections = []
        
        sections.append(self._format_header(result))
        sections.append(self._format_summary(result))
        sections.append(self._format_category_scores(result))
        sections.append(self._format_metrics(result))
        
        if detailed:
            sections.append(self._format_detailed_recommendations(result))
        else:
            sections.append(self._format_key_recommendations(result))
        
        sections.append(self._format_footer(result))
        
        return '\n\n'.join(sections)
    
    def get_file_extension(self) -> str:
        """Get file extension for Markdown format.
        
        Returns
        -------
        str
            File extension 'md'.
        """
        return 'md'
    
    def get_content_type(self) -> str:
        """Get MIME content type for Markdown.
        
        Returns
        -------
        str
            Markdown content type.
        """
        return 'text/markdown'
    
    def _format_header(self, result: ScoringResult) -> str:
        """Format report header.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted header.
        """
        api_title = result.spec_info.get('title', 'API Quality Report')
        api_version = result.spec_info.get('version', '1.0.0')
        
        return f"""# API Quality Scorecard Report

**API**: {api_title} v{api_version}  
**Analysis Date**: {self.format_timestamp(result.analysis_timestamp)}  
**OpenAPI Version**: {result.spec_info.get('openapi_version', '3.0')}"""
    
    def _format_summary(self, result: ScoringResult) -> str:
        """Format summary section.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted summary.
        """
        grade_emoji = {
            'A': '🟢',
            'B': '🟡', 
            'C': '🟠',
            'D': '🔴',
            'F': '⚫'
        }.get(result.quality_grade, '❓')
        
        return f"""## Overall Score

{grade_emoji} **{result.overall_score}/100** (Grade: {result.quality_grade})

### Quick Stats
- **Total Operations**: {result.spec_info.get('total_operations', 0)}
- **Critical Issues**: {result.critical_issues_count}
- **High Priority Issues**: {result.high_issues_count}
- **Total Recommendations**: {len(result.recommendations)}"""
    
    def _format_category_scores(self, result: ScoringResult) -> str:
        """Format category scores section.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted category scores.
        """
        categories = [
            ('Documentation Quality', result.category_scores.documentation, 25),
            ('Schema Completeness', result.category_scores.schemas, 25),
            ('Error Handling', result.category_scores.errors, 20),
            ('Agent Usability', result.category_scores.usability, 20),
            ('Authentication Clarity', result.category_scores.authentication, 10)
        ]
        
        lines = ['## Category Scores', '']
        
        for name, score, max_score in categories:
            percentage = (score / max_score) * 100
            bar = self._create_progress_bar(percentage)
            lines.append(f"### {name}")
            lines.append(f"**{score}/{max_score}** ({percentage:.1f}%)")
            lines.append(f"{bar}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_metrics(self, result: ScoringResult) -> str:
        """Format metrics section.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted metrics.
        """
        metrics = result.metrics
        
        return f"""## Analysis Metrics

| Metric | Count | Coverage |
|--------|-------|----------|
| Operations with descriptions | {metrics.operations_with_descriptions}/{metrics.total_operations} | {metrics.description_coverage_operations:.1f}% |
| Parameters with descriptions | {metrics.parameters_with_descriptions}/{metrics.total_parameters} | {metrics.description_coverage_parameters:.1f}% |
| Responses with schemas | {metrics.responses_with_schemas}/{metrics.total_responses} | {metrics.schema_coverage_responses:.1f}% |
| Operations with examples | {metrics.operations_with_examples}/{metrics.total_operations} | {(metrics.operations_with_examples/metrics.total_operations*100) if metrics.total_operations > 0 else 0:.1f}% |
| Operations with IDs | {metrics.operations_with_operation_ids}/{metrics.total_operations} | {(metrics.operations_with_operation_ids/metrics.total_operations*100) if metrics.total_operations > 0 else 0:.1f}% |
| Error responses documented | {metrics.error_responses_documented} | - |
| Security schemes | {metrics.security_schemes_count} | - |"""
    
    def _format_key_recommendations(self, result: ScoringResult) -> str:
        """Format key recommendations section.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted key recommendations.
        """
        critical_recs = [r for r in result.recommendations if r.severity == SeverityLevel.CRITICAL]
        high_recs = [r for r in result.recommendations if r.severity == SeverityLevel.HIGH]
        
        lines = ['## Key Recommendations']
        
        if critical_recs:
            lines.append('\n### 🚨 Critical Issues')
            for rec in critical_recs[:5]:
                lines.append(f"- **{rec.title}**: {rec.description}")
                if rec.suggested_fix:
                    lines.append(f"  - *Fix*: {rec.suggested_fix}")
        
        if high_recs:
            lines.append('\n### ⚠️ High Priority Issues')
            for rec in high_recs[:5]:
                lines.append(f"- **{rec.title}**: {rec.description}")
                if rec.suggested_fix:
                    lines.append(f"  - *Fix*: {rec.suggested_fix}")
        
        if not critical_recs and not high_recs:
            lines.append('\n✅ No critical or high priority issues found!')
        
        return '\n'.join(lines)
    
    def _format_detailed_recommendations(self, result: ScoringResult) -> str:
        """Format detailed recommendations section.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted detailed recommendations.
        """
        lines = ['## Detailed Recommendations']
        
        by_category = {}
        for rec in result.recommendations:
            category = rec.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        for category, recs in by_category.items():
            lines.append(f'\n### {category.title()} ({len(recs)} issues)')
            
            by_severity = {}
            for rec in recs:
                severity = rec.severity.value
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(rec)
            
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                if severity in by_severity:
                    severity_emoji = {
                        'critical': '🚨',
                        'high': '⚠️',
                        'medium': '🔶',
                        'low': 'ℹ️',
                        'info': '💡'
                    }.get(severity, '•')
                    
                    lines.append(f'\n#### {severity_emoji} {severity.title()} Priority')
                    
                    for rec in by_severity[severity]:
                        lines.append(f'\n**{rec.title}**')
                        lines.append(f'{rec.description}')
                        
                        if rec.operation_id:
                            lines.append(f'- *Operation*: `{rec.operation_id}`')
                        if rec.parameter_name:
                            lines.append(f'- *Parameter*: `{rec.parameter_name}`')
                        if rec.suggested_fix:
                            lines.append(f'- *Suggested Fix*: {rec.suggested_fix}')
                        lines.append(f'- *Impact Score*: {rec.impact_score}/10')
        
        return '\n'.join(lines)
    
    def _format_footer(self, result: ScoringResult) -> str:
        """Format report footer.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result.
            
        Returns
        -------
        str
            Formatted footer.
        """
        return f"""---

*Report generated by API Quality Scorecard v1.0.0*  
*Analysis completed at {self.format_timestamp(result.analysis_timestamp)}*

### Quality Grades
- **A (90-100)**: Excellent - Ready for production use
- **B (80-89)**: Good - Minor improvements recommended  
- **C (70-79)**: Acceptable - Some issues should be addressed
- **D (60-69)**: Needs Improvement - Significant issues present
- **F (0-59)**: Poor - Major improvements required"""
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create ASCII progress bar.
        
        Parameters
        ----------
        percentage : float
            Percentage value (0-100).
        width : int, optional
            Width of progress bar, by default 20.
            
        Returns
        -------
        str
            ASCII progress bar.
        """
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage >= 80:
            fill_char = '█'
        elif percentage >= 60:
            fill_char = '▓'
        else:
            fill_char = '░'
        
        bar = fill_char * filled + '░' * empty
        return f"`{bar}` {percentage:.1f}%"