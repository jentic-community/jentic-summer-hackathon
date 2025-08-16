#!/usr/bin/env python3
"""
Performance analysis and reporting script for Track 06 - Standard Agent Prompts
Analyzes test results and generates comprehensive performance reports.
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics

class PromptPerformanceAnalyzer:
    """Analyzes prompt performance data and generates reports."""
    
    def __init__(self, results_file: str = "all_prompts_results.json"):
        self.results_file = results_file
        self.results = self.load_results()
    
    def load_results(self) -> List[Dict[str, Any]]:
        """Load test results from JSON file."""
        try:
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"⚠️  Results file {self.results_file} not found.")
                print("💡 Run 'python test_all_prompts.py' first to generate results.")
                return []
        except Exception as e:
            print(f"❌ Error loading results: {e}")
            return []
    
    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze performance metrics from test results."""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        execution_times = [r['execution_time'] for r in self.results]
        successful_times = [r['execution_time'] for r in successful_results]
        
        metrics = {
            'total_prompts': len(self.results),
            'successful_prompts': len(successful_results),
            'failed_prompts': len(failed_results),
            'success_rate': len(successful_results) / len(self.results) * 100 if self.results else 0,
            'total_execution_time': sum(execution_times),
            'average_execution_time': statistics.mean(execution_times) if execution_times else 0,
            'median_execution_time': statistics.median(execution_times) if execution_times else 0,
            'min_execution_time': min(execution_times) if execution_times else 0,
            'max_execution_time': max(execution_times) if execution_times else 0,
            'successful_avg_time': statistics.mean(successful_times) if successful_times else 0,
            'failed_avg_time': statistics.mean([r['execution_time'] for r in failed_results]) if failed_results else 0
        }
        
        return metrics
    
    def categorize_prompts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize prompts by type and performance."""
        categories = {
            'fast_successful': [],  # < 10s and successful
            'medium_successful': [],  # 10-30s and successful
            'slow_successful': [],  # > 30s and successful
            'failed_quick': [],  # < 10s and failed
            'failed_slow': [],  # >= 10s and failed
            'reasoning_prompts': [],  # Prompts that don't require external APIs
            'api_dependent': []  # Prompts that tried to use external APIs
        }
        
        for result in self.results:
            time = result['execution_time']
            success = result['success']
            
            # Performance categories
            if success:
                if time < 10:
                    categories['fast_successful'].append(result)
                elif time < 30:
                    categories['medium_successful'].append(result)
                else:
                    categories['slow_successful'].append(result)
            else:
                if time < 10:
                    categories['failed_quick'].append(result)
                else:
                    categories['failed_slow'].append(result)
            
            # Content categories
            error_msg = result.get('error', '').lower()
            if 'credential' in error_msg or 'unauthorized' in error_msg or 'api' in error_msg:
                categories['api_dependent'].append(result)
            else:
                categories['reasoning_prompts'].append(result)
        
        return categories
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        if not self.results:
            return "No results available for analysis."
        
        metrics = self.analyze_performance_metrics()
        categories = self.categorize_prompts()
        
        report = []
        report.append("📊 STANDARD AGENT PROMPTS - PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("🎯 EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Prompts Tested: {metrics['total_prompts']}")
        report.append(f"Success Rate: {metrics['success_rate']:.1f}%")
        report.append(f"Average Execution Time: {metrics['average_execution_time']:.2f}s")
        report.append(f"Total Testing Time: {metrics['total_execution_time']:.2f}s")
        report.append("")
        
        # Performance Metrics
        report.append("⚡ PERFORMANCE METRICS")
        report.append("-" * 40)
        report.append(f"Fastest Prompt: {metrics['min_execution_time']:.2f}s")
        report.append(f"Slowest Prompt: {metrics['max_execution_time']:.2f}s")
        report.append(f"Median Time: {metrics['median_execution_time']:.2f}s")
        report.append(f"Successful Prompts Avg: {metrics['successful_avg_time']:.2f}s")
        if metrics['failed_avg_time'] > 0:
            report.append(f"Failed Prompts Avg: {metrics['failed_avg_time']:.2f}s")
        report.append("")
        
        # Success Analysis
        report.append("✅ SUCCESS ANALYSIS")
        report.append("-" * 40)
        report.append(f"Successful Prompts: {metrics['successful_prompts']}/{metrics['total_prompts']}")
        report.append(f"Fast Successful (< 10s): {len(categories['fast_successful'])}")
        report.append(f"Medium Successful (10-30s): {len(categories['medium_successful'])}")
        report.append(f"Slow Successful (> 30s): {len(categories['slow_successful'])}")
        report.append("")
        
        # Failure Analysis
        if metrics['failed_prompts'] > 0:
            report.append("❌ FAILURE ANALYSIS")
            report.append("-" * 40)
            report.append(f"Failed Prompts: {metrics['failed_prompts']}/{metrics['total_prompts']}")
            report.append(f"Quick Failures (< 10s): {len(categories['failed_quick'])}")
            report.append(f"Slow Failures (>= 10s): {len(categories['failed_slow'])}")
            report.append(f"API-Related Failures: {len(categories['api_dependent'])}")
            report.append("")
        
        # Prompt Categories
        report.append("📂 PROMPT CATEGORIES")
        report.append("-" * 40)
        report.append(f"Reasoning-Based Prompts: {len(categories['reasoning_prompts'])}")
        report.append(f"API-Dependent Prompts: {len(categories['api_dependent'])}")
        report.append("")
        
        # Top Performing Prompts
        if categories['fast_successful']:
            report.append("🏆 TOP PERFORMING PROMPTS (Fast & Successful)")
            report.append("-" * 40)
            for i, result in enumerate(categories['fast_successful'][:5], 1):
                report.append(f"{i}. {result['prompt'][:60]}... ({result['execution_time']:.2f}s)")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if metrics['success_rate'] >= 80:
            report.append("✅ Excellent success rate! Your prompt collection is ready for submission.")
        elif metrics['success_rate'] >= 60:
            report.append("⚠️  Good success rate, but consider optimizing failed prompts.")
        else:
            report.append("❌ Low success rate. Focus on simpler, reasoning-based prompts.")
        
        if metrics['average_execution_time'] < 15:
            report.append("✅ Good performance - prompts execute quickly.")
        elif metrics['average_execution_time'] < 30:
            report.append("⚠️  Moderate performance - consider optimizing slower prompts.")
        else:
            report.append("❌ Slow performance - focus on simpler prompts or better API access.")
        
        if len(categories['reasoning_prompts']) >= 5:
            report.append("✅ Good mix of reasoning-based prompts that don't require external APIs.")
        else:
            report.append("💡 Consider adding more reasoning-based prompts for reliability.")
        
        report.append("")
        report.append("🎯 SUBMISSION READINESS")
        report.append("-" * 40)
        
        mvp_ready = metrics['successful_prompts'] >= 5
        enhanced_ready = metrics['successful_prompts'] >= 10
        
        if enhanced_ready:
            report.append("🎉 READY FOR ENHANCED SUBMISSION!")
            report.append("   ✅ 10+ successful prompts")
            report.append("   ✅ Comprehensive test coverage")
        elif mvp_ready:
            report.append("✅ READY FOR MVP SUBMISSION!")
            report.append("   ✅ 5+ successful prompts")
            report.append("   💡 Add more prompts for enhanced submission")
        else:
            report.append("⚠️  NOT READY FOR SUBMISSION")
            report.append(f"   ❌ Need {5 - metrics['successful_prompts']} more successful prompts")
            report.append("   💡 Focus on reasoning-based prompts")
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: str = "performance_report.txt") -> None:
        """Save the performance report to a file."""
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"📁 Performance report saved to {filename}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
    
    def generate_json_summary(self) -> Dict[str, Any]:
        """Generate a JSON summary for programmatic use."""
        metrics = self.analyze_performance_metrics()
        categories = self.categorize_prompts()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'categories': {k: len(v) for k, v in categories.items()},
            'submission_ready': {
                'mvp': metrics['successful_prompts'] >= 5,
                'enhanced': metrics['successful_prompts'] >= 10,
                'successful_prompts': metrics['successful_prompts']
            },
            'top_prompts': [
                {
                    'prompt': r['prompt'][:100],
                    'execution_time': r['execution_time'],
                    'success': r['success']
                }
                for r in sorted(self.results, key=lambda x: (x['success'], -x['execution_time']))[:10]
            ]
        }
        
        return summary

def main():
    """Main function to generate performance reports."""
    print("📊 Generating Standard Agent Prompts Performance Report...")
    print()
    
    analyzer = PromptPerformanceAnalyzer()
    
    if not analyzer.results:
        print("❌ No results found. Please run 'python test_all_prompts.py' first.")
        return
    
    # Generate and display report
    report = analyzer.generate_performance_report()
    print(report)
    
    # Save report to file
    analyzer.save_report(report)
    
    # Generate JSON summary
    summary = analyzer.generate_json_summary()
    try:
        with open("performance_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        print("📁 JSON summary saved to performance_summary.json")
    except Exception as e:
        print(f"⚠️  Could not save JSON summary: {e}")
    
    print()
    print("🎉 Performance analysis complete!")

if __name__ == "__main__":
    main()