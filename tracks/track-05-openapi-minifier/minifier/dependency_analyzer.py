"""
Advanced Dependency Analyzer Module
Handles complex dependency resolution using graph analysis.
"""

import networkx as nx
from typing import Dict, Any, List, Set, Optional, Tuple
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class DependencyGraph:
    """Manages schema dependency relationships using NetworkX."""
    
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for dependencies
        self.schema_cache = {}  # Cache resolved schemas
        
    def add_schema_dependency(self, from_schema: str, to_schema: str):
        """Add a dependency relationship between schemas."""
        self.graph.add_edge(from_schema, to_schema)
        
    def get_all_dependencies(self, schema_ref: str) -> Set[str]:
        """Get all dependencies (transitive) for a schema."""
        if schema_ref not in self.graph:
            return set()
        
        # Use networkx to find all nodes reachable from this schema
        reachable = nx.descendants(self.graph, schema_ref)
        reachable.add(schema_ref)  # Include the schema itself
        return reachable
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the schema graph."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXError:
            return []
    
    def get_dependency_order(self, schemas: Set[str]) -> List[str]:
        """Get schemas in dependency order (dependencies first)."""
        if not schemas:
            return []
        
        # Create subgraph with only the schemas we care about
        subgraph = self.graph.subgraph(schemas)
        
        try:
            # Topological sort gives us dependency order
            return list(nx.topological_sort(subgraph))
        except nx.NetworkXError:
            # If there are cycles, return as-is with warning
            logger.warning("Circular dependencies detected, returning unordered")
            return list(schemas)
    
    def analyze_schema_relationships(self) -> Dict[str, Any]:
        """Analyze the dependency graph for insights."""
        return {
            'total_schemas': self.graph.number_of_nodes(),
            'total_dependencies': self.graph.number_of_edges(),
            'circular_dependencies': len(self.detect_circular_dependencies()),
            'isolated_schemas': len(list(nx.isolates(self.graph))),
            'strongly_connected_components': len(list(nx.strongly_connected_components(self.graph)))
        }


class AdvancedDependencyAnalyzer:
    """Advanced dependency analyzer with graph-based resolution."""
    
    def __init__(self, parser):
        self.parser = parser
        self.dependency_graph = DependencyGraph()
        self.optimization_config = {
            'remove_descriptions': False,
            'remove_examples': False,
            'strip_unused_properties': True,
            'optimize_allof_oneof': True,
            'preserve_required_fields': True
        }
    
    def build_complete_dependency_graph(self, spec: Dict[str, Any]) -> DependencyGraph:
        """Build a complete dependency graph for all schemas in the spec."""
        schemas = spec.get('components', {}).get('schemas', {})
        
        # Clear and rebuild the graph
        self.dependency_graph = DependencyGraph()
        
        # Add all schemas as nodes first
        for schema_name in schemas.keys():
            schema_ref = f"#/components/schemas/{schema_name}"
            self.dependency_graph.graph.add_node(schema_ref)
        
        # Now add all dependencies
        for schema_name, schema_def in schemas.items():
            schema_ref = f"#/components/schemas/{schema_name}"
            dependencies = self._extract_schema_dependencies(schema_def)
            
            for dep_ref in dependencies:
                self.dependency_graph.add_schema_dependency(schema_ref, dep_ref)
        
        return self.dependency_graph
    
    def _extract_schema_dependencies(self, schema: Dict[str, Any]) -> Set[str]:
        """Extract all schema references from a schema definition."""
        dependencies = set()
        
        def find_refs(obj):
            if isinstance(obj, dict):
                # Direct $ref
                if '$ref' in obj:
                    ref = obj['$ref']
                    if ref.startswith('#/components/schemas/'):
                        dependencies.add(ref)
                
                # Handle allOf, oneOf, anyOf
                for key in ['allOf', 'oneOf', 'anyOf']:
                    if key in obj:
                        for item in obj[key]:
                            find_refs(item)
                
                # Handle properties
                if 'properties' in obj:
                    for prop_schema in obj['properties'].values():
                        find_refs(prop_schema)
                
                # Handle array items
                if 'items' in obj:
                    find_refs(obj['items'])
                
                # Handle additionalProperties
                if 'additionalProperties' in obj and isinstance(obj['additionalProperties'], dict):
                    find_refs(obj['additionalProperties'])
                
                # Recursively check all other values
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        find_refs(value)
            
            elif isinstance(obj, list):
                for item in obj:
                    find_refs(item)
        
        find_refs(schema)
        return dependencies
    
    def resolve_dependencies_with_graph(self, operation_schemas: Set[str]) -> Tuple[Set[str], Dict[str, Any]]:
        """
        Resolve dependencies using the dependency graph.
        Returns (all_dependencies, analysis_info)
        """
        all_dependencies = set()
        analysis = {
            'direct_dependencies': len(operation_schemas),
            'circular_refs': [],
            'dependency_chains': {},
            'optimization_opportunities': []
        }
        
        # Get all transitive dependencies
        for schema_ref in operation_schemas:
            deps = self.dependency_graph.get_all_dependencies(schema_ref)
            all_dependencies.update(deps)
            
            # Track dependency chains for analysis
            analysis['dependency_chains'][schema_ref] = list(deps - {schema_ref})
        
        # Check for circular dependencies
        analysis['circular_refs'] = self.dependency_graph.detect_circular_dependencies()
        
        # Identify optimization opportunities
        analysis['optimization_opportunities'] = self._identify_optimization_opportunities(all_dependencies)
        
        analysis['total_dependencies'] = len(all_dependencies)
        
        return all_dependencies, analysis
    
    def _identify_optimization_opportunities(self, schema_refs: Set[str]) -> List[Dict[str, Any]]:
        """Identify schemas that could be optimized."""
        opportunities = []
        
        for schema_ref in schema_refs:
            schema = self.parser.resolve_schema_reference(schema_ref)
            if not schema:
                continue
            
            schema_name = schema_ref.split('/')[-1]
            
            # Check for large schemas with many properties
            if 'properties' in schema and len(schema['properties']) > 20:
                opportunities.append({
                    'type': 'large_schema',
                    'schema': schema_name,
                    'property_count': len(schema['properties']),
                    'suggestion': 'Consider breaking into smaller schemas'
                })
            
            # Check for schemas with complex allOf/oneOf/anyOf
            for key in ['allOf', 'oneOf', 'anyOf']:
                if key in schema and len(schema[key]) > 5:
                    opportunities.append({
                        'type': 'complex_composition',
                        'schema': schema_name,
                        'composition_type': key,
                        'branch_count': len(schema[key]),
                        'suggestion': f'Complex {key} with {len(schema[key])} branches'
                    })
            
            # Check for schemas with many examples
            if 'examples' in schema and len(schema['examples']) > 3:
                opportunities.append({
                    'type': 'excessive_examples',
                    'schema': schema_name,
                    'example_count': len(schema['examples']),
                    'suggestion': 'Consider reducing examples for smaller spec'
                })
        
        return opportunities
    
    def optimize_schema_definitions(self, schemas: Dict[str, Any], used_properties: Dict[str, Set[str]] = None) -> Dict[str, Any]:
        """
        Optimize schema definitions by removing unused elements.
        
        Args:
            schemas: Dictionary of schema definitions
            used_properties: Optional dict mapping schema names to sets of used properties
        """
        optimized_schemas = {}
        
        for schema_name, schema_def in schemas.items():
            optimized_schema = self._optimize_single_schema(
                schema_def, 
                schema_name,
                used_properties.get(schema_name) if used_properties else None
            )
            optimized_schemas[schema_name] = optimized_schema
        
        return optimized_schemas
    
    def _optimize_single_schema(self, schema: Dict[str, Any], schema_name: str, used_properties: Set[str] = None) -> Dict[str, Any]:
        """Optimize a single schema definition."""
        optimized = deepcopy(schema)
        
        # Remove descriptions if configured
        if self.optimization_config['remove_descriptions']:
            optimized.pop('description', None)
            if 'properties' in optimized:
                for prop in optimized['properties'].values():
                    if isinstance(prop, dict):
                        prop.pop('description', None)
        
        # Remove examples if configured
        if self.optimization_config['remove_examples']:
            optimized.pop('example', None)
            optimized.pop('examples', None)
            if 'properties' in optimized:
                for prop in optimized['properties'].values():
                    if isinstance(prop, dict):
                        prop.pop('example', None)
                        prop.pop('examples', None)
        
        # Strip unused properties if we know which are used
        if (self.optimization_config['strip_unused_properties'] and 
            used_properties is not None and 
            'properties' in optimized):
            
            # Keep only used properties, but preserve required fields
            required_fields = set(optimized.get('required', []))
            properties_to_keep = used_properties | required_fields
            
            if properties_to_keep:
                optimized['properties'] = {
                    prop: optimized['properties'][prop] 
                    for prop in optimized['properties'] 
                    if prop in properties_to_keep
                }
        
        # Optimize allOf/oneOf/anyOf constructs
        if self.optimization_config['optimize_allof_oneof']:
            optimized = self._optimize_composition_schemas(optimized)
        
        return optimized
    
    def _optimize_composition_schemas(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize allOf/oneOf/anyOf constructs."""
        # This is a simplified optimization - in practice, this would be more complex
        
        # If allOf has only one item, we can potentially flatten it
        if 'allOf' in schema and len(schema['allOf']) == 1:
            single_item = schema['allOf'][0]
            if isinstance(single_item, dict) and '$ref' not in single_item:
                # Merge the single allOf item into the parent schema
                merged = deepcopy(schema)
                merged.pop('allOf')
                
                # Merge properties if both have them
                if 'properties' in merged and 'properties' in single_item:
                    merged['properties'].update(single_item['properties'])
                elif 'properties' in single_item:
                    merged['properties'] = single_item['properties']
                
                # Merge other fields as well
                for key, value in single_item.items():
                    if key not in merged:
                        merged[key] = value
                
                return merged
        
        return schema
    
    def set_optimization_config(self, config: Dict[str, bool]):
        """Update optimization configuration."""
        self.optimization_config.update(config)