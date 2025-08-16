"""HTML formatter for rich visual reports."""

from typing import Dict, Any
from core.models import ScoringResult
from core.types import SeverityLevel
from reporting.formatters.base import BaseFormatter


class HTMLFormatter(BaseFormatter):
    """Formatter for HTML output with rich visualizations."""
    
    def format(self, result: ScoringResult, detailed: bool = False) -> str:
        """Format scoring result as HTML.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to format.
        detailed : bool, optional
            Whether to include detailed information, by default False.
            
        Returns
        -------
        str
            HTML formatted report.
        """
        template_vars = self.prepare_template_vars(result, detailed)
        
        if detailed:
            return self._render_detailed_template(template_vars)
        else:
            return self._render_summary_template(template_vars)
    
    def get_file_extension(self) -> str:
        """Get file extension for HTML format.
        
        Returns
        -------
        str
            File extension 'html'.
        """
        return 'html'
    
    def get_content_type(self) -> str:
        """Get MIME content type for HTML.
        
        Returns
        -------
        str
            HTML content type.
        """
        return 'text/html'
    
    def _render_summary_template(self, vars: Dict[str, Any]) -> str:
        """Render summary HTML template.
        
        Parameters
        ----------
        vars : Dict[str, Any]
            Template variables.
            
        Returns
        -------
        str
            Rendered HTML.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Quality Scorecard - {vars['spec_info'].get('title', 'API Report')}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>API Quality Scorecard</h1>
            <div class="api-info">
                <h2>{vars['spec_info'].get('title', 'API Report')}</h2>
                <p>Version: {vars['spec_info'].get('version', '1.0.0')} | 
                   OpenAPI: {vars['spec_info'].get('openapi_version', '3.0')} | 
                   Analyzed: {self.format_timestamp(vars['analysis_timestamp'])}</p>
            </div>
        </header>

        <div class="score-summary">
            <div class="overall-score {self.get_score_color(vars['overall_score'], 100)}">
                <div class="score-value">{vars['overall_score']}</div>
                <div class="score-label">Overall Score</div>
                <div class="grade">Grade: {vars['quality_grade']}</div>
            </div>
            
            <div class="quick-stats">
                <div class="stat">
                    <div class="stat-value">{vars['spec_info'].get('total_operations', 0)}</div>
                    <div class="stat-label">Operations</div>
                </div>
                <div class="stat critical">
                    <div class="stat-value">{vars['critical_issues']}</div>
                    <div class="stat-label">Critical Issues</div>
                </div>
                <div class="stat high">
                    <div class="stat-value">{vars['high_issues']}</div>
                    <div class="stat-label">High Priority</div>
                </div>
            </div>
        </div>

        <div class="categories">
            <h3>Category Scores</h3>
            <div class="category-grid">
                {self._render_category_card('Documentation', vars['documentation_score'], 25, vars['documentation_percentage'])}
                {self._render_category_card('Schemas', vars['schemas_score'], 25, vars['schemas_percentage'])}
                {self._render_category_card('Error Handling', vars['errors_score'], 20, vars['errors_percentage'])}
                {self._render_category_card('Usability', vars['usability_score'], 20, vars['usability_percentage'])}
                {self._render_category_card('Authentication', vars['authentication_score'], 10, vars['authentication_percentage'])}
            </div>
        </div>

        <div class="metrics">
            <h3>Analysis Metrics</h3>
            <div class="metrics-grid">
                {self._render_metric('Operations with Descriptions', vars['metrics'].operations_with_descriptions, vars['metrics'].total_operations)}
                {self._render_metric('Parameters with Descriptions', vars['metrics'].parameters_with_descriptions, vars['metrics'].total_parameters)}
                {self._render_metric('Responses with Schemas', vars['metrics'].responses_with_schemas, vars['metrics'].total_responses)}
                {self._render_metric('Operations with Examples', vars['metrics'].operations_with_examples, vars['metrics'].total_operations)}
            </div>
        </div>

        {self._render_recommendations_summary(vars['recommendations'])}

        <footer class="footer">
            <p>Generated by API Quality Scorecard v1.0.0</p>
        </footer>
    </div>
</body>
</html>"""
    
    def _render_detailed_template(self, vars: Dict[str, Any]) -> str:
        """Render detailed HTML template.
        
        Parameters
        ----------
        vars : Dict[str, Any]
            Template variables.
            
        Returns
        -------
        str
            Rendered detailed HTML.
        """
        summary_html = self._render_summary_template(vars)
        
        detailed_sections = f"""
        <div class="detailed-recommendations">
            <h3>Detailed Recommendations</h3>
            {self._render_detailed_recommendations(vars['recommendations'])}
        </div>
        """
        
        return summary_html.replace('</div>\n</body>', f'{detailed_sections}</div>\n</body>')
    
    def _render_category_card(self, name: str, score: int, max_score: int, percentage: float) -> str:
        """Render category score card.
        
        Parameters
        ----------
        name : str
            Category name.
        score : int
            Category score.
        max_score : int
            Maximum possible score.
        percentage : float
            Score percentage.
            
        Returns
        -------
        str
            HTML for category card.
        """
        color_class = self.get_score_color(score, max_score)
        
        return f"""
        <div class="category-card {color_class}">
            <div class="category-name">{name}</div>
            <div class="category-score">{score}/{max_score}</div>
            <div class="category-percentage">{percentage:.1f}%</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%"></div>
            </div>
        </div>"""
    
    def _render_metric(self, name: str, value: int, total: int) -> str:
        """Render metric display.
        
        Parameters
        ----------
        name : str
            Metric name.
        value : int
            Metric value.
        total : int
            Total possible value.
            
        Returns
        -------
        str
            HTML for metric.
        """
        percentage = (value / total * 100) if total > 0 else 0
        
        return f"""
        <div class="metric">
            <div class="metric-name">{name}</div>
            <div class="metric-value">{value}/{total}</div>
            <div class="metric-percentage">{percentage:.1f}%</div>
        </div>"""
    
    def _render_recommendations_summary(self, recommendations) -> str:
        """Render recommendations summary.
        
        Parameters
        ----------
        recommendations : list
            List of recommendations.
            
        Returns
        -------
        str
            HTML for recommendations summary.
        """
        critical_recs = [r for r in recommendations if r.severity == SeverityLevel.CRITICAL]
        high_recs = [r for r in recommendations if r.severity == SeverityLevel.HIGH]
        
        html = '<div class="recommendations-summary"><h3>Key Recommendations</h3>'
        
        if critical_recs:
            html += '<div class="critical-issues"><h4>🚨 Critical Issues</h4><ul>'
            for rec in critical_recs[:3]:
                html += f'<li><strong>{rec.title}</strong>: {rec.description}</li>'
            html += '</ul></div>'
        
        if high_recs:
            html += '<div class="high-issues"><h4>⚠️ High Priority Issues</h4><ul>'
            for rec in high_recs[:3]:
                html += f'<li><strong>{rec.title}</strong>: {rec.description}</li>'
            html += '</ul></div>'
        
        if not critical_recs and not high_recs:
            html += '<div class="no-issues">✅ No critical or high priority issues found!</div>'
        
        html += '</div>'
        return html
    
    def _render_detailed_recommendations(self, recommendations) -> str:
        """Render detailed recommendations section.
        
        Parameters
        ----------
        recommendations : list
            List of recommendations.
            
        Returns
        -------
        str
            HTML for detailed recommendations.
        """
        by_category = {}
        for rec in recommendations:
            category = rec.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)
        
        html = ''
        for category, recs in by_category.items():
            html += f'<div class="category-recommendations"><h4>{category.title()} ({len(recs)} issues)</h4>'
            
            for rec in recs:
                severity_class = self.get_severity_color(rec.severity.value)
                html += f'''
                <div class="recommendation {severity_class}">
                    <div class="rec-header">
                        <span class="rec-title">{rec.title}</span>
                        <span class="rec-severity {rec.severity.value}">{rec.severity.value.upper()}</span>
                    </div>
                    <div class="rec-description">{rec.description}</div>
                    {f'<div class="rec-operation">Operation: <code>{rec.operation_id}</code></div>' if rec.operation_id else ''}
                    {f'<div class="rec-parameter">Parameter: <code>{rec.parameter_name}</code></div>' if rec.parameter_name else ''}
                    {f'<div class="rec-fix"><strong>Suggested Fix:</strong> {rec.suggested_fix}</div>' if rec.suggested_fix else ''}
                    <div class="rec-impact">Impact Score: {rec.impact_score}/10</div>
                </div>'''
            
            html += '</div>'
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report.
        
        Returns
        -------
        str
            CSS styles.
        """
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .api-info h2 {
            color: #34495e;
            margin-bottom: 5px;
        }
        
        .score-summary {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }
        
        .overall-score {
            text-align: center;
        }
        
        .score-value {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .score-label {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .grade {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .quick-stats {
            display: flex;
            gap: 30px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .category-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .category-card.success { background: #d4edda; border-left: 4px solid #28a745; }
        .category-card.warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .category-card.danger { background: #f8d7da; border-left: 4px solid #dc3545; }
        
        .category-name {
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .category-score {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .category-percentage {
            color: #666;
            margin-bottom: 10px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .metric {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #007bff;
        }
        
        .metric-name {
            font-weight: 500;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #007bff;
        }
        
        .recommendations-summary {
            margin-bottom: 30px;
        }
        
        .recommendations-summary h3 {
            margin-bottom: 20px;
            color: #2c3e50;
        }
        
        .critical-issues, .high-issues {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 6px;
        }
        
        .critical-issues {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        
        .high-issues {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        
        .no-issues {
            padding: 20px;
            text-align: center;
            background: #d4edda;
            border-radius: 6px;
            color: #155724;
            font-weight: 500;
        }
        
        .recommendation {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ccc;
        }
        
        .recommendation.danger { border-left-color: #dc3545; background: #f8d7da; }
        .recommendation.warning { border-left-color: #ffc107; background: #fff3cd; }
        .recommendation.info { border-left-color: #17a2b8; background: #d1ecf1; }
        
        .rec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .rec-title {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .rec-severity {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .rec-severity.critical { background: #dc3545; color: white; }
        .rec-severity.high { background: #fd7e14; color: white; }
        .rec-severity.medium { background: #ffc107; color: #212529; }
        .rec-severity.low { background: #17a2b8; color: white; }
        
        .rec-description {
            margin-bottom: 10px;
            color: #495057;
        }
        
        .rec-operation, .rec-parameter {
            margin-bottom: 5px;
            font-size: 0.9em;
            color: #6c757d;
        }
        
        .rec-fix {
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(0,0,0,0.05);
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .rec-impact {
            font-size: 0.8em;
            color: #6c757d;
            text-align: right;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #6c757d;
        }
        
        code {
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }
        """