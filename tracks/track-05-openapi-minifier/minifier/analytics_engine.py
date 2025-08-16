"""
Advanced Analytics Engine - Phase 4
Sophisticated analysis and intelligence features for OpenAPI optimization.
"""

import networkx as nx
import json
import yaml
import time
import statistics
from typing import Dict, Any, List, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib
import logging

from .parser import OpenAPIParser
from .dependency_analyzer import AdvancedDependencyAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class APIComplexityMetrics:
    """Comprehensive API complexity analysis."""
    total_operations: int
    total_schemas: int
    total_dependencies: int
    circular_dependencies: int
    max_dependency_depth: int
    avg_dependency_depth: float
    schema_complexity_score: float
    operation_complexity_score: float
    overall_complexity_score: float
    optimization_potential: float
    hotspot_operations: List[str]
    unused_schemas: List[str]
    oversized_schemas: List[str]


@dataclass
class OptimizationRecommendation:
    """Intelligent optimization recommendation."""
    category: str
    priority: str  # critical, high, medium, low
    operation_id: Optional[str]
    schema_name: Optional[str]
    issue: str
    impact: str
    recommendation: str
    estimated_savings: float
    implementation_difficulty: str
    cli_commands: List[str]


@dataclass
class PerformanceBenchmark:
    """Performance benchmark results."""
    spec_size_bytes: int
    load_time_ms: float
    parse_time_ms: float
    dependency_resolution_time_ms: float
    minification_time_ms: float
    memory_usage_mb: float
    operations_per_second: float
    schemas_per_second: float


class APIAnalyticsEngine:
    """Advanced analytics engine for deep OpenAPI analysis."""
    
    def __init__(self, parser: OpenAPIParser):
        self.parser = parser
        self.dependency_analyzer = AdvancedDependencyAnalyzer(parser)
        self.analysis_cache = {}
        self.benchmark_history = []
        
    def analyze_api_complexity(self, spec: Dict[str, Any]) -> APIComplexityMetrics:
        """Perform comprehensive API complexity analysis."""
        
        print("🔍 Analyzing API complexity...")
        
        # Basic metrics
        operations = spec.get('paths', {})
        schemas = spec.get('components', {}).get('schemas', {})
        
        total_operations = sum(len([m for m in path_methods.keys() 
                                  if m.lower() in ['get', 'post', 'put', 'delete', 'patch']]) 
                             for path_methods in operations.values())
        total_schemas = len(schemas)
        
        # Build dependency graph for analysis
        self.dependency_analyzer.build_complete_dependency_graph(spec)
        graph_analysis = self.dependency_analyzer.dependency_graph.analyze_schema_relationships()
        
        # Dependency metrics
        total_dependencies = graph_analysis['total_dependencies']
        circular_dependencies = graph_analysis['circular_dependencies']
        
        # Calculate dependency depths
        dependency_depths = self._calculate_dependency_depths(spec)
        max_depth = max(dependency_depths.values()) if dependency_depths else 0
        avg_depth = statistics.mean(dependency_depths.values()) if dependency_depths else 0
        
        # Complexity scores
        schema_complexity = self._calculate_schema_complexity(schemas)
        operation_complexity = self._calculate_operation_complexity(operations)
        overall_complexity = (schema_complexity + operation_complexity) / 2
        
        # Optimization analysis
        optimization_potential = self._calculate_optimization_potential(spec)
        hotspot_operations = self._identify_hotspot_operations(spec)
        unused_schemas = self._find_unused_schemas(spec)
        oversized_schemas = self._find_oversized_schemas(schemas)
        
        return APIComplexityMetrics(
            total_operations=total_operations,
            total_schemas=total_schemas,
            total_dependencies=total_dependencies,
            circular_dependencies=circular_dependencies,
            max_dependency_depth=max_depth,
            avg_dependency_depth=avg_depth,
            schema_complexity_score=schema_complexity,
            operation_complexity_score=operation_complexity,
            overall_complexity_score=overall_complexity,
            optimization_potential=optimization_potential,
            hotspot_operations=hotspot_operations,
            unused_schemas=unused_schemas,
            oversized_schemas=oversized_schemas
        )
    
    def generate_intelligent_recommendations(self, spec: Dict[str, Any], 
                                          complexity_metrics: APIComplexityMetrics) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations using ML-like analysis."""
        
        print("💡 Generating intelligent recommendations...")
        recommendations = []
        
        # Critical recommendations
        if complexity_metrics.circular_dependencies > 0:
            recommendations.append(OptimizationRecommendation(
                category="Schema Design",
                priority="critical",
                operation_id=None,
                schema_name=None,
                issue=f"Circular dependencies detected ({complexity_metrics.circular_dependencies})",
                impact="Can cause infinite loops in processing",
                recommendation="Refactor schemas to eliminate circular references",
                estimated_savings=15.0,
                implementation_difficulty="high",
                cli_commands=[
                    "python minify.py --input api.yaml --operations all --circular-check --optimize-allof --output fixed-api.yaml"
                ]
            ))
        
        # High priority recommendations
        if complexity_metrics.unused_schemas:
            savings = len(complexity_metrics.unused_schemas) / complexity_metrics.total_schemas * 100
            recommendations.append(OptimizationRecommendation(
                category="Schema Cleanup",
                priority="high",
                operation_id=None,
                schema_name=None,
                issue=f"{len(complexity_metrics.unused_schemas)} unused schemas detected",
                impact=f"Wasting {savings:.1f}% of schema space",
                recommendation="Remove unused schemas to reduce API size",
                estimated_savings=savings,
                implementation_difficulty="low",
                cli_commands=[
                    f"# Remove unused schemas: {', '.join(complexity_metrics.unused_schemas[:5])}",
                    "python minify.py --input api.yaml --operations all --strip-unused --output cleaned-api.yaml"
                ]
            ))
        
        # Operation-specific recommendations
        for operation_id in complexity_metrics.hotspot_operations[:3]:
            recommendations.append(OptimizationRecommendation(
                category="Operation Optimization",
                priority="medium",
                operation_id=operation_id,
                schema_name=None,
                issue=f"High complexity operation: {operation_id}",
                impact="Heavy operation affecting performance",
                recommendation="Consider splitting into smaller operations or optimizing schemas",
                estimated_savings=10.0,
                implementation_difficulty="medium",
                cli_commands=[
                    f"python minify.py --input api.yaml --operations {operation_id} --optimize-for speed --output optimized-{operation_id}.yaml"
                ]
            ))
        
        # Schema-specific recommendations
        for schema_name in complexity_metrics.oversized_schemas[:3]:
            recommendations.append(OptimizationRecommendation(
                category="Schema Optimization",
                priority="medium",
                operation_id=None,
                schema_name=schema_name,
                issue=f"Oversized schema: {schema_name}",
                impact="Large schema affecting minification efficiency",
                recommendation="Consider breaking into smaller, focused schemas",
                estimated_savings=8.0,
                implementation_difficulty="medium",
                cli_commands=[
                    f"python minify.py --input api.yaml --operations all --strip-unused-properties --output optimized-schemas.yaml"
                ]
            ))
        
        # Performance recommendations
        if complexity_metrics.overall_complexity_score > 0.8:
            recommendations.append(OptimizationRecommendation(
                category="Performance",
                priority="high",
                operation_id=None,
                schema_name=None,
                issue="High overall API complexity",
                impact="Slow agent performance and high resource usage",
                recommendation="Apply aggressive optimization strategies",
                estimated_savings=25.0,
                implementation_difficulty="low",
                cli_commands=[
                    "python minify.py --input api.yaml --operations all --optimize-for size --no-examples --no-descriptions --output performance-optimized.yaml"
                ]
            ))
        
        return sorted(recommendations, key=lambda r: self._priority_score(r.priority), reverse=True)
    
    def benchmark_performance(self, spec: Dict[str, Any], operations: List[str]) -> PerformanceBenchmark:
        """Comprehensive performance benchmarking."""
        
        print("⚡ Running performance benchmarks...")
        
        # Measure spec size
        spec_json = json.dumps(spec, separators=(',', ':'))
        spec_size = len(spec_json.encode('utf-8'))
        
        # Benchmark loading
        start_time = time.perf_counter()
        self.parser.spec = spec
        load_time = (time.perf_counter() - start_time) * 1000
        
        # Benchmark parsing
        start_time = time.perf_counter()
        all_operations = self.parser.get_operations()
        parse_time = (time.perf_counter() - start_time) * 1000
        
        # Benchmark dependency resolution
        start_time = time.perf_counter()
        self.dependency_analyzer.build_complete_dependency_graph(spec)
        dependency_time = (time.perf_counter() - start_time) * 1000
        
        # Benchmark minification (simulation)
        start_time = time.perf_counter()
        for op_id in operations[:10]:  # Test with first 10 operations
            try:
                found_ops = [op for op in all_operations if op.get('operationId') == op_id]
                if found_ops:
                    # Simulate dependency calculation
                    self._simulate_dependency_calculation(found_ops)
            except:
                pass
        minification_time = (time.perf_counter() - start_time) * 1000
        
        # Estimate memory usage (rough calculation)
        memory_estimate = (spec_size / (1024 * 1024)) * 1.5  # Rough multiplier for processing overhead
        
        # Calculate throughput
        operations_per_second = len(all_operations) / (parse_time / 1000) if parse_time > 0 else 0
        schemas = spec.get('components', {}).get('schemas', {})
        schemas_per_second = len(schemas) / (dependency_time / 1000) if dependency_time > 0 else 0
        
        benchmark = PerformanceBenchmark(
            spec_size_bytes=spec_size,
            load_time_ms=load_time,
            parse_time_ms=parse_time,
            dependency_resolution_time_ms=dependency_time,
            minification_time_ms=minification_time,
            memory_usage_mb=memory_estimate,
            operations_per_second=operations_per_second,
            schemas_per_second=schemas_per_second
        )
        
        self.benchmark_history.append(benchmark)
        return benchmark
    
    def compare_api_versions(self, old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two API versions and identify changes."""
        
        print("🔄 Comparing API versions...")
        
        # Compare operations
        old_ops = set(self._extract_operation_signatures(old_spec))
        new_ops = set(self._extract_operation_signatures(new_spec))
        
        added_ops = new_ops - old_ops
        removed_ops = old_ops - new_ops
        common_ops = old_ops & new_ops
        
        # Compare schemas
        old_schemas = set(old_spec.get('components', {}).get('schemas', {}).keys())
        new_schemas = set(new_spec.get('components', {}).get('schemas', {}).keys())
        
        added_schemas = new_schemas - old_schemas
        removed_schemas = old_schemas - new_schemas
        common_schemas = old_schemas & new_schemas
        
        # Analyze complexity changes
        old_complexity = self.analyze_api_complexity(old_spec)
        new_complexity = self.analyze_api_complexity(new_spec)
        
        complexity_delta = new_complexity.overall_complexity_score - old_complexity.overall_complexity_score
        
        return {
            'operations': {
                'added': list(added_ops),
                'removed': list(removed_ops),
                'unchanged': len(common_ops),
                'total_old': len(old_ops),
                'total_new': len(new_ops)
            },
            'schemas': {
                'added': list(added_schemas),
                'removed': list(removed_schemas),
                'unchanged': len(common_schemas),
                'total_old': len(old_schemas),
                'total_new': len(new_schemas)
            },
            'complexity': {
                'old_score': old_complexity.overall_complexity_score,
                'new_score': new_complexity.overall_complexity_score,
                'delta': complexity_delta,
                'trend': 'increased' if complexity_delta > 0.1 else 'decreased' if complexity_delta < -0.1 else 'stable'
            },
            'summary': {
                'breaking_changes': len(removed_ops) + len(removed_schemas),
                'new_features': len(added_ops) + len(added_schemas),
                'stability_score': len(common_ops) / max(len(old_ops), 1)
            }
        }
    
    def generate_api_health_report(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive API health and quality report."""
        
        print("📋 Generating API health report...")
        
        complexity_metrics = self.analyze_api_complexity(spec)
        recommendations = self.generate_intelligent_recommendations(spec, complexity_metrics)
        benchmark = self.benchmark_performance(spec, list(spec.get('paths', {}).keys())[:5])
        
        # Calculate health scores
        health_scores = {
            'complexity_health': max(0, 100 - (complexity_metrics.overall_complexity_score * 100)),
            'performance_health': min(100, max(0, 100 - (benchmark.load_time_ms / 10))),
            'dependency_health': max(0, 100 - (complexity_metrics.circular_dependencies * 20)),
            'optimization_health': max(0, 100 - complexity_metrics.optimization_potential),
            'maintainability_health': max(0, 100 - (len(complexity_metrics.unused_schemas) / max(complexity_metrics.total_schemas, 1) * 100))
        }
        
        overall_health = statistics.mean(health_scores.values())
        
        # Generate improvement roadmap
        roadmap = self._generate_improvement_roadmap(recommendations)
        
        return {
            'overall_health_score': round(overall_health, 1),
            'health_breakdown': {k: round(v, 1) for k, v in health_scores.items()},
            'complexity_analysis': asdict(complexity_metrics),
            'performance_benchmark': asdict(benchmark),
            'recommendations': [asdict(rec) for rec in recommendations],
            'improvement_roadmap': roadmap,
            'api_statistics': {
                'total_endpoints': complexity_metrics.total_operations,
                'total_schemas': complexity_metrics.total_schemas,
                'dependency_ratio': complexity_metrics.total_dependencies / max(complexity_metrics.total_schemas, 1),
                'optimization_potential_percentage': round(complexity_metrics.optimization_potential, 1)
            }
        }
    
    def _calculate_dependency_depths(self, spec: Dict[str, Any]) -> Dict[str, int]:
        """Calculate dependency depth for each schema."""
        depths = {}
        schemas = spec.get('components', {}).get('schemas', {})
        
        def calculate_depth(schema_name: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()
            
            if schema_name in visited:
                return 0  # Circular dependency
            
            if schema_name in depths:
                return depths[schema_name]
            
            visited.add(schema_name)
            schema = schemas.get(schema_name)
            if not schema:
                return 0
            
            refs = self.dependency_analyzer._extract_schema_dependencies(schema)
            if not refs:
                depths[schema_name] = 1
                return 1
            
            max_child_depth = 0
            for ref in refs:
                if ref.startswith('#/components/schemas/'):
                    child_name = ref.split('/')[-1]
                    child_depth = calculate_depth(child_name, visited.copy())
                    max_child_depth = max(max_child_depth, child_depth)
            
            depths[schema_name] = max_child_depth + 1
            return depths[schema_name]
        
        for schema_name in schemas.keys():
            calculate_depth(schema_name)
        
        return depths
    
    def _calculate_schema_complexity(self, schemas: Dict[str, Any]) -> float:
        """Calculate overall schema complexity score (0-1)."""
        if not schemas:
            return 0.0
        
        total_complexity = 0
        for schema in schemas.values():
            schema_complexity = 0
            
            # Property count complexity
            if 'properties' in schema:
                schema_complexity += min(len(schema['properties']) / 20, 1) * 0.3
            
            # Composition complexity (allOf, oneOf, anyOf)
            for comp_type in ['allOf', 'oneOf', 'anyOf']:
                if comp_type in schema:
                    schema_complexity += min(len(schema[comp_type]) / 5, 1) * 0.2
            
            # Nesting complexity
            schema_complexity += self._calculate_nesting_depth(schema) / 10 * 0.3
            
            # Required fields ratio
            if 'required' in schema and 'properties' in schema:
                required_ratio = len(schema['required']) / len(schema['properties'])
                schema_complexity += required_ratio * 0.2
            
            total_complexity += min(schema_complexity, 1.0)
        
        return total_complexity / len(schemas)
    
    def _calculate_operation_complexity(self, operations: Dict[str, Any]) -> float:
        """Calculate overall operation complexity score (0-1)."""
        if not operations:
            return 0.0
        
        total_complexity = 0
        operation_count = 0
        
        for path_item in operations.values():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    operation_count += 1
                    op_complexity = 0
                    
                    # Parameter complexity
                    params = operation.get('parameters', [])
                    op_complexity += min(len(params) / 10, 1) * 0.3
                    
                    # Response complexity
                    responses = operation.get('responses', {})
                    op_complexity += min(len(responses) / 5, 1) * 0.2
                    
                    # Request body complexity
                    if 'requestBody' in operation:
                        content = operation['requestBody'].get('content', {})
                        op_complexity += min(len(content) / 3, 1) * 0.3
                    
                    # Security requirements
                    security = operation.get('security', [])
                    op_complexity += min(len(security) / 3, 1) * 0.2
                    
                    total_complexity += min(op_complexity, 1.0)
        
        return total_complexity / max(operation_count, 1)
    
    def _calculate_optimization_potential(self, spec: Dict[str, Any]) -> float:
        """Calculate optimization potential percentage."""
        schemas = spec.get('components', {}).get('schemas', {})
        if not schemas:
            return 0.0
        
        optimization_factors = []
        
        # Unused schema factor
        unused_count = len(self._find_unused_schemas(spec))
        optimization_factors.append(unused_count / len(schemas) * 100)
        
        # Large schema factor
        oversized_count = len(self._find_oversized_schemas(schemas))
        optimization_factors.append(oversized_count / len(schemas) * 50)
        
        # Description/example factor (estimate)
        schemas_with_descriptions = sum(1 for s in schemas.values() if 'description' in s)
        optimization_factors.append(schemas_with_descriptions / len(schemas) * 20)
        
        return min(statistics.mean(optimization_factors), 100.0)
    
    def _identify_hotspot_operations(self, spec: Dict[str, Any]) -> List[str]:
        """Identify operations with high complexity."""
        hotspots = []
        operations = spec.get('paths', {})
        
        for path, path_item in operations.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    complexity_score = 0
                    
                    # Count parameters
                    params = operation.get('parameters', [])
                    complexity_score += len(params) * 2
                    
                    # Count response schemas
                    responses = operation.get('responses', {})
                    for response in responses.values():
                        content = response.get('content', {})
                        complexity_score += len(content) * 3
                    
                    # Request body schemas
                    if 'requestBody' in operation:
                        content = operation['requestBody'].get('content', {})
                        complexity_score += len(content) * 3
                    
                    if complexity_score > 15:  # Threshold for "hot" operations
                        op_id = operation.get('operationId', f"{method.upper()} {path}")
                        hotspots.append(op_id)
        
        return sorted(hotspots, key=lambda x: x)[:10]  # Top 10 hotspots
    
    def _find_unused_schemas(self, spec: Dict[str, Any]) -> List[str]:
        """Find schemas that are not referenced by any operation."""
        all_schemas = set(spec.get('components', {}).get('schemas', {}).keys())
        used_schemas = set()
        
        # Check all operations for schema references
        operations = spec.get('paths', {})
        for path_item in operations.values():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    # Check parameters
                    for param in operation.get('parameters', []):
                        if 'schema' in param:
                            refs = self.parser.get_schema_references(param['schema'])
                            for ref in refs:
                                if ref.startswith('#/components/schemas/'):
                                    used_schemas.add(ref.split('/')[-1])
                    
                    # Check request body
                    if 'requestBody' in operation:
                        content = operation['requestBody'].get('content', {})
                        for media_type in content.values():
                            if 'schema' in media_type:
                                refs = self.parser.get_schema_references(media_type['schema'])
                                for ref in refs:
                                    if ref.startswith('#/components/schemas/'):
                                        used_schemas.add(ref.split('/')[-1])
                    
                    # Check responses
                    for response in operation.get('responses', {}).values():
                        content = response.get('content', {})
                        for media_type in content.values():
                            if 'schema' in media_type:
                                refs = self.parser.get_schema_references(media_type['schema'])
                                for ref in refs:
                                    if ref.startswith('#/components/schemas/'):
                                        used_schemas.add(ref.split('/')[-1])
        
        return list(all_schemas - used_schemas)
    
    def _find_oversized_schemas(self, schemas: Dict[str, Any]) -> List[str]:
        """Find schemas that are unusually large."""
        oversized = []
        
        for name, schema in schemas.items():
            size_indicators = 0
            
            # Many properties
            if 'properties' in schema and len(schema['properties']) > 25:
                size_indicators += 1
            
            # Deep nesting
            if self._calculate_nesting_depth(schema) > 5:
                size_indicators += 1
            
            # Large serialized size
            schema_json = json.dumps(schema, separators=(',', ':'))
            if len(schema_json) > 2000:  # 2KB threshold
                size_indicators += 1
            
            if size_indicators >= 2:
                oversized.append(name)
        
        return oversized
    
    def _calculate_nesting_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of an object."""
        if not isinstance(obj, dict):
            return current_depth
        
        max_depth = current_depth
        for value in obj.values():
            if isinstance(value, dict):
                max_depth = max(max_depth, self._calculate_nesting_depth(value, current_depth + 1))
            elif isinstance(value, list):
                for item in value:
                    max_depth = max(max_depth, self._calculate_nesting_depth(item, current_depth + 1))
        
        return max_depth
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score."""
        return {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(priority, 0)
    
    def _generate_improvement_roadmap(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, List[str]]:
        """Generate a phased improvement roadmap."""
        roadmap = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        for rec in recommendations:
            if rec.priority == 'critical':
                roadmap['immediate'].append(f"{rec.issue}: {rec.recommendation}")
            elif rec.priority == 'high':
                roadmap['short_term'].append(f"{rec.issue}: {rec.recommendation}")
            else:
                roadmap['long_term'].append(f"{rec.issue}: {rec.recommendation}")
        
        return roadmap
    
    def _extract_operation_signatures(self, spec: Dict[str, Any]) -> List[str]:
        """Extract operation signatures for comparison."""
        signatures = []
        operations = spec.get('paths', {})
        
        for path, path_item in operations.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    op_id = operation.get('operationId', f"{method.upper()}_{path}")
                    signatures.append(f"{method.upper()} {path} ({op_id})")
        
        return signatures
    
    def _simulate_dependency_calculation(self, operations: List[Dict[str, Any]]) -> None:
        """Simulate dependency calculation for benchmarking."""
        for operation in operations:
            # Simulate extracting schema references
            op_details = operation.get('operation', {})
            
            # Simulate request body processing
            if 'requestBody' in op_details:
                content = op_details['requestBody'].get('content', {})
                for media_type in content.values():
                    if 'schema' in media_type:
                        self.parser.get_schema_references(media_type['schema'])
            
            # Simulate response processing
            for response in op_details.get('responses', {}).values():
                content = response.get('content', {})
                for media_type in content.values():
                    if 'schema' in media_type:
                        self.parser.get_schema_references(media_type['schema'])