#!/usr/bin/env python3
"""
Advanced API Analytics CLI - Phase 4
Sophisticated analysis and intelligence features for OpenAPI optimization.
"""

import argparse
import sys
import json
import yaml
import time
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.tree import Tree
from rich.markdown import Markdown

from minifier.parser import OpenAPIParser
from minifier.analytics_engine import APIAnalyticsEngine, APIComplexityMetrics, OptimizationRecommendation

console = Console()


def main():
    """Advanced analytics CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Advanced OpenAPI Analytics and Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Comprehensive API health analysis
  python analyze.py --input api.yaml --health-report --output health-report.json
  
  # Performance benchmarking
  python analyze.py --input api.yaml --benchmark --operations createTask,updateTask
  
  # Compare API versions
  python analyze.py --compare old-api.yaml new-api.yaml --output comparison.json
  
  # Generate optimization recommendations
  python analyze.py --input api.yaml --recommendations --priority high --format markdown
  
  # Intelligence dashboard
  python analyze.py --input api.yaml --dashboard --auto-refresh 30
        """
    )
    
    # Input options
    parser.add_argument("--input", "-i", 
                       help="Input OpenAPI specification file")
    parser.add_argument("--compare", nargs=2, metavar=("OLD", "NEW"),
                       help="Compare two API versions")
    
    # Analysis modes
    parser.add_argument("--health-report", action="store_true",
                       help="Generate comprehensive API health report")
    parser.add_argument("--complexity", action="store_true",
                       help="Analyze API complexity metrics")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run performance benchmarks")
    parser.add_argument("--recommendations", action="store_true",
                       help="Generate optimization recommendations")
    parser.add_argument("--dashboard", action="store_true",
                       help="Interactive analytics dashboard")
    
    # Filtering options
    parser.add_argument("--operations",
                       help="Comma-separated operations for focused analysis")
    parser.add_argument("--priority", choices=["critical", "high", "medium", "low"],
                       help="Filter recommendations by priority")
    parser.add_argument("--category",
                       help="Filter recommendations by category")
    
    # Output options
    parser.add_argument("--output", "-o",
                       help="Output file for results")
    parser.add_argument("--format", choices=["json", "yaml", "markdown", "table"],
                       default="table", help="Output format")
    parser.add_argument("--auto-refresh", type=int,
                       help="Auto-refresh interval for dashboard (seconds)")
    
    # Advanced options
    parser.add_argument("--cache", action="store_true",
                       help="Enable analysis caching for performance")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--export-metrics", 
                       help="Export metrics to file for trend analysis")
    
    args = parser.parse_args()
    
    if args.compare:
        return handle_comparison(args)
    elif args.dashboard:
        return handle_dashboard(args)
    else:
        return handle_analysis(args)


def handle_analysis(args) -> int:
    """Handle single API analysis."""
    if not args.input:
        console.print("❌ Error: --input required for analysis", style="red")
        return 1
    
    try:
        with console.status("Loading API specification..."):
            parser = OpenAPIParser()
            spec = parser.load(args.input)
            analytics = APIAnalyticsEngine(parser)
        
        results = {}
        
        if args.complexity or args.health_report:
            with console.status("Analyzing API complexity..."):
                complexity_metrics = analytics.analyze_api_complexity(spec)
                results['complexity'] = complexity_metrics
                
                if not args.health_report:
                    display_complexity_analysis(complexity_metrics)
        
        if args.benchmark:
            operations = args.operations.split(',') if args.operations else list(spec.get('paths', {}).keys())[:5]
            with console.status("Running performance benchmarks..."):
                benchmark = analytics.benchmark_performance(spec, operations)
                results['benchmark'] = benchmark
                display_benchmark_results(benchmark)
        
        if args.recommendations or args.health_report:
            with console.status("Generating intelligent recommendations..."):
                if 'complexity' not in results:
                    complexity_metrics = analytics.analyze_api_complexity(spec)
                    results['complexity'] = complexity_metrics
                
                recommendations = analytics.generate_intelligent_recommendations(spec, results['complexity'])
                
                # Filter recommendations
                if args.priority:
                    recommendations = [r for r in recommendations if r.priority == args.priority]
                if args.category:
                    recommendations = [r for r in recommendations if r.category.lower() == args.category.lower()]
                
                results['recommendations'] = recommendations
                
                if not args.health_report:
                    display_recommendations(recommendations)
        
        if args.health_report:
            with console.status("Generating comprehensive health report..."):
                health_report = analytics.generate_api_health_report(spec)
                results['health_report'] = health_report
                display_health_report(health_report)
        
        # Export results
        if args.output:
            export_results(results, args.output, args.format)
        
        if args.export_metrics:
            export_metrics_for_trending(results, args.export_metrics)
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_comparison(args) -> int:
    """Handle API version comparison."""
    try:
        with console.status("Loading API specifications..."):
            parser = OpenAPIParser()
            old_spec = parser.load(args.compare[0])
            new_spec = parser.load(args.compare[1])
            analytics = APIAnalyticsEngine(parser)
        
        with console.status("Comparing API versions..."):
            comparison = analytics.compare_api_versions(old_spec, new_spec)
        
        display_version_comparison(comparison, args.compare[0], args.compare[1])
        
        if args.output:
            export_results({'comparison': comparison}, args.output, args.format)
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        return 1


def handle_dashboard(args) -> int:
    """Handle interactive analytics dashboard."""
    if not args.input:
        console.print("❌ Error: --input required for dashboard", style="red")
        return 1
    
    try:
        parser = OpenAPIParser()
        spec = parser.load(args.input)
        analytics = APIAnalyticsEngine(parser)
        
        if args.auto_refresh:
            # Auto-refreshing dashboard
            while True:
                console.clear()
                display_dashboard(analytics, spec, args.input)
                time.sleep(args.auto_refresh)
        else:
            # Static dashboard
            display_dashboard(analytics, spec, args.input)
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n👋 Dashboard closed by user", style="yellow")
        return 0
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        return 1


def display_complexity_analysis(metrics: APIComplexityMetrics):
    """Display complexity analysis results."""
    
    # Create complexity overview table
    table = Table(title="🔍 API Complexity Analysis", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Assessment", style="green")
    
    # Basic metrics
    table.add_row("Total Operations", str(metrics.total_operations), get_assessment(metrics.total_operations, [50, 100, 200]))
    table.add_row("Total Schemas", str(metrics.total_schemas), get_assessment(metrics.total_schemas, [20, 50, 100]))
    table.add_row("Total Dependencies", str(metrics.total_dependencies), get_assessment(metrics.total_dependencies, [50, 150, 300]))
    table.add_row("Circular Dependencies", str(metrics.circular_dependencies), "❌ Critical" if metrics.circular_dependencies > 0 else "✅ Good")
    
    # Complexity scores
    table.add_row("Schema Complexity", f"{metrics.schema_complexity_score:.2f}", get_score_assessment(metrics.schema_complexity_score))
    table.add_row("Operation Complexity", f"{metrics.operation_complexity_score:.2f}", get_score_assessment(metrics.operation_complexity_score))
    table.add_row("Overall Complexity", f"{metrics.overall_complexity_score:.2f}", get_score_assessment(metrics.overall_complexity_score))
    table.add_row("Optimization Potential", f"{metrics.optimization_potential:.1f}%", get_percentage_assessment(metrics.optimization_potential))
    
    console.print(table)
    
    # Display hotspots and issues
    if metrics.hotspot_operations:
        console.print(f"\n🔥 Hotspot Operations: {', '.join(metrics.hotspot_operations[:5])}")
    
    if metrics.unused_schemas:
        console.print(f"\n♻️  Unused Schemas ({len(metrics.unused_schemas)}): {', '.join(metrics.unused_schemas[:5])}")
    
    if metrics.oversized_schemas:
        console.print(f"\n📏 Oversized Schemas ({len(metrics.oversized_schemas)}): {', '.join(metrics.oversized_schemas[:5])}")


def display_benchmark_results(benchmark):
    """Display performance benchmark results."""
    
    table = Table(title="⚡ Performance Benchmark Results", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Performance", style="green")
    
    # File and memory metrics
    table.add_row("Spec Size", f"{benchmark.spec_size_bytes:,} bytes", get_size_assessment(benchmark.spec_size_bytes))
    table.add_row("Memory Usage", f"{benchmark.memory_usage_mb:.1f} MB", get_memory_assessment(benchmark.memory_usage_mb))
    
    # Timing metrics
    table.add_row("Load Time", f"{benchmark.load_time_ms:.1f} ms", get_time_assessment(benchmark.load_time_ms))
    table.add_row("Parse Time", f"{benchmark.parse_time_ms:.1f} ms", get_time_assessment(benchmark.parse_time_ms))
    table.add_row("Dependency Resolution", f"{benchmark.dependency_resolution_time_ms:.1f} ms", get_time_assessment(benchmark.dependency_resolution_time_ms))
    table.add_row("Minification Time", f"{benchmark.minification_time_ms:.1f} ms", get_time_assessment(benchmark.minification_time_ms))
    
    # Throughput metrics
    table.add_row("Operations/Second", f"{benchmark.operations_per_second:.1f}", "🚀 High" if benchmark.operations_per_second > 100 else "🐌 Low")
    table.add_row("Schemas/Second", f"{benchmark.schemas_per_second:.1f}", "🚀 High" if benchmark.schemas_per_second > 50 else "🐌 Low")
    
    console.print(table)


def display_recommendations(recommendations: List[OptimizationRecommendation]):
    """Display optimization recommendations."""
    
    if not recommendations:
        console.print("✅ No optimization recommendations - API is well optimized!", style="green")
        return
    
    # Group by priority
    by_priority = {}
    for rec in recommendations:
        if rec.priority not in by_priority:
            by_priority[rec.priority] = []
        by_priority[rec.priority].append(rec)
    
    for priority in ['critical', 'high', 'medium', 'low']:
        if priority in by_priority:
            priority_style = {
                'critical': 'red',
                'high': 'orange1', 
                'medium': 'yellow',
                'low': 'cyan'
            }[priority]
            
            console.print(f"\n{priority.upper()} Priority Recommendations", style=f"bold {priority_style}")
            
            for i, rec in enumerate(by_priority[priority], 1):
                panel_content = f"""
**Issue**: {rec.issue}
**Impact**: {rec.impact}
**Recommendation**: {rec.recommendation}
**Estimated Savings**: {rec.estimated_savings:.1f}%
**Difficulty**: {rec.implementation_difficulty}

**CLI Commands**:
```bash
{chr(10).join(rec.cli_commands)}
```
                """.strip()
                
                console.print(Panel(
                    Markdown(panel_content),
                    title=f"{priority.upper()}-{i}: {rec.category}",
                    border_style=priority_style
                ))


def display_health_report(health_report: Dict[str, Any]):
    """Display comprehensive API health report."""
    
    # Overall health score
    overall_score = health_report['overall_health_score']
    health_color = "green" if overall_score >= 80 else "yellow" if overall_score >= 60 else "red"
    
    console.print(Panel(
        f"Overall API Health Score: {overall_score}/100",
        title="🏥 API Health Dashboard",
        border_style=health_color
    ))
    
    # Health breakdown
    table = Table(title="Health Breakdown", show_header=True, header_style="bold cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Score", style="white")
    table.add_column("Status", style="green")
    
    for category, score in health_report['health_breakdown'].items():
        status = "🟢 Excellent" if score >= 90 else "🟡 Good" if score >= 70 else "🟠 Fair" if score >= 50 else "🔴 Poor"
        table.add_row(category.replace('_', ' ').title(), f"{score:.1f}/100", status)
    
    console.print(table)
    
    # API Statistics
    stats = health_report['api_statistics']
    console.print(f"\n📊 API Statistics:")
    console.print(f"   • {stats['total_endpoints']} endpoints, {stats['total_schemas']} schemas")
    console.print(f"   • Dependency ratio: {stats['dependency_ratio']:.2f}")
    console.print(f"   • Optimization potential: {stats['optimization_potential_percentage']}%")
    
    # Improvement roadmap
    roadmap = health_report['improvement_roadmap']
    if any(roadmap.values()):
        console.print("\n🗺️  Improvement Roadmap:")
        
        if roadmap['immediate']:
            console.print("   🚨 Immediate Actions:", style="red")
            for action in roadmap['immediate']:
                console.print(f"     • {action}")
        
        if roadmap['short_term']:
            console.print("   ⏱️  Short-term Actions:", style="yellow")
            for action in roadmap['short_term']:
                console.print(f"     • {action}")
        
        if roadmap['long_term']:
            console.print("   📅 Long-term Actions:", style="cyan")
            for action in roadmap['long_term']:
                console.print(f"     • {action}")


def display_version_comparison(comparison: Dict[str, Any], old_file: str, new_file: str):
    """Display API version comparison results."""
    
    console.print(Panel(
        f"Comparing: {old_file} → {new_file}",
        title="🔄 API Version Comparison",
        border_style="blue"
    ))
    
    # Operations comparison
    ops = comparison['operations']
    table = Table(title="Operations Changes", show_header=True, header_style="bold green")
    table.add_column("Change Type", style="cyan")
    table.add_column("Count", style="white")
    table.add_column("Details", style="yellow")
    
    table.add_row("Added", str(len(ops['added'])), ', '.join(ops['added'][:3]) + ('...' if len(ops['added']) > 3 else ''))
    table.add_row("Removed", str(len(ops['removed'])), ', '.join(ops['removed'][:3]) + ('...' if len(ops['removed']) > 3 else ''))
    table.add_row("Unchanged", str(ops['unchanged']), f"{ops['total_old']} → {ops['total_new']} total")
    
    console.print(table)
    
    # Schemas comparison
    schemas = comparison['schemas'] 
    table = Table(title="Schema Changes", show_header=True, header_style="bold purple")
    table.add_column("Change Type", style="cyan")
    table.add_column("Count", style="white")
    table.add_column("Details", style="yellow")
    
    table.add_row("Added", str(len(schemas['added'])), ', '.join(schemas['added'][:3]) + ('...' if len(schemas['added']) > 3 else ''))
    table.add_row("Removed", str(len(schemas['removed'])), ', '.join(schemas['removed'][:3]) + ('...' if len(schemas['removed']) > 3 else ''))
    table.add_row("Unchanged", str(schemas['unchanged']), f"{schemas['total_old']} → {schemas['total_new']} total")
    
    console.print(table)
    
    # Complexity changes
    complexity = comparison['complexity']
    console.print(f"\n📈 Complexity Analysis:")
    console.print(f"   • Old complexity score: {complexity['old_score']:.2f}")
    console.print(f"   • New complexity score: {complexity['new_score']:.2f}")
    console.print(f"   • Change: {complexity['delta']:+.2f} ({complexity['trend']})")
    
    # Summary
    summary = comparison['summary']
    console.print(f"\n📋 Summary:")
    console.print(f"   • Breaking changes: {summary['breaking_changes']}")
    console.print(f"   • New features: {summary['new_features']}")
    console.print(f"   • Stability score: {summary['stability_score']:.2f}")


def display_dashboard(analytics: APIAnalyticsEngine, spec: Dict[str, Any], spec_file: str):
    """Display interactive analytics dashboard."""
    
    console.print(Panel(
        f"API: {spec_file} | Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        title="📊 OpenAPI Analytics Dashboard",
        border_style="bright_blue"
    ))
    
    # Quick stats
    operations = spec.get('paths', {})
    schemas = spec.get('components', {}).get('schemas', {})
    total_ops = sum(len([m for m in path_methods.keys() if m.lower() in ['get', 'post', 'put', 'delete', 'patch']]) 
                   for path_methods in operations.values())
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column(style="cyan", width=20)
    stats_table.add_column(style="white", width=15)
    stats_table.add_column(style="cyan", width=20)
    stats_table.add_column(style="white", width=15)
    
    stats_table.add_row("📋 Total Operations", str(total_ops), "🏗️  Total Schemas", str(len(schemas)))
    stats_table.add_row("📊 API Paths", str(len(operations)), "🔗 Dependencies", "Analyzing...")
    
    console.print(stats_table)
    
    # Real-time analysis
    with Progress() as progress:
        task1 = progress.add_task("Analyzing complexity...", total=100)
        complexity_metrics = analytics.analyze_api_complexity(spec)
        progress.update(task1, completed=100)
        
        task2 = progress.add_task("Generating recommendations...", total=100)
        recommendations = analytics.generate_intelligent_recommendations(spec, complexity_metrics)
        progress.update(task2, completed=100)
    
    # Display key metrics
    console.print(f"\n🎯 Key Metrics:")
    console.print(f"   • Overall complexity: {complexity_metrics.overall_complexity_score:.2f}/1.0")
    console.print(f"   • Optimization potential: {complexity_metrics.optimization_potential:.1f}%")
    console.print(f"   • Critical recommendations: {len([r for r in recommendations if r.priority == 'critical'])}")
    
    # Top recommendations
    critical_recs = [r for r in recommendations if r.priority == 'critical'][:3]
    if critical_recs:
        console.print("\n🚨 Critical Issues:")
        for i, rec in enumerate(critical_recs, 1):
            console.print(f"   {i}. {rec.issue}: {rec.recommendation}")


def export_results(results: Dict[str, Any], output_file: str, format_type: str):
    """Export analysis results to file."""
    
    output_path = Path(output_file)
    
    # Convert dataclass objects to dictionaries
    serializable_results = {}
    for key, value in results.items():
        if hasattr(value, '__dict__'):
            # Convert dataclass to dict
            from dataclasses import asdict
            serializable_results[key] = asdict(value)
        elif isinstance(value, list) and value and hasattr(value[0], '__dict__'):
            # Convert list of dataclasses to list of dicts
            from dataclasses import asdict
            serializable_results[key] = [asdict(item) for item in value]
        else:
            serializable_results[key] = value
    
    try:
        if format_type == 'json':
            with open(output_path, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
        elif format_type == 'yaml':
            with open(output_path, 'w') as f:
                yaml.dump(serializable_results, f, default_flow_style=False)
        elif format_type == 'markdown':
            generate_markdown_report(serializable_results, output_path)
        
        console.print(f"✅ Results exported to {output_file}", style="green")
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}", style="red")


def generate_markdown_report(results: Dict[str, Any], output_path: Path):
    """Generate markdown report from analysis results."""
    
    md_content = ["# OpenAPI Analysis Report", ""]
    md_content.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append("")
    
    if 'complexity' in results:
        complexity = results['complexity']
        md_content.extend([
            "## Complexity Analysis",
            "",
            f"- **Total Operations**: {complexity['total_operations']}",
            f"- **Total Schemas**: {complexity['total_schemas']}",
            f"- **Overall Complexity**: {complexity['overall_complexity_score']:.2f}",
            f"- **Optimization Potential**: {complexity['optimization_potential']:.1f}%",
            ""
        ])
    
    if 'recommendations' in results:
        md_content.extend(["## Recommendations", ""])
        for rec in results['recommendations']:
            md_content.extend([
                f"### {rec['priority'].upper()}: {rec['category']}",
                f"**Issue**: {rec['issue']}",
                f"**Recommendation**: {rec['recommendation']}",
                f"**Estimated Savings**: {rec['estimated_savings']:.1f}%",
                ""
            ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(md_content))


def export_metrics_for_trending(results: Dict[str, Any], export_file: str):
    """Export metrics in format suitable for trend analysis."""
    
    metrics_entry = {
        'timestamp': time.time(),
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    if 'complexity' in results:
        complexity = results['complexity']
        metrics_entry.update({
            'total_operations': complexity['total_operations'],
            'total_schemas': complexity['total_schemas'],
            'complexity_score': complexity['overall_complexity_score'],
            'optimization_potential': complexity['optimization_potential']
        })
    
    if 'benchmark' in results:
        benchmark = results['benchmark']
        metrics_entry.update({
            'load_time_ms': benchmark['load_time_ms'],
            'memory_usage_mb': benchmark['memory_usage_mb'],
            'spec_size_bytes': benchmark['spec_size_bytes']
        })
    
    # Append to existing file or create new
    export_path = Path(export_file)
    if export_path.exists():
        with open(export_path, 'r') as f:
            existing_data = json.load(f)
        existing_data.append(metrics_entry)
    else:
        existing_data = [metrics_entry]
    
    with open(export_path, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    console.print(f"📈 Metrics exported to {export_file}", style="green")


def get_assessment(value: int, thresholds: List[int]) -> str:
    """Get assessment based on thresholds."""
    if value <= thresholds[0]:
        return "🟢 Good"
    elif value <= thresholds[1]:
        return "🟡 Moderate"
    elif value <= thresholds[2]:
        return "🟠 High"
    else:
        return "🔴 Very High"


def get_score_assessment(score: float) -> str:
    """Get assessment for complexity scores (0-1)."""
    if score <= 0.3:
        return "🟢 Low"
    elif score <= 0.6:
        return "🟡 Moderate"
    elif score <= 0.8:
        return "🟠 High"
    else:
        return "🔴 Very High"


def get_percentage_assessment(percentage: float) -> str:
    """Get assessment for percentage values."""
    if percentage <= 20:
        return "🟢 Low"
    elif percentage <= 50:
        return "🟡 Moderate"
    elif percentage <= 80:
        return "🟠 High"
    else:
        return "🔴 Very High"


def get_size_assessment(size_bytes: int) -> str:
    """Get assessment for file sizes."""
    size_mb = size_bytes / (1024 * 1024)
    if size_mb <= 1:
        return "🟢 Small"
    elif size_mb <= 5:
        return "🟡 Medium"
    elif size_mb <= 10:
        return "🟠 Large"
    else:
        return "🔴 Very Large"


def get_memory_assessment(memory_mb: float) -> str:
    """Get assessment for memory usage."""
    if memory_mb <= 50:
        return "🟢 Low"
    elif memory_mb <= 200:
        return "🟡 Moderate"
    elif memory_mb <= 500:
        return "🟠 High"
    else:
        return "🔴 Very High"


def get_time_assessment(time_ms: float) -> str:
    """Get assessment for timing metrics."""
    if time_ms <= 100:
        return "🟢 Fast"
    elif time_ms <= 500:
        return "🟡 Moderate"
    elif time_ms <= 2000:
        return "🟠 Slow"
    else:
        return "🔴 Very Slow"


if __name__ == "__main__":
    sys.exit(main())