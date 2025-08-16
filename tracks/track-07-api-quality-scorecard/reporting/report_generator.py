"""Main report generator that orchestrates different output formats."""

from pathlib import Path
from typing import Dict, Any, Optional
from core.models import ScoringResult
from core.types import OutputFormat
from core.exceptions import ReportGenerationError
from config.settings import get_settings
from reporting.formatters import (
    BaseFormatter,
    HTMLFormatter,
    JSONFormatter,
    MarkdownFormatter
)


class ReportGenerator:
    """Main report generator that coordinates different output formatters."""
    
    def __init__(self):
        self.settings = get_settings()
        self.formatters: Dict[OutputFormat, BaseFormatter] = {
            OutputFormat.HTML: HTMLFormatter(),
            OutputFormat.JSON: JSONFormatter(),
            OutputFormat.MARKDOWN: MarkdownFormatter()
        }
    
    def generate(
        self,
        result: ScoringResult,
        format: OutputFormat = OutputFormat.HTML,
        detailed: bool = False,
        output_path: Optional[Path] = None
    ) -> str:
        """Generate report in specified format.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to generate report for.
        format : OutputFormat, optional
            Output format, by default OutputFormat.HTML.
        detailed : bool, optional
            Whether to include detailed analysis, by default False.
        output_path : Optional[Path], optional
            Path to save report to, by default None.
            
        Returns
        -------
        str
            Generated report content.
            
        Raises
        ------
        ReportGenerationError
            If report generation fails.
        """
        try:
            formatter = self.get_formatter(format)
            content = formatter.format(result, detailed)
            
            if output_path:
                self.save_report(content, output_path)
            
            return content
            
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate {format.value} report: {e}",
                format.value
            )
    
    def generate_all_formats(
        self,
        result: ScoringResult,
        output_dir: Path,
        base_filename: str = "api_quality_report",
        detailed: bool = False
    ) -> Dict[OutputFormat, Path]:
        """Generate reports in all supported formats.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to generate reports for.
        output_dir : Path
            Directory to save reports in.
        base_filename : str, optional
            Base filename for reports, by default "api_quality_report".
        detailed : bool, optional
            Whether to include detailed analysis, by default False.
            
        Returns
        -------
        Dict[OutputFormat, Path]
            Dictionary mapping formats to generated file paths.
            
        Raises
        ------
        ReportGenerationError
            If any report generation fails.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = {}
        
        for format_type, formatter in self.formatters.items():
            try:
                content = formatter.format(result, detailed)
                filename = f"{base_filename}.{formatter.get_file_extension()}"
                file_path = output_dir / filename
                
                self.save_report(content, file_path)
                generated_files[format_type] = file_path
                
            except Exception as e:
                raise ReportGenerationError(
                    f"Failed to generate {format_type.value} report: {e}",
                    format_type.value
                )
        
        return generated_files
    
    def get_formatter(self, format: OutputFormat) -> BaseFormatter:
        """Get formatter instance for specified format.
        
        Parameters
        ----------
        format : OutputFormat
            Output format to get formatter for.
            
        Returns
        -------
        BaseFormatter
            Formatter instance.
            
        Raises
        ------
        ReportGenerationError
            If formatter not found for format.
        """
        if format not in self.formatters:
            raise ReportGenerationError(
                f"No formatter available for format: {format.value}",
                format.value
            )
        
        return self.formatters[format]
    
    def save_report(self, content: str, output_path: Path) -> None:
        """Save report content to file.
        
        Parameters
        ----------
        content : str
            Report content to save.
        output_path : Path
            Path to save report to.
            
        Raises
        ------
        ReportGenerationError
            If file cannot be saved.
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to save report to {output_path}: {e}",
                str(output_path)
            )
    
    def generate_summary_report(self, result: ScoringResult) -> Dict[str, Any]:
        """Generate summary report data for API responses.
        
        Parameters
        ----------
        result : ScoringResult
            Scoring result to summarize.
            
        Returns
        -------
        Dict[str, Any]
            Summary report data.
        """
        return {
            'overall_score': result.overall_score,
            'quality_grade': result.quality_grade,
            'category_scores': {
                'documentation': result.category_scores.documentation,
                'schemas': result.category_scores.schemas,
                'errors': result.category_scores.errors,
                'usability': result.category_scores.usability,
                'authentication': result.category_scores.authentication
            },
            'issues_summary': {
                'critical': result.critical_issues_count,
                'high': result.high_issues_count,
                'total_recommendations': len(result.recommendations)
            },
            'api_info': {
                'title': result.spec_info.get('title', 'Unknown API'),
                'version': result.spec_info.get('version', '1.0.0'),
                'total_operations': result.spec_info.get('total_operations', 0)
            },
            'analysis_timestamp': result.analysis_timestamp.isoformat()
        }
    
    def generate_comparison_report(
        self,
        results: Dict[str, ScoringResult],
        format: OutputFormat = OutputFormat.HTML
    ) -> str:
        """Generate comparison report for multiple API analyses.
        
        Parameters
        ----------
        results : Dict[str, ScoringResult]
            Dictionary mapping API names to their scoring results.
        format : OutputFormat, optional
            Output format, by default OutputFormat.HTML.
            
        Returns
        -------
        str
            Generated comparison report.
            
        Raises
        ------
        ReportGenerationError
            If comparison report generation fails.
        """
        try:
            formatter = self.get_formatter(format)
            
            if format == OutputFormat.JSON:
                return self._generate_json_comparison(results)
            elif format == OutputFormat.MARKDOWN:
                return self._generate_markdown_comparison(results)
            elif format == OutputFormat.HTML:
                return self._generate_html_comparison(results)
            else:
                raise ReportGenerationError(f"Comparison not supported for format: {format.value}")
                
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate comparison report: {e}")
    
    def _generate_json_comparison(self, results: Dict[str, ScoringResult]) -> str:
        """Generate JSON comparison report.
        
        Parameters
        ----------
        results : Dict[str, ScoringResult]
            API results to compare.
            
        Returns
        -------
        str
            JSON comparison report.
        """
        import json
        
        comparison_data = {
            'comparison_timestamp': results[list(results.keys())[0]].analysis_timestamp.isoformat(),
            'apis_compared': len(results),
            'results': {}
        }
        
        for api_name, result in results.items():
            comparison_data['results'][api_name] = {
                'overall_score': result.overall_score,
                'quality_grade': result.quality_grade,
                'category_scores': {
                    'documentation': result.category_scores.documentation,
                    'schemas': result.category_scores.schemas,
                    'errors': result.category_scores.errors,
                    'usability': result.category_scores.usability,
                    'authentication': result.category_scores.authentication
                },
                'critical_issues': result.critical_issues_count,
                'high_issues': result.high_issues_count
            }
        
        return json.dumps(comparison_data, indent=2, default=str)
    
    def _generate_markdown_comparison(self, results: Dict[str, ScoringResult]) -> str:
        """Generate Markdown comparison report.
        
        Parameters
        ----------
        results : Dict[str, ScoringResult]
            API results to compare.
            
        Returns
        -------
        str
            Markdown comparison report.
        """
        lines = [
            "# API Quality Comparison Report",
            f"\n**APIs Compared**: {len(results)}",
            f"**Generated**: {list(results.values())[0].analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "\n## Overall Scores\n",
            "| API | Score | Grade | Documentation | Schemas | Errors | Usability | Auth |",
            "|-----|-------|-------|---------------|---------|--------|-----------|------|"
        ]
        
        for api_name, result in results.items():
            lines.append(
                f"| {api_name} | {result.overall_score}/100 | {result.quality_grade} | "
                f"{result.category_scores.documentation}/25 | {result.category_scores.schemas}/25 | "
                f"{result.category_scores.errors}/20 | {result.category_scores.usability}/20 | "
                f"{result.category_scores.authentication}/10 |"
            )
        
        return '\n'.join(lines)
    
    def _generate_html_comparison(self, results: Dict[str, ScoringResult]) -> str:
        """Generate HTML comparison report.
        
        Parameters
        ----------
        results : Dict[str, ScoringResult]
            API results to compare.
            
        Returns
        -------
        str
            HTML comparison report.
        """
        html_formatter = self.formatters[OutputFormat.HTML]
        
        table_rows = ""
        for api_name, result in results.items():
            grade_class = html_formatter.get_score_color(result.overall_score, 100)
            table_rows += f"""
            <tr class="{grade_class}">
                <td><strong>{api_name}</strong></td>
                <td>{result.overall_score}/100</td>
                <td>{result.quality_grade}</td>
                <td>{result.category_scores.documentation}/25</td>
                <td>{result.category_scores.schemas}/25</td>
                <td>{result.category_scores.errors}/20</td>
                <td>{result.category_scores.usability}/20</td>
                <td>{result.category_scores.authentication}/10</td>
                <td>{result.critical_issues_count}</td>
                <td>{result.high_issues_count}</td>
            </tr>"""
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>API Quality Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .success {{ background-color: #d4edda; }}
        .warning {{ background-color: #fff3cd; }}
        .danger {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <h1>API Quality Comparison Report</h1>
    <p><strong>APIs Compared:</strong> {len(results)}</p>
    <p><strong>Generated:</strong> {list(results.values())[0].analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    
    <table>
        <thead>
            <tr>
                <th>API</th>
                <th>Overall Score</th>
                <th>Grade</th>
                <th>Documentation</th>
                <th>Schemas</th>
                <th>Errors</th>
                <th>Usability</th>
                <th>Auth</th>
                <th>Critical Issues</th>
                <th>High Issues</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</body>
</html>"""