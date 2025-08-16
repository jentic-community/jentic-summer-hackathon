#!/usr/bin/env python3
"""
API Quality Scorecard - Main CLI interface
Analyzes OpenAPI specifications for agent-readiness and quality.
"""

import click
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from parser.openapi_parser import OpenAPIParser
from analyzer.quality_analyzer import QualityAnalyzer
from reporting.report_generator import ReportGenerator
from core.types import OutputFormat
from core.exceptions import ScorecardError, ParseError, ValidationError, AnalysisError
from config.settings import get_settings

@click.command()
@click.argument('spec_path')
@click.option('--output', '-o', help='Output file path for report')
@click.option('--format', '-f', 
              type=click.Choice(['html', 'json', 'markdown'], case_sensitive=False),
              default='html', 
              help='Output format for report')
@click.option('--detailed', '-d', is_flag=True, help='Generate detailed analysis')
@click.option('--quiet', '-q', is_flag=True, help='Suppress console output')
@click.option('--threshold', '-t', type=int, default=70, 
              help='Minimum score threshold (default: 70)')
def main(spec_path, output, format, detailed, quiet, threshold):
    """
    Analyze OpenAPI specification for agent-readiness and quality.
    
    SPEC_PATH can be a local file path or URL to an OpenAPI specification.
    
    Examples:
        scorecard.py api.yaml
        scorecard.py https://api.example.com/openapi.json --detailed
        scorecard.py spec.yaml --output report.html --format html
    """
    
    if not quiet:
        click.echo("🔍 API Quality Scorecard")
        click.echo("=" * 50)
        click.echo(f"Analyzing: {spec_path}")
        click.echo()
    
    try:
        # 1. Parse the OpenAPI specification
        if not quiet:
            click.echo("📖 Parsing OpenAPI specification...")
        
        parser = OpenAPIParser()
        spec = parser.load(spec_path)
        
        # 2. Analyze the specification
        if not quiet:
            click.echo("🔬 Analyzing API quality...")
        
        analyzer = QualityAnalyzer()
        results = analyzer.analyze(spec, detailed=detailed)
        
        # 3. Generate report
        if not quiet:
            click.echo("📊 Generating report...")
        
        reporter = ReportGenerator()
        output_format = OutputFormat(format.lower())
        
        if output:
            output_path = Path(output)
            report_content = reporter.generate(results, output_format, detailed, output_path)
            if not quiet:
                click.echo(f"📁 Report saved to: {output}")
        else:
            report_content = reporter.generate(results, output_format, detailed)
            if format.lower() == 'json':
                click.echo(report_content)
        
        # Display results to console
        if not quiet:
            display_results(results, threshold)
        
        # Exit with appropriate code
        score = results.overall_score
        if score < threshold:
            if not quiet:
                click.echo(f"\n⚠️  Score {score} below threshold {threshold}")
            sys.exit(1)
        else:
            if not quiet:
                click.echo(f"\n✅ Score {score} meets threshold {threshold}")
            sys.exit(0)
            
    except ParseError as e:
        click.echo(f"❌ Parse Error: {e.message}", err=True)
        if e.file_path:
            click.echo(f"   File: {e.file_path}", err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(f"❌ Validation Error: {e.message}", err=True)
        if e.validation_errors:
            click.echo("   Validation issues:", err=True)
            for error in e.validation_errors[:5]:
                click.echo(f"   - {error}", err=True)
        sys.exit(1)
    except AnalysisError as e:
        click.echo(f"❌ Analysis Error: {e.message}", err=True)
        if e.category:
            click.echo(f"   Category: {e.category}", err=True)
        sys.exit(1)
    except ScorecardError as e:
        click.echo(f"❌ Scorecard Error: {e.message}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"❌ Error: File not found: {spec_path}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if not quiet:
            click.echo("\n💡 Troubleshooting tips:")
            click.echo("  - Verify the OpenAPI specification is valid")
            click.echo("  - Check file permissions and network connectivity")
            click.echo("  - Try with a simpler specification first")
            click.echo("  - Use --detailed flag for more information")
        sys.exit(1)

def display_results(results, threshold):
    """Display analysis results to console."""
    score = results.overall_score
    
    # Overall score with color coding
    if score >= 80:
        score_color = 'green'
        score_emoji = '🟢'
    elif score >= threshold:
        score_color = 'yellow'
        score_emoji = '🟡'
    else:
        score_color = 'red'
        score_emoji = '🔴'
    
    click.echo(f"\n{score_emoji} Overall Score: ", nl=False)
    click.secho(f"{score}/100", fg=score_color, bold=True)
    
    # Category breakdown
    click.echo("\n📋 Category Scores:")
    categories = [
        ('Documentation Quality', results.category_scores.documentation, 25),
        ('Schema Completeness', results.category_scores.schemas, 25),
        ('Error Handling', results.category_scores.errors, 20),
        ('Agent Usability', results.category_scores.usability, 20),
        ('Authentication Clarity', results.category_scores.authentication, 10)
    ]
    
    for name, category_score, max_score in categories:
        percentage = int((category_score / max_score) * 100)
        
        if percentage >= 80:
            color = 'green'
        elif percentage >= 60:
            color = 'yellow'
        else:
            color = 'red'
        
        click.echo(f"  {name:25} ", nl=False)
        click.secho(f"{category_score:2}/{max_score} ({percentage:3}%)", fg=color)
    
    # Summary stats
    click.echo(f"\n📊 Analysis Summary:")
    click.echo(f"  Operations analyzed: {results.metrics.total_operations}")
    click.echo(f"  Critical issues: {results.critical_issues_count}")
    click.echo(f"  High priority issues: {results.high_issues_count}")
    click.echo(f"  Total recommendations: {len(results.recommendations)}")

def save_report(results, output_path, format):
    """Save report to file."""
    reporter = ReportGenerator()
    output_format = OutputFormat(format.lower())
    reporter.generate(results, output_format, detailed=False, output_path=Path(output_path))

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
    
    # Run CLI
    main()